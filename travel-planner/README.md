# ✈️ Travel Planner — Evidence-Backed Travel Intelligence Agent

> An AI-powered Evidence-Backed Travel Intelligence Agent that constructs realistic, verified travel itineraries grounded in live Google Places API data, actionable Google Maps and directions URLs, authentic regional cuisine, astronomical timing, seasonal events, deterministic budget calculations, and offline travel packs.

![Travel Planner Demo](demo.gif)

---

## 🌟 Core Product Purpose

Generic travel assistants hallucinate non-existent attractions, invent addresses and operating hours, and fail basic travel math. **Travel Planner** operates on an evidence-first philosophy:

> **"Discover a destination through verified places, working navigation links, authentic regional cuisine, date-aware recommendations, practical routing, deterministic budget calculations, seasonal events, persistent traveler preferences, and offline access."**

### Core Capabilities:
1. **Intelligent Trip-Duration Handling (`plan_trip_duration`)**:
   - **Case A (No dates/duration)**: Generates a comprehensive **7-day itinerary** by default and explicitly states this assumption.
   - **Case B (Exact duration)**: Faithfully creates the exact requested day count (e.g. 3-day, 5-day, 7-day, 10-day).
   - **Case C (Calendar dates)**: Calculates inclusive calendar days (e.g., Nov 2 to Nov 8 = 7 calendar days) and aligns seasonal operating schedules.
   - **Case D (Conflict detection)**: Flags conflicts between stated days and date spans (e.g. *"3-day trip from Nov 2 to Nov 10"*) and prompts concisely for clarification.
2. **Verified Place Links & Turn-by-Turn Directions (`link_utils.py`)**:
   - Direct Google Maps place links (`maps/search?api=1&query=...`) for all recommended stops.
   - Turn-by-turn directions URLs between consecutive stops (e.g. transit or walking from Day 1 Morning stop to Lunch stop).
   - Sanitized official website links (HTTP/HTTPS only).
3. **Authentic Local Food Discovery (`discover_authentic_cuisine`)**:
   - Grounded regional dishes, cultural context, and traditional market districts (e.g., Kyo-ryori, Shojin Ryori, Nishiki Market, Tsukiji).
   - Paired with live Google Places API (New) verification for real business existence, addresses, actual ratings, review counts, and hours.
   - Strict adherence to food allergies and dietary restrictions.
4. **Best-Time-to-Visit Intelligence (`get_best_visit_time`)**:
   - Astronomical sunrise and sunset calculations via Open-Meteo for golden-hour views, temple morning visits, and trail daylight safety.
5. **Deterministic Source-Backed Budget Calculator (`calculate_budget_plan`)**:
   - Python-powered financial calculation layer independent of model math.
   - Category breakdowns (accommodation, food, transit, activities, contingency), daily subtotals, per-person vs. group costs, and explicit distinction between verified ticket prices and estimated expenses.
6. **Seasonal Events Discovery (`get_seasonal_events`)**:
   - Date-aware matching of municipal and cultural festivals (e.g., Kyoto Jidai Matsuri in late October, Gion Matsuri in July) verified against cultural calendars.
7. **User-Approved Food Passport (`manage_food_passport`)**:
   - Personal passport allowing travelers to save dishes to try, log dishes tried with 1-5 ratings and notes, stored durably in Cloud Firestore.
8. **Offline Trip Pack (`compile_offline_pack` & Frontend Export)**:
   - Self-contained travel document generation with complete stops, addresses, and saved links.
   - One-click "Save Trip Offline" export in the chat frontend.
9. **Trip Copilot Context-Aware Replanning**:
   - Real-time conversational modifications to active trips.
   - Targeted activity and meal replacements that update day schedules and recalculate budgets deterministically without corrupting other days.
10. **Browser-Persistent Saved Trips**:
    - Local storage trip management allowing users to save, review, load, and switch between saved itineraries with 1-click active workspace updates.

---

## 🛠️ Google Cloud Services & Architecture

