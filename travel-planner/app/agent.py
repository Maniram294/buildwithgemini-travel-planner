# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import base64
import datetime
import json
import os
from typing import Any, Dict, List, Optional
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

load_dotenv()

from a2ui.schema.manager import A2uiSchemaManager
from a2ui.basic_catalog.provider import BasicCatalog
from .a2ui_utils import a2ui_callback
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.adk.models import Gemini
from google.adk.tools import ToolContext
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.cloud import firestore
from google.cloud import storage
from google import genai
from google.genai import types

MODEL = "gemini-3.8-flash"
IMAGE_MODEL = "gemini-3.1-flash-lite-image"
VIDEO_MODEL = "gemini-omni-flash-preview"
FIRESTORE_PROJECT_ID = "qwiklabs-gcp-03-fe98c55ba1b5"
BUCKET_NAME = "travel-planner-media-7dx9bu"
AGENT_ENGINE_ID = "460472171177705472"
MEMORY_BANK_ID = "460472171177705472"
SANDBOX_RESOURCE_NAME = "projects/513515792631/locations/us-east1/reasoningEngines/460472171177705472/sandboxEnvironments/2933928031464456192"


def get_firestore_client() -> firestore.Client:
    """Return a Firestore client pinned to the hardcoded project ID."""
    return firestore.Client(project=FIRESTORE_PROJECT_ID)


def list_destinations(travel_style: Optional[str] = None) -> List[Dict[str, Any]]:
    """List curated travel destinations from the Firestore catalog.

    Args:
        travel_style: Optional filter by style (e.g., 'cultural', 'adventure', 'foodie').

    Returns:
        A list of destination dictionaries matching the query.
    """
    db = get_firestore_client()
    collection_ref = db.collection("destinations")

    if travel_style:
        query = collection_ref.where("travel_style", "==", travel_style.lower().strip())
        docs = query.stream()
    else:
        docs = collection_ref.stream()

    destinations = [doc.to_dict() for doc in docs]
    return destinations


def get_destination_details(destination_id: str) -> Dict[str, Any]:
    """Retrieve detailed information for a specific destination by its ID.

    Args:
        destination_id: The unique identifier of the destination (e.g., 'kyoto-japan', 'oaxaca-mexico').

    Returns:
        A dictionary containing the destination details or an error message if not found.
    """
    db = get_firestore_client()
    doc = db.collection("destinations").document(destination_id.lower().strip()).get()

    if not doc.exists:
        return {"error": f"Destination with ID '{destination_id}' was not found in the catalog."}

    return doc.to_dict()


def save_destination(
    destination_id: str,
    name: str,
    country: str,
    travel_style: str,
    budget_tier: str,
    highlights: List[str],
    best_season: str,
    estimated_daily_cost_usd: int,
    description: str,
) -> Dict[str, Any]:
    """Save or update a travel destination in the Firestore catalog.

    Args:
        destination_id: A URL-friendly identifier (e.g., 'tokyo-japan', 'paris-france').
        name: Name of the city/region (e.g., 'Tokyo').
        country: Country name (e.g., 'Japan').
        travel_style: Category such as 'adventure', 'cultural', 'foodie', or 'relaxation'.
        budget_tier: 'budget', 'moderate', or 'luxury'.
        highlights: A list of key attractions or activities.
        best_season: Ideal months or season to visit.
        estimated_daily_cost_usd: Approximate daily cost in USD per traveler.
        description: A short overview of the destination.

    Returns:
        Status dictionary confirming the save action.
    """
    db = get_firestore_client()
    data = {
        "id": destination_id.lower().strip(),
        "name": name,
        "country": country,
        "travel_style": travel_style.lower().strip(),
        "budget_tier": budget_tier.lower().strip(),
        "highlights": highlights,
        "best_season": best_season,
        "estimated_daily_cost_usd": estimated_daily_cost_usd,
        "description": description,
    }
    db.collection("destinations").document(destination_id.lower().strip()).set(data)
    return {"status": "success", "message": f"Destination '{name}' saved successfully with ID '{destination_id}'."}


