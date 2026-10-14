# Post-Audit Implementation Roadmap: Subsequent Phases

## Phase 2: Foundation & Context Enrichment (Next Phase)
- **Objective:** Eliminate state divergence between the active workspace itinerary and the Copilot assistant.
- **Tasks:**
  1. Enhance `frontend/main.py` and `frontend/static/index.html` to inject active trip metadata (destination, current day, scheduled activities) into `/chat` payloads.
  2. Implement conversational fallback text generation in `_extract_parts` when the agent executes background tools without returning explicit text.
  3. Ensure Pydantic serialization for `FeasibilityReport.verification_density` always renders formatted percentage strings.
- **Measurable Acceptance Criteria:**
  - Copilot responds to "What are we doing on Day 3?" with exact activities from the active trip workspace.
  - Zero instances of `(The agent didn't return a reply.)` on valid user requests.

---

## Phase 3: Intelligence & Dynamic Routing
- **Objective:** Connect Places API live geocodes with dynamic walking and driving duration estimates.
- **Tasks:**
  1. Implement automated bounding box geocoding for activity clusters to calculate intra-city transit minutes.
  2. Add real-time opening hours verification via Places API Place Details when an API key is present.
- **Measurable Acceptance Criteria:**
  - Day activities display estimated travel times between consecutive stops.
  - Conflicts flagged if an attraction is visited outside verified operating hours.

---

## Phase 4: Adaptation & Targeted Replanning
- **Objective:** Enable granular, non-destructive activity swaps.
- **Tasks:**
  1. Add "Replace Activity" interactive action in daily itinerary cards.
  2. Connect Copilot command "Replace lunch with Hyderabadi biryani" to targeted meal slot substitution rather than regenerating the entire 7-day schedule.
- **Measurable Acceptance Criteria:**
  - Single activity updated in `currentItinerary` while preserving the remaining 6 days unchanged.

---

## Phase 5: Experience & Presentation
- **Objective:** Finalize interactive map visualization and responsive layouts.
- **Tasks:**
  1. Render interactive Google Maps markers with numbered stop pins for each day.
  2. Expand Food Passport with photo upload or visual badge rewards.
- **Measurable Acceptance Criteria:**
  - Interactive map dynamically pans and zooms to the active day's coordinates.

---

## Phase 6: Verification & Hardening
- **Objective:** Run complete end-to-end regression suites and load tests.
- **Tasks:**
  1. Automate 10-destination cross-switching integration test suite.
  2. Perform adversarial input testing (conflicting date ranges, nonexistent cities).
- **Measurable Acceptance Criteria:**
  - 100% test pass rate across all unit and integration suites.

---

## Phase 7: Delivery & Cloud Run Readiness
- **Objective:** Package production container and verify deployment readiness.
- **Tasks:**
  1. Verify multi-stage Docker build with zero redundant dev dependencies.
  2. Validate Cloud Run environment variable configuration.
- **Measurable Acceptance Criteria:**
  - Container boots cleanly in <3 seconds without missing module warnings.