| Component / Service | Implementation in Code | Purpose |
|---|---|---|
| **Agent Platform / Agent Runtime** | `agents-cli-manifest.yaml`, `Dockerfile` | Hosts the ADK agent runtime over the A2A protocol (`gemini-3.8-flash`). |
| **Vertex AI Memory Bank** | `PreloadMemoryTool`, `generate_memories_callback` in `app/agent.py` | Cross-session persistent memory for traveler preferences and strict food allergies. |
| **Cloud Firestore** | `list_destinations`, `save_destination`, `FoodPassportManager` | Curated destination catalog and traveler food passport storage. |
| **Google Maps Places API (New)** | `discover_authentic_cuisine`, `search_destination_experiences`, `find_nearby_places` | Live business verification, ratings, review counts, operating hours, and Maps URLs. |
| **Google Maps Geocoding API** | `geocode_address` in `app/agent.py` | Geocoding landmarks to latitude/longitude coordinates. |
| **Open-Meteo APIs** | `fetch_live_weather`, `evaluate_best_visit_time` | Real-time weather conditions, forecasts, and astronomical sunrise/sunset calculations. |
| **Cloud Storage** | `generate_destination_image` in `app/agent.py` | Media bucket storing generated destination postcards. |
| **Vertex AI Image Generation** | `client.models.generate_content(model="gemini-3.1-flash-lite-image")` | On-demand scenic destination postcard generation. |
| **Vertex AI Code Execution Sandbox** | `AgentEngineSandboxCodeExecutor` in `app/agent.py` | Secure isolated environment for mathematical calculations. |
| **A2UI Protocol & Web Frontend** | `a2ui_schema_manager`, `frontend/static/index.html` | Rich interactive card UI, view switcher, day tabs, and offline pack export. |

---

## 📋 Implemented Agent Tools (`app/agent.py`)

1. `plan_trip_duration(user_request)`: Deterministic duration and date parsing (Cases A, B, C, D).
2. `discover_authentic_cuisine(destination, specialty_or_dish, neighborhood, origin_location, max_results)`: Verified regional cuisine and live Google Places discovery with directions.
3. `search_destination_experiences(destination, experience_category, neighborhood, origin_location, max_results)`: Cultural landmarks, walkable districts, and museums via Places API (New).
4. `get_best_visit_time(attraction_name, attraction_type, latitude, longitude, target_date)`: Astronomical timing, daylight safety, and golden-hour recommendations.
5. `calculate_budget_plan(expenses_json, group_size, num_days, target_currency)`: Deterministic budget calculator with verified vs. estimated tracking.
6. `get_seasonal_events(destination, start_date, end_date)`: Date-filtered verified cultural events.
7. `manage_food_passport(action, user_id, dish_name, destination, status, rating, notes)`: User food passport (add, list, remove dishes).
8. `compile_offline_pack(trip_name, destination, duration_days, itinerary_json, start_date, end_date)`: Self-contained offline pack compiler.
9. `PreloadMemoryTool`: Long-term traveler profile, preferences, and dietary restrictions.
10. `list_destinations(travel_style)`: Firestore destination catalog search.
11. `get_destination_details(destination_id)`: Firestore destination details lookup.
12. `save_destination(...)`: Firestore destination saving.
13. `fetch_live_weather(location)`: Real-time weather via Open-Meteo.
14. `convert_currency(amount, from_currency, to_currency)`: Live international currency conversion.
15. `geocode_address(address)`: Google Maps geocoding to coordinates.
16. `find_nearby_places(latitude, longitude, place_type, radius_meters)`: Nearby places search.
17. `generate_destination_image(prompt, tool_context, destination_name)`: Scenic postcard generation via `gemini-3.1-flash-lite-image`.

*(Note: Video generation is deliberately excluded from product scope. Grounded RAG corpus integration is marked as planned).*

---

## 💻 Local Development & Testing

### 1. Run Complete Test Suite (92 Tests)

The repository includes a comprehensive 92-test suite covering Unit, Integration, Multi-Agent Orchestration, Trip Copilot replanning, and Playwright End-to-End browser workflows:

```bash
cd travel-planner
.venv/bin/pytest tests/ -v
```

All 92 tests pass with 100% success rate:
- **Unit Suite (60 tests)**: Schema models, validator, budget calculations, weather, places, multi-agent orchestration, and copilot engine.
- **Integration Suite (5 tests)**: Agent streaming SSE, batch queries, live places tools, and static asset delivery.
- **Phase 5 Interactive E2E (7 tests)**: Full user journeys, day tabs, Maps link validation, destination switching, and narrow-viewport mobile responsiveness.
- **Phase 6 Verification Scenarios (7 tests)**: Scenarios A through G including 3-trial repeatability and persistence checks.

### 2. Run the Web Frontend & Proxy Server

Start the full web application locally:

```bash
cd travel-planner/frontend
.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8081
```

Access the UI at `http://localhost:8081`.

### 3. Screen Recording Verification

The repository contains an official 1080p screen recording: `demo_travel_planner.mp4`.
Refer to [`docs/demo-recording.md`](docs/demo-recording.md) for recording reproduction steps and metadata specifications.

---

## ⚠️ Known Limitations & Estimates

1. **Estimated Expenses**: Activity admission fees, museum tickets, and Frecciarossa rail fares are source-verified; general food estimates and miscellaneous transit represent regional market averages marked as estimates in the UI.
2. **Quota & Fallback Modes**: When live Google Places API quotas are depleted, the intelligence engine falls back to curated verified place databases to prevent user disruptions.
3. **RAG Integration**: Document grounding via Vertex AI RAG Engine is planned for upcoming releases.