def fetch_live_weather(location: str) -> Dict[str, Any]:
    """Fetch live real-time weather and forecast conditions for any city or destination.

    Args:
        location: City or destination name (e.g., 'Kyoto', 'Reykjavik', 'Paris').

    Returns:
        A dictionary with temperature in Fahrenheit, weather condition description, wind speed, and location coordinates.
    """
    try:
        # 1. Geocode location name to coordinates
        encoded_loc = urllib.parse.quote(location)
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={encoded_loc}&count=1&language=en&format=json"
        req = urllib.request.Request(geo_url, headers={"User-Agent": "TravelPlannerAgent/1.0"})
        with urllib.request.urlopen(req, timeout=5) as res:
            geo_data = json.loads(res.read().decode())

        if not geo_data.get("results"):
            return {"error": f"Could not find geographic coordinates for '{location}'."}

        place = geo_data["results"][0]
        lat, lon = place["latitude"], place["longitude"]
        resolved_name = f"{place.get('name')}, {place.get('country', '')}".strip(", ")

        # 2. Fetch current weather from Open-Meteo
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
            "&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m"
            "&temperature_unit=fahrenheit&wind_speed_unit=mph"
        )
        req_w = urllib.request.Request(weather_url, headers={"User-Agent": "TravelPlannerAgent/1.0"})
        with urllib.request.urlopen(req_w, timeout=5) as res_w:
            w_data = json.loads(res_w.read().decode())

        current = w_data.get("current", {})
        code = current.get("weather_code", 0)

        # Simple WMO weather code mapping
        weather_descriptions = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Foggy",
            51: "Light drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            71: "Slight snow",
            73: "Moderate snow",
            75: "Heavy snow",
            95: "Thunderstorm",
        }
        condition = weather_descriptions.get(code, "Clear to partly cloudy")

        return {
            "location": resolved_name,
            "temperature_f": current.get("temperature_2m"),
            "feels_like_f": current.get("apparent_temperature"),
            "condition": condition,
            "humidity_percent": current.get("relative_humidity_2m"),
            "wind_speed_mph": current.get("wind_speed_10m"),
        }
    except Exception as e:
        return {"error": f"Failed to fetch live weather for '{location}': {str(e)}"}


def convert_currency(amount: float, from_currency: str = "USD", to_currency: str = "EUR") -> Dict[str, Any]:
    """Convert travel budgets and costs between international currencies using live exchange rates.

    Args:
        amount: The monetary amount to convert.
        from_currency: 3-letter currency code to convert from (e.g., 'USD', 'EUR', 'GBP', 'JPY', 'MXN').
        to_currency: 3-letter currency code to convert to (e.g., 'JPY', 'EUR', 'MXN', 'NZD', 'USD').

    Returns:
        A dictionary with the original amount, converted amount, conversion rate, and timestamp.
    """
    base = from_currency.upper().strip()
    target = to_currency.upper().strip()
    try:
        url = f"https://open.er-api.com/v6/latest/{base}"
        req = urllib.request.Request(url, headers={"User-Agent": "TravelPlannerAgent/1.0"})
        with urllib.request.urlopen(req, timeout=5) as res:
            data = json.loads(res.read().decode())

        if data.get("result") != "success":
            return {"error": f"Unable to fetch exchange rates for base currency '{base}'."}

        rates = data.get("rates", {})
        if target not in rates:
            return {"error": f"Target currency '{target}' not supported or not found."}

        rate = rates[target]
        converted_amount = round(amount * rate, 2)

        return {
            "original_amount": amount,
            "from_currency": base,
            "converted_amount": converted_amount,
            "to_currency": target,
            "exchange_rate": rate,
            "last_updated": data.get("time_last_update_utc"),
        }
    except Exception as e:
        return {"error": f"Currency conversion failed: {str(e)}"}


def geocode_address(address: str) -> Dict[str, Any]:
    """Convert an address, landmark, or location string into geographic latitude and longitude coordinates.

    Args:
        address: The address, place name, or landmark to geocode (e.g. '1600 Amphitheatre Pkwy, Mountain View, CA' or 'Eiffel Tower, Paris').

    Returns:
        A dictionary with the formatted address, location coordinates (latitude, longitude), and place ID.
    """
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        return {"error": "GOOGLE_MAPS_API_KEY environment variable is not set."}

    try:
        encoded_address = urllib.parse.quote(address)
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={encoded_address}&key={api_key}"
        req = urllib.request.Request(url, headers={"User-Agent": "TravelPlannerAgent/1.0"})
        with urllib.request.urlopen(req, timeout=5) as res:
            data = json.loads(res.read().decode())

        if data.get("status") != "OK" or not data.get("results"):
            return {"error": f"Geocoding failed for '{address}'. Status: {data.get('status')}"}

        result = data["results"][0]
        loc = result["geometry"]["location"]
        return {
            "formatted_address": result.get("formatted_address"),
            "location": {"latitude": loc["lat"], "longitude": loc["lng"]},
            "place_id": result.get("place_id"),
        }
    except Exception as e:
        return {"error": f"Geocoding request failed: {str(e)}"}


