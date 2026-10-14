# Application Architecture & System Baseline Audit

## 1. Executive Summary & Purpose

This document provides a factual, evidence-backed architectural mapping of the **Gemini Travel Planner** application as audited in **Phase 1**. It traces data structures, backend-frontend communication protocols, agent orchestration, persistence lifecycles, and component state boundaries.

---

## 2. Actual Request-Response Workflow

```mermaid
flowchart TD
    User([User Browser Interface]) -->|1. Submit Trip Prompt| FE_SPA[Vanilla JS Single-Page App\nindex.html]
    
    subgraph Frontend Server [FastAPI Proxy - Port 8081 / Port 8080]
        FE_SPA -->|2. POST /api/trip/canonical| API_Canonical[/api/trip/canonical]
        FE_SPA -->|3. POST /chat| API_Chat[/chat]
        FE_SPA -->|4. GET /api/food/specialties| API_Food[/api/food/specialties]
        FE_SPA -->|5. GET/POST /api/passport| API_Passport[/api/passport]
        FE_SPA -->|6. GET /api/events| API_Events[/api/events]
    end

    subgraph MultiAgent Engine [Multi-Agent Subsystem: app/multi_agent/]
        API_Canonical --> Agent_A[Agent A: MultiAgentTravelOrchestrator]
        Agent_A --> Agent_B[Agent B: Discovery & Decomposition]
        Agent_A --> Agent_C[Agent C: PlacesAndFoodVerificationAgent]
        Agent_A --> Agent_E[Agent E: TransportationAndLogisticsAgent]
        Agent_A --> Agent_H[Agent H: QualityAssuranceAndConsistencyAgent]
        Agent_H --> Canonical_State[(CanonicalTripState Pydantic Object)]
    end

    subgraph A2A Backend [Agent Engine Runtime - Port 8000 / Cloud Run]
        API_Chat -->|A2A Protocol / JSON-RPC| ADK_Runtime[Google ADK Root Agent\napp/agent.py]
        ADK_Runtime --> Gemini_Model[Gemini 2.5 Flash]
        ADK_Runtime --> Tools[Trip Utils / Weather / Currency / Places]
    end

    subgraph Persistence [State & Storage]
        API_Passport --> Firestore_DB[(Google Cloud Firestore\n'food_passport' collection)]
        FE_SPA --> LocalStorage[(Browser LocalStorage\n'saved_trips' / 'food_passport_local')]
    end

    Canonical_State -->|JSON Payload| FE_SPA
    ADK_Runtime -->|A2UI / Text Parts| API_Chat
    API_Chat -->|Extracted Parts JSON| FE_SPA
```

---

## 3. Component Inventory & Ownership

| Component | File Path | Implementation Status | Data In / Out | State Ownership & Persistence |
| :--- | :--- | :--- | :--- | :--- |
| **Frontend SPA** | `frontend/static/index.html` | Genuine | In: User interactions, JSON APIs<br>Out: DOM rendering, LocalStorage | Client DOM memory + `localStorage.getItem("saved_trips")` |
| **Frontend Gateway** | `frontend/main.py` | Genuine | In: HTTP Requests<br>Out: JSON Responses | Stateless proxy; caches user `_contexts` in in-memory dictionary |
| **Multi-Agent Engine** | `app/multi_agent/*.py` | Genuine | In: Prompt strings<br>Out: `CanonicalTripState` Pydantic models | In-memory during synthesis |
| **ADK Root Agent** | `app/agent.py` | Genuine | In: User text, A2A messages<br>Out: Streaming A2UI & text | State maintained by Agent Engine session/context |
| **Culinary & Food Grounding** | `app/culinary_data.py` | Genuine | In: Destination string<br>Out: Regional specialties, etiquette, markets | Static reference dataset |
| **Seasonal Events Engine** | `app/events_data.py` | Genuine | In: Destination, Date range<br>Out: List of cultural festivals | Static reference dataset |
| **Food Passport Manager** | `app/food_passport.py` | Genuine | In: Dish name, notes, rating<br>Out: Persistent passport records | Firestore collection `food_passport` with local fallback |
| **Places API Client** | `app/places_utils.py` | Genuine / Dependent | In: Text query, location bias<br>Out: Place ID, formatted address, rating | External Google Maps Places API (requires API key) |
| **Weather Integration** | `app/weather_utils.py` | Genuine | In: Lat/Lng coordinates<br>Out: 7-day temperature & precipitation | Open-Meteo REST API |
| **Currency Conversion** | `app/currency_utils.py` | Genuine | In: Amount, base, target<br>Out: Converted numeric amount | Exchange rate API with fixed fallback rates |

---

## 4. State Management & Lifecycle

1. **Active Trip Model:**
   - The application supports structured trip representations via `CanonicalTripState` (`app/trip_models.py`) containing `DaySchedule`, `Activity`, `CostItem`, `IntercityTransfer`, and `FeasibilityReport`.
   - On the client side, `currentItinerary` holds the active trip in JavaScript memory.
2. **Food Explorer Context Synchronization:**
   - Handled via `syncFoodExplorerWithActiveTrip(destName)` in `frontend/static/index.html`.
   - Detects active trip cities (e.g., Rome, Florence, Venice) and synchronizes `#food-dest-select` dropdown to prevent stale defaults (e.g. Chennai).
3. **Trip Copilot Context Protocol:**
   - Handled via `POST /chat` on `frontend/main.py`.
   - Operates over the A2A (Agent-to-Agent) JSON-RPC protocol against Google ADK Agent Engine.
   - Context is preserved across user turns via `context_id` tracking in `_contexts[user_id]`.
