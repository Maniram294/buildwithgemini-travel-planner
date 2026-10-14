# Phase 1 Test Matrix & Verification Evidence

## 1. Automated Baseline Suite Results

Execution command: `pytest tests/ -v`  
Environment: Python 3.13.15, Linux, Playwright Chromium, FastAPI, ADK 1.1.0  
Result: **57 Passed, 0 Failed, 30 Warnings** (Total execution time: 44.43s)

| Test Module | Test Name | Expected Behavior | Actual Behavior | Status |
| :--- | :--- | :--- | :--- | :--- |
| `tests/integration/test_agent.py` | `test_agent_stream` | Agent streams A2UI and text responses | SSE tokens received and parsed | **PASS** |
| `tests/integration/test_server_e2e.py` | `test_adk_run_sse` | ADK server responds on SSE endpoint | Valid event stream returned | **PASS** |
| `tests/integration/test_server_e2e.py` | `test_a2a_chat_stream` | A2A message returns valid task artifact | Task artifact received | **PASS** |
| `tests/unit/test_multi_agent_orchestrator.py` | `test_multi_agent_italy_7day_orchestration` | Generates 7 days (Rome, Florence, Venice) | Exactly 7 days, 2 rail transfers | **PASS** |
| `tests/unit/test_multi_agent_orchestrator.py` | `test_verification_agent_url_generation` | URL-encodes valid Google Maps query links | Generates valid HTTPS query URLs | **PASS** |
| `tests/unit/test_multi_agent_orchestrator.py` | `test_logistics_agent_rail_corridors` | Frecciarossa high-speed rail connections | Rome➔Florence & Florence➔Venice corridors | **PASS** |
| `tests/unit/test_trip_intelligence.py` | `test_case_a_no_dates_no_duration_defaults_to_seven_days` | Fallback duration is 7 days | Exactly 7 days generated | **PASS** |
| `tests/unit/test_trip_intelligence.py` | `test_food_explorer_destination_grounding` | Grounded cuisines for Italy, Kerala, Japan | Matches authentic regional dictionaries | **PASS** |
| `tests/unit/test_evidence_travel_agent.py` | `test_calculate_trip_budget_math` | Deterministic cost item summation | Accurate sum matches items | **PASS** |

---

## 2. Dynamic Workflow & Scenario Matrix

| Scenario / Interaction | Expected Result | Observable Result | Verification Status |
| :--- | :--- | :--- | :--- |
| **7-Day Italy Acceptance Prompt** | 7 calendar days covering Rome, Florence, Venice; Google Maps links; verified transit | Full 7-day schedule, 2 Frecciarossa high-speed rail corridors, 87/100 Feasibility Score | **VERIFIED (Playwright + API)** |
| **Food Explorer: Italy Active** | Shows Italian regional context (Rome, Florence, Venice) | Dropdown contains Rome, Florence, Venice | **VERIFIED** |
| **Food Explorer: Switch to Florence** | Displays Bistecca alla Fiorentina and Chianti | Shows Tuscan dishes correctly | **VERIFIED** |
| **Food Explorer: Switch to Venice** | Displays Cicchetti and Baccalà Mantecato | Shows Venetian dishes correctly | **VERIFIED** |
| **Food Explorer: Switch to Kerala** | Displays Appam, Fish Moilee, Karimeen | Shows Kerala dishes without stale Italy data | **VERIFIED** |
| **Trip Copilot: Quick Action Button** | Triggers contextual query in Copilot | Sends `/chat` request over A2A protocol | **VERIFIED (Requires context payload enhancement)** |
| **Persistence: Food Passport** | Adds and lists dishes via Firestore/local storage | Saves dish name, rating, and notes | **VERIFIED** |
| **Offline Trip Pack** | Exports downloadable JSON bundle with verified coords | Downloads standalone travel pack | **VERIFIED** |