def find_nearby_places(
    latitude: float,
    longitude: float,
    place_type: str = "tourist_attraction",
    radius_meters: float = 1500.0,
    max_results: int = 5,
) -> Dict[str, Any]:
    """Find nearby places of a given type around coordinates using the Google Places API (New).

    Args:
        latitude: Latitude of the center point.
        longitude: Longitude of the center point.
        place_type: Type of place to search for (e.g., 'tourist_attraction', 'restaurant', 'museum', 'hotel', 'cafe').
        radius_meters: Search radius in meters (default: 1500 meters).
        max_results: Maximum number of places to return (1-20, default: 5).

    Returns:
        A list of nearby places with name, formatted address, and location coordinates.
    """
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        return {"error": "GOOGLE_MAPS_API_KEY environment variable is not set."}

    try:
        url = "https://places.googleapis.com/v1/places:searchNearby"
        payload = {
            "includedTypes": [place_type.lower().strip()],
            "maxResultCount": min(max(1, max_results), 20),
            "locationRestriction": {
                "circle": {
                    "center": {"latitude": latitude, "longitude": longitude},
                    "radius": float(radius_meters),
                }
            },
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "X-Goog-Api-Key": api_key,
                "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location",
            },
        )
        with urllib.request.urlopen(req, timeout=5) as res:
            data = json.loads(res.read().decode())

        places = []
        for p in data.get("places", []):
            loc = p.get("location", {})
            places.append({
                "name": p.get("displayName", {}).get("text"),
                "address": p.get("formattedAddress"),
                "location": {"latitude": loc.get("latitude"), "longitude": loc.get("longitude")},
            })

        return {"places": places, "count": len(places)}
    except Exception as e:
        return {"error": f"Nearby places search failed: {str(e)}"}


