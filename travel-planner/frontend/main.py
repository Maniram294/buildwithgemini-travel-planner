"""Minimal FastAPI proxy for a deployed A2A agent (Agent Runtime, agents-cli 1.1.0+).

The browser talks ONLY to this proxy (same origin, no CORS, no GCP creds in the
browser). The proxy authenticates with Application Default Credentials and
forwards chat to the deployed agent over the A2A protocol, returning replies as
structured parts the chat UI knows how to show:

  * {"kind": "text", "text": ...}  -> a normal chat bubble
  * {"kind": "a2ui", "data": ...}  -> one A2UI message (beginRendering /
    surfaceUpdate); static/index.html renders these as a card.

Why A2A: agents-cli 1.1.0 (GA) deploys ADK agents to Agent Runtime as A2A agents
and no longer registers the reasoning-engine operation schema the old
`agent_engines.get(...).stream_query()` path relied on (operation_schemas() comes
back empty). The container serves the A2A protocol over the Agent Engine HTTP
passthrough, so this proxy fetches the agent's card and sends messages with the
a2a-sdk client (the same path `agents-cli run --mode a2a` uses). This works for
both A2A and plain ADK 1.1.0 deployments (the container serves A2A either way).

Run:
  pip install -r requirements.txt
  export AGENT_ENGINE_RESOURCE_NAME="projects/.../locations/.../reasoningEngines/..."
  export AGENT_DIRECTORY="app"   # your agent's app directory (agents-cli-manifest.yaml)
  python main.py                 # -> http://localhost:8080
"""

import os
import uuid

import google.auth
import google.auth.transport.requests
import httpx
from a2a.client import ClientConfig, ClientFactory
from a2a.types import (
    AgentCard,
    FilePart,
    Message,
    Part,
    Role,
    TaskArtifactUpdateEvent,
    TextPart,
    TransportProtocol,
)
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

def _resolve_resource_name() -> str:
    if res := os.environ.get("AGENT_ENGINE_RESOURCE_NAME"):
        return res
    meta_path = os.path.join(os.path.dirname(__file__), "..", "deployment_metadata.json")
    if os.path.exists(meta_path):
        import json
        with open(meta_path) as f:
            data = json.load(f)
            if "remote_agent_runtime_id" in data:
                return data["remote_agent_runtime_id"]
    raise KeyError("AGENT_ENGINE_RESOURCE_NAME environment variable not set")

RESOURCE = _resolve_resource_name()
# The agent's app directory (matches agent_directory in agents-cli-manifest.yaml).
AGENT_DIRECTORY = os.environ.get("AGENT_DIRECTORY", "app")
# Location is embedded in the resource name: projects/<p>/locations/<loc>/reasoningEngines/<id>.
LOCATION = RESOURCE.split("/locations/")[1].split("/")[0]

# A2A endpoint for an Agent Runtime deployment, via the Agent Engine HTTP
# passthrough. The card lives at the well-known path under this base.
A2A_BASE = (
    f"https://{LOCATION}-aiplatform.googleapis.com/reasoningEngines/v1/"
    f"{RESOURCE}/api/a2a/{AGENT_DIRECTORY}"
)
A2A_CARD_URL = f"{A2A_BASE}/.well-known/agent-card.json"

# The agent tags its A2UI data parts with this mime type.
_A2UI_MIME = "application/json+a2ui"

# One set of ADC credentials, refreshed per request (access tokens expire ~1h).
_creds, _ = google.auth.default(
    scopes=["https://www.googleapis.com/auth/cloud-platform"]
)


def _auth_headers() -> dict[str, str]:
    _creds.refresh(google.auth.transport.requests.Request())
    return {
        "Authorization": f"Bearer {_creds.token}",
        "Content-Type": "application/json",
    }


app = FastAPI()


@app.exception_handler(Exception)
async def _json_errors(request: Request, exc: Exception):
    # Always return JSON so the browser never receives a plain-text 500 page
    # (which shows up in the chat as "Unexpected token 'I', "Internal S"... is
    # not valid JSON"). Any server-side failure now surfaces as a readable
    # message in the chat bubble instead.
    return JSONResponse(
        status_code=200,
        content={
            "parts": [{"kind": "text", "text": f"Error: {type(exc).__name__}: {exc}"}]
        },
    )


# Reuse ONE A2A context per user so the agent remembers the conversation.
_contexts: dict[str, str] = {}
# Cache the agent card after the first fetch.
_card: AgentCard | None = None


async def _get_card(client: httpx.AsyncClient) -> AgentCard:
    global _card
    if _card is None:
        resp = await client.get(A2A_CARD_URL)
        resp.raise_for_status()
        card = AgentCard(**resp.json())
        # Agent Runtime does not serve a public card URL, so point the client at
        # the passthrough base for message sends.
        card.url = A2A_BASE
        _card = card
    return _card


