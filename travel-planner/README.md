# ✈️ Travel Planner Agent

> An agent-first travel assistant that helps travelers discover destinations, explore curated catalogs, generate scenic travel media, and plan customized itineraries with persistent memory and rich A2UI cards.

![Travel Planner Demo](demo.gif)

---

## 🌟 What This Agent Does

The Travel Planner agent is built with Google's **Agent Development Kit (ADK)** and deployed to **Google Cloud Agent Platform (Agent Runtime)**. It operates as an **A2A (Agent-to-Agent)** compliant conversational agent with native tool execution, persistent cross-session memory, and dynamic UI rendering:

- **Curated Destination Catalog**: Searches and inspects curated travel destinations stored in Firestore, including top attractions, best travel seasons, highlights, and local tips.
- **Persistent Personal Memory**: Automatically remembers traveler preferences, home airport, travel style (adventure, luxury, budget), past trips, and **crucially tracks food allergies and dietary restrictions** across conversations so future recommendations never conflict with safety guidelines.
- **Live Weather & Packing Insights**: Queries real-time weather forecasts, current temperatures, wind speeds, and humidity via the Open-Meteo API to provide dynamic packing recommendations.
- **Live Currency Conversion**: Pulls live international exchange rates to convert travel costs, lodging expenses, and trip budgets between international currencies.
- **Geocoding & Places Discovery**: Converts landmark names to geographic coordinates and queries nearby points of interest, attractions, museums, and hotels via the Google Maps Places API.
- **Scenic Postcard Generation**: Generates high-resolution travel photos and postcards on-demand using Google's `gemini-3.1-flash-lite-image` model, saving them as local artifacts and uploading them directly to Google Cloud Storage.
- **Cinematic Video Previews**: Generates short travel preview videos using Google's Omni model (`gemini-omni-flash-preview`), saves them as artifacts, and uploads them to Google Cloud Storage.
- **Safe Code Execution Sandbox**: Executes custom Python calculations within Vertex AI's Agent Engine Sandbox environment for math, travel budget breakdowns, and data analysis.
- **Agent-First UI (A2UI)**: Returns structured UI cards and layout columns natively rendered by the frontend rather than markdown text alone.

---

## 🛠️ Google Cloud Services & Integrations

The code in this repository connects directly to the following Google Cloud and ADK services:

| Component / Service | Implementation in Code | Purpose |
|---|---|---|
| **Agent Platform / Agent Runtime** | `agents-cli-manifest.yaml`, `Dockerfile` | Hosts the ADK agent runtime over the A2A protocol (`gemini-3.8-flash`). |
| **Vertex AI Memory Bank** | `PreloadMemoryTool`, `generate_memories_callback` in `app/agent.py` | Cross-session persistent memory for traveler preferences, allergies, and history. |
| **Cloud Firestore** | `list_destinations`, `get_destination_details`, `save_destination` in `app/agent.py` | Real-time NoSQL database holding the curated destination catalog and reviews. |
| **Cloud Storage** | `generate_destination_image`, `generate_destination_video` in `app/agent.py` | Public media bucket storing generated postcards and cinematic preview videos. |
| **Vertex AI Image Generation** | `client.models.generate_content(model="gemini-3.1-flash-lite-image")` in `app/agent.py` | On-demand scenic postcard generation. |
| **Vertex AI Omni Video** | `client.interactions.create(model="gemini-omni-flash-preview")` in `app/agent.py` | Short cinematic travel preview video generation. |
| **Vertex AI Agent Engine Sandbox** | `AgentEngineSandboxCodeExecutor` in `app/agent.py` | Isolated secure code execution environment for budget formulas and data analysis. |
| **A2UI Protocol** | `a2ui_schema_manager`, `a2ui_callback` in `app/agent.py` | Structured JSON component system rendering visual cards in the chat UI. |
| **FastAPI Proxy & Web UI** | `frontend/main.py`, `frontend/static/index.html` | Client-facing web interface communicating with the deployed agent via A2A. |

---

## 📋 Implemented Tools (`app/agent.py`)