def generate_destination_image(
    prompt: str,
    tool_context: ToolContext,
    destination_name: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate a scenic travel photograph or postcard for a destination, save it as an artifact, and upload it to Cloud Storage.

    Args:
        prompt: Description of the scene, destination, or landmark to generate (e.g. 'A tranquil sunset view of Kyoto bamboo forest').
        tool_context: Tool execution context injected by the ADK runtime.
        destination_name: Optional name of the destination for clean file naming.

    Returns:
        A dictionary containing the public Cloud Storage URL of the image, the artifact filename, and status.
    """
    try:
        # 1. Initialize Vertex AI GenAI Client in the global region
        client = genai.Client(
            vertexai=True,
            project=FIRESTORE_PROJECT_ID,
            location="global",
        )

        # 2. Generate the image using gemini-3.1-flash-lite-image
        response = client.models.generate_content(
            model=IMAGE_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(response_modalities=["IMAGE"]),
        )

        image_bytes = None
        mime_type = "image/jpeg"
        for candidate in response.candidates:
            if candidate.content and candidate.content.parts:
                for part in candidate.content.parts:
                    if part.inline_data and part.inline_data.data:
                        image_bytes = part.inline_data.data
                        if part.inline_data.mime_type:
                            mime_type = part.inline_data.mime_type
                        break
            if image_bytes:
                break

        if not image_bytes:
            return {"error": "No image data was generated by the model."}

        # 3. Clean up filename
        ext = "png" if "png" in mime_type else "jpg"
        prefix = destination_name.lower().replace(" ", "_") if destination_name else "postcard"
        filename = f"{prefix}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"

        # 4. Save to Playground Artifacts via tool_context
        artifact_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
        tool_context.save_artifact(filename=filename, artifact=artifact_part)

        # 5. Upload directly from bytes to public Cloud Storage bucket
        storage_client = storage.Client(project=FIRESTORE_PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(image_bytes, content_type=mime_type)

        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"

        return {
            "status": "success",
            "public_url": public_url,
            "artifact_filename": filename,
            "message": f"Image generated successfully and published to {public_url}",
        }
    except Exception as e:
        return {"error": f"Image generation or upload failed: {str(e)}"}


def generate_destination_video(
    prompt: str,
    tool_context: ToolContext,
    destination_name: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate a short cinematic travel video for a destination or attraction using Google's Omni model (gemini-omni-flash-preview).

    Saves the video as an artifact for the Playground's Artifacts panel and uploads the video bytes to the public Cloud Storage bucket.

    Args:
        prompt: Description of the scene or camera movement for the travel preview video (e.g. 'A scenic aerial drone shot flying over turquoise waves in Santorini at golden hour').
        tool_context: Tool execution context injected by the ADK runtime.
        destination_name: Optional name of the destination or landmark for clean file naming.

    Returns:
        A dictionary containing the public Cloud Storage URL (https://storage.googleapis.com/<bucket>/<object>), the artifact filename, and status.
    """
    try:
        # 1. Initialize Vertex AI GenAI Client in the global region
        client = genai.Client(
            vertexai=True,
            project=FIRESTORE_PROJECT_ID,
            location="global",
        )

        # 2. Generate video using the Omni model
        interaction = client.interactions.create(
            model=VIDEO_MODEL,
            input=prompt,
        )

        video_bytes = None
        mime_type = "video/mp4"

        # Check output_video attribute on the interaction
        if hasattr(interaction, "output_video") and interaction.output_video:
            out_vid = interaction.output_video
            if hasattr(out_vid, "data") and out_vid.data:
                raw_data = out_vid.data
                video_bytes = base64.b64decode(raw_data) if isinstance(raw_data, str) else raw_data
            if hasattr(out_vid, "mime_type") and out_vid.mime_type:
                mime_type = out_vid.mime_type

        # Fallback check across steps if output_video attribute wasn't populated directly
        if not video_bytes and hasattr(interaction, "steps"):
            for step in reversed(interaction.steps or []):
                content = getattr(step, "content", None) or []
                for item in content:
                    item_type = getattr(item, "type", None) or (item.get("type") if isinstance(item, dict) else None)
                    if item_type == "video":
                        data_val = getattr(item, "data", None) or (item.get("data") if isinstance(item, dict) else None)
                        if data_val:
                            video_bytes = base64.b64decode(data_val) if isinstance(data_val, str) else data_val
                            item_mime = getattr(item, "mime_type", None) or (item.get("mime_type") if isinstance(item, dict) else None)
                            if item_mime:
                                mime_type = item_mime
                            break
                if video_bytes:
                    break

        if not video_bytes:
            return {"error": "No video data was generated by the model."}

        # 3. Create filename
        prefix = destination_name.lower().replace(" ", "_") if destination_name else "video_preview"
        filename = f"{prefix}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"

        # 4. Save to Playground Artifacts via tool_context
        artifact_part = types.Part.from_bytes(data=video_bytes, mime_type=mime_type)
        tool_context.save_artifact(filename=filename, artifact=artifact_part)

        # 5. Upload directly from bytes to public Cloud Storage bucket
        storage_client = storage.Client(project=FIRESTORE_PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(video_bytes, content_type=mime_type)

        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"

        return {
            "status": "success",
            "public_url": public_url,
            "artifact_filename": filename,
            "message": f"Video generated successfully and published to {public_url}",
        }
    except Exception as e:
        return {"error": f"Video generation or upload failed: {str(e)}"}


# WRITE: after each turn, send the session to Memory Bank for extraction.
async def generate_memories_callback(callback_context: CallbackContext):
    await callback_context.add_session_to_memory()
    return None


code_executor = AgentEngineSandboxCodeExecutor(sandbox_resource_name=SANDBOX_RESOURCE_NAME)

a2ui_schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

instruction = a2ui_schema_manager.generate_system_prompt(
    role_description=(
        "You are an expert travel planner agent. You help travelers discover destinations, "
        "explore curated travel experiences from the catalog, and plan customized trips. "
        "Crucially, remember and track all user allergies (food allergies, ingredient sensitivities, medical or environmental allergies) "
        "and dietary restrictions across conversations. Never recommend places, dishes, or activities that conflict with their stated allergies. "
        "Also remember their travel preferences, home airport, past trips, and personal facts to personalize your recommendations. "
        "Use the Firestore destination tools to search, view details, or add new destinations, "
        "fetch_live_weather to check real-time weather and packing advice for any location, "
        "convert_currency to convert travel costs and budgets between currencies, "
        "geocode_address to find the coordinates of any place or landmark, "
        "find_nearby_places to discover nearby attractions, restaurants, museums, or hotels, "
        "generate_destination_image to generate scenic photos or postcards for any destination or landmark, "
        "and generate_destination_video to generate short cinematic video previews using the Omni model. "
        "You have an AgentEngineSandboxCodeExecutor code executor. Whenever you need to calculate math, "
        "analyze data, or run Python code in the sandbox, write executable Python code enclosed within "
        "```python ... ``` or ```tool_code ... ``` blocks. Your code will be automatically executed in the "
        "Agent Engine code execution sandbox and the execution output will be returned to you. After the code "
        "executes, synthesize and present the final answer clearly to the user."
    ),
    workflow_description="Analyze the user request, call appropriate tools if needed, and return structured UI when appropriate.",
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        "{\"Image\": {\"url\": {\"literalString\": \"https://...\"}}}. Never point an "
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
    ),
    include_schema=True,
    include_examples=True,
)

root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=instruction,
    code_executor=code_executor,
    after_agent_callback=generate_memories_callback,
    after_model_callback=a2ui_callback,
    tools=[
        PreloadMemoryTool(),
        list_destinations,
        get_destination_details,
        save_destination,
        fetch_live_weather,
        convert_currency,
        geocode_address,
        find_nearby_places,
        generate_destination_image,
        generate_destination_video,
    ],
)

app = App(
    root_agent=root_agent,
    name="app",
)