def _extract_parts(parts: list) -> list[dict]:
    """Turn A2A response parts into structured parts for the chat UI.

    Text parts pass through as {"kind": "text"}. A2UI data parts (tagged
    application/json+a2ui) become {"kind": "a2ui", "data": <message>} so the UI
    renders the card; each data part is one A2UI message (beginRendering or
    surfaceUpdate).
    """
    out: list[dict] = []
    for p in parts:
        root = getattr(p, "root", p)
        if isinstance(root, TextPart) and getattr(root, "text", None):
            out.append({"kind": "text", "text": root.text})
        elif getattr(root, "data", None) is not None:
            data_val = root.data
            meta = getattr(root, "metadata", None) or {}
            # Sometimes data_val is wrapped in an inner dict: {'kind': 'data', 'data': {...}, 'metadata': {...}}
            if isinstance(data_val, dict) and "data" in data_val and "metadata" in data_val:
                inner_meta = data_val.get("metadata") or {}
                mime = inner_meta.get("mimeType") if isinstance(inner_meta, dict) else None
                inner_data = data_val.get("data")
                if mime == _A2UI_MIME and inner_data is not None:
                    out.append({"kind": "a2ui", "data": inner_data})
                    continue
            mime = meta.get("mimeType") if isinstance(meta, dict) else None
            if mime == _A2UI_MIME:
                out.append({"kind": "a2ui", "data": data_val})
        elif isinstance(root, FilePart):
            uri = getattr(getattr(root, "file", None), "uri", None)
            if uri:
                out.append({"kind": "text", "text": uri})
    return out


import importlib.util

def _load_app_module(name: str, rel_path: str):
    file_path = os.path.join(os.path.dirname(__file__), "..", rel_path)
    spec = importlib.util.spec_from_file_location(name, file_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

try:
    _culinary_mod = _load_app_module("culinary_data", "app/culinary_data.py")
    _events_mod = _load_app_module("events_data", "app/events_data.py")
    _passport_mod = _load_app_module("food_passport", "app/food_passport.py")
    _food_passport_mgr = _passport_mod.food_passport
except Exception as e:
    _culinary_mod = None
    _events_mod = None
    _food_passport_mgr = None

@app.get("/api/food/specialties")
async def get_food_specialties(destination: str = "italy"):
    if not _culinary_mod:
        return JSONResponse({"error": "Culinary module unavailable"}, status_code=500)
    dest_key = destination.lower().strip()
    data = None
    for k, v in _culinary_mod.REGIONAL_SPECIALTIES.items():
        if k in dest_key or dest_key in k:
            data = v
            break
    if not data:
        data = _culinary_mod.REGIONAL_SPECIALTIES.get("italy") or _culinary_mod.REGIONAL_SPECIALTIES.get("kyoto")
    return JSONResponse(data or {})

@app.get("/api/events")
async def get_events(destination: str = "Italy", start_date: str = None, end_date: str = None):
    if not _events_mod:
        return JSONResponse({"events": []})
    events = _events_mod.find_seasonal_events(destination, start_date or "2026-01-01", end_date or "2026-12-31")
    return JSONResponse(events)

@app.get("/api/passport")
async def list_passport(user_id: str = "web-user", destination: str = None):
    if not _food_passport_mgr:
        return JSONResponse([])
    items = _food_passport_mgr.list_passport_dishes(user_id=user_id, destination=destination)
    return JSONResponse(items)

@app.post("/api/passport")
async def add_passport(req: Request):
    if not _food_passport_mgr:
        return JSONResponse({"error": "Passport manager unavailable"}, status_code=500)
    data = await req.json()
    res = _food_passport_mgr.add_or_update_dish(
        user_id=data.get("user_id", "web-user"),
        dish_name=data.get("dish_name", ""),
        destination=data.get("destination", "Kyoto"),
        status=data.get("status", "want_to_try"),
        rating=data.get("rating"),
        notes=data.get("notes"),
        venue_name=data.get("venue_name"),
    )
    return JSONResponse(res)

@app.delete("/api/passport")
async def delete_passport(req: Request):
    if not _food_passport_mgr:
        return JSONResponse({"error": "Passport manager unavailable"}, status_code=500)
    data = await req.json()
    res = _food_passport_mgr.remove_dish(
        user_id=data.get("user_id", "web-user"),
        dish_name=data.get("dish_name", ""),
        destination=data.get("destination", "Kyoto"),
    )
    return JSONResponse(res)

@app.post("/chat")
async def chat(req: Request):
    body = await req.json()
    message = body.get("message", "")
    user_id = body.get("user_id") or "web-user"
    parts: list[dict] = []

    async with httpx.AsyncClient(headers=_auth_headers(), timeout=120) as client:
        card = await _get_card(client)
        factory = ClientFactory(
            ClientConfig(
                supported_transports=[
                    TransportProtocol.jsonrpc,
                    TransportProtocol.http_json,
                ],
                httpx_client=client,
            )
        )
        a2a_client = factory.create(card)

        msg = Message(
            message_id=str(uuid.uuid4()),
            role=Role.user,
            parts=[Part(root=TextPart(text=message))],
            context_id=_contexts.get(user_id),
        )

        last_task = None
        got_artifact_update = False
        async for event in a2a_client.send_message(msg):
            if not isinstance(event, tuple):
                continue
            task, update = event
            if task is not None:
                last_task = task
                if getattr(task, "context_id", None):
                    _contexts[user_id] = task.context_id
            if isinstance(update, TaskArtifactUpdateEvent):
                got_artifact_update = True
                parts.extend(_extract_parts(update.artifact.parts))

        # Non-streaming fallback: pull parts from the final task's artifacts.
        if not got_artifact_update and last_task is not None:
            for artifact in getattr(last_task, "artifacts", None) or []:
                parts.extend(_extract_parts(artifact.parts))

    if not parts:
        # The turn produced no text or UI (e.g. the agent only ran tools, or a
        # tool stalled). Be honest rather than silent.
        parts = [{"kind": "text", "text": "(The agent didn't return a reply.)"}]
    return JSONResponse({"parts": parts})


# Serve the chat UI (keep this mount last so /chat wins).
app.mount("/", StaticFiles(directory="static", html=True), name="static")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
