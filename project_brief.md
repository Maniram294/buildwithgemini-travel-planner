# My agent: travel-planner
One-liner: An Evidence-Backed AI Travel Intelligence Agent that constructs realistic, verified travel itineraries grounded in real Google Places API data, actionable Google Maps and directions URLs, authentic regional cuisine, astronomical timing, seasonal events, and deterministic budget calculations.

Product differentiator:
Move beyond plausible generative text: retrieve verified real-world places, compute deterministic duration rules, validate geographic proximity, provide actionable turn-by-turn directions links, calculate source-backed multi-currency budgets, and provide offline travel access.

Tool coverage:
- Duration Intelligence: Deterministic trip duration parser (`plan_trip_duration`) supporting default 7-day planning (Case A), exact requested day counts (Case B), calendar date ranges with inclusive day math (Case C), and conflict detection (Case D).
- Verified Links & Actions: Automatically constructs Google Maps place URLs, turn-by-turn directions URLs between consecutive itinerary stops, and safe official website links.
- Authentic Local Food Discovery: Combines verified regional culinary heritage records (`discover_authentic_cuisine`) with live Google Places API (New) verification (ratings, reviews, hours, addresses, and maps links).
- Destination Experiences: Real-time discovery of cultural landmarks, museums, and walkable districts via Google Places API (New).
- Best-Time-to-Visit Engine: Astronomical sunrise/sunset calculations via Open-Meteo and golden-hour guidance (`get_best_visit_time`).
- Source-Backed Budget Calculator: Multi-currency deterministic cost engine distinguishing verified fees from estimates with group/daily subtotals (`calculate_budget_plan`).
- Seasonal Events Discovery: Date-filtered cultural festivals and municipal events (`get_seasonal_events`).
- Food Passport: User-controlled tracking of regional dishes to try and dishes tried with Firestore persistence (`manage_food_passport`).
- Offline Trip Pack: Self-contained offline itinerary compilation (`compile_offline_pack`) and one-click frontend export.
- Memory: Vertex AI Memory Bank persists traveler style, dietary needs/strict food allergies, home airport, and previous destinations visited.
- Catalog & Practical Tools: Firestore curated destination guides, live weather via Open-Meteo, international currency conversions, and Vertex AI code execution sandbox.
- Image gen: Generates scenic destination postcards and visual moodboards using `gemini-3.1-flash-lite-image` with Cloud Storage hosting.