1. `PreloadMemoryTool`: Loads long-term traveler profile and memory bank facts into the agent context at the start of each session.
2. `list_destinations(travel_style)`: Queries the Firestore `destinations` collection filtered by travel style.
3. `get_destination_details(destination_id)`: Fetches complete catalog details for a specific destination from Firestore.
4. `save_destination(destination_id, name, country, description, ...)`: Saves or updates a destination document in Firestore.
5. `fetch_live_weather(location)`: Fetches current temperature, humidity, wind speed, and weather condition for any location.
6. `convert_currency(amount, from_currency, to_currency)`: Converts trip budgets and activity costs with live exchange rates.
7. `geocode_address(address)`: Resolves landmark or destination names to latitude/longitude coordinates via Google Maps Geocoding.
8. `find_nearby_places(latitude, longitude, place_type, radius_meters)`: Discovers nearby attractions, restaurants, museums, or lodging via Google Maps Places API.
9. `generate_destination_image(prompt, tool_context, destination_name)`: Generates travel postcard images using `gemini-3.1-flash-lite-image`, registers them in the Playground's Artifacts panel, and publishes them to Google Cloud Storage.
10. `generate_destination_video(prompt, tool_context, destination_name)`: Generates short cinematic travel preview videos using `gemini-omni-flash-preview`, saves them as artifacts, and uploads them to Google Cloud Storage.

*(Note: Grounded RAG corpus integration is planned, but not yet implemented; the agent currently utilizes Firestore and real-time APIs for factual grounding).*

---

## 💻 Local Development & Setup

### Prerequisites
- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) (`gcloud`) authenticated with a project containing Vertex AI, Firestore, and Cloud Storage permissions.

### 1. Install Dependencies

Clone the repository and install dependencies using `uv`:

```bash
cd travel-planner
uv sync
```

### 2. Configure Environment

Copy the example environment file and configure your API keys and project settings:

```bash
cp .env.example .env
```

Ensure the following variables are set in `.env`:
```bash
GOOGLE_GENAI_USE_VERTEXAI=true
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_CLOUD_LOCATION=us-east1
MEMORY_BANK_LOCATION=us-east1
GOOGLE_MAPS_API_KEY=your-google-maps-api-key
```

### 3. Seed the Destination Catalog

Populate the Firestore database with curated travel destinations:

```bash
uv run python seed_firestore.py
```

### 4. Run the Agent Playground

Launch the interactive ADK Web interface with hot reloading and Memory Bank support:

```bash
uv run adk web . --port 8080 --reload_agents --memory_service_uri=agentengine://<YOUR_MEMORY_BANK_ID>
```

Open your browser to the local playground address to test tools, inspect prompts, and view artifacts.

---

## 🌐 Running the Web Frontend Locally

The repository includes a standalone FastAPI proxy and chat interface in `frontend/` that communicates with the deployed Agent Runtime via the A2A protocol:

```bash
cd frontend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Set your deployed Agent Engine resource name
export AGENT_ENGINE_RESOURCE_NAME="projects/<PROJECT_NUMBER>/locations/us-east1/reasoningEngines/<RESOURCE_ID>"
export AGENT_DIRECTORY="app"

python main.py
```

Open your browser to the local port (default: 8080) to interact with the branded Travel Planner chat UI, quick prompt pills, and real-time A2UI card renderer.

---

## 🚢 Deployment

### Deploy Agent to Agent Runtime

Deploy the agent to Google Cloud Agent Platform using `agents-cli`:

```bash
agents-cli deploy --project <your-gcp-project-id> --update-env-vars GOOGLE_MAPS_API_KEY=<your-api-key>
```

### Deploy Frontend to Cloud Run

Deploy the web frontend container to Google Cloud Run:

```bash
cd frontend
gcloud run deploy travel-planner-frontend \
  --source . \
  --region us-east1 \
  --set-env-vars AGENT_ENGINE_RESOURCE_NAME="projects/<PROJECT_NUMBER>/locations/us-east1/reasoningEngines/<RESOURCE_ID>",AGENT_DIRECTORY="app" \
  --allow-unauthenticated
```
