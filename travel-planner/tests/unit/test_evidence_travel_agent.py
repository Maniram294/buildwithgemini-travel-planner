"""Comprehensive unit test suite for the Evidence-Backed Travel Intelligence Agent."""

import datetime
from unittest.mock import MagicMock, patch
import pytest

from app.trip_utils import parse_trip_duration, validate_itinerary_structure
from app.link_utils import (
    build_google_maps_search_url,
    build_google_maps_directions_url,
    validate_web_url,
    format_evidence_record,
)
from app.culinary_data import get_culinary_context
from app.budget_utils import calculate_trip_budget
from app.timing_utils import evaluate_best_visit_time
from app.events_data import find_seasonal_events
from app.food_passport import food_passport
from app.offline_pack import generate_offline_trip_pack
from app.agent import root_agent


class TestTripDurationIntelligence:
    """1. Exact-Duration Trip Planner tests (A, B, C, D cases, invalid ranges, and preservation)."""

    def test_case_a_default_seven_days(self):
        prompts = ["Plan a trip to Kyoto", "Show me around Tokyo", "Explore Istanbul"]
        for p in prompts:
            res = parse_trip_duration(p)
            assert res["num_days"] == 7
            assert res["is_default"] is True
            assert res["has_conflict"] is False
            assert "7-day" in res["explanation"]

    def test_case_b_exact_days(self):
        cases = [
            ("3-day trip to Paris", 3),
            ("I need a 5 days itinerary", 5),
            ("10-day trip in Vietnam", 10),
            ("Plan a two weeks holiday", 14),
        ]
        for p, expected in cases:
            res = parse_trip_duration(p)
            assert res["num_days"] == expected
            assert res["is_default"] is False
            assert res["has_conflict"] is False

    def test_case_c_calendar_dates_inclusive(self):
        # Nov 2 to Nov 8 is exactly 7 days
        res = parse_trip_duration("Visit Tokyo from November 2 to November 8", reference_date=datetime.date(2026, 1, 1))
        assert res["num_days"] == 7
        assert res["start_date"] == "2026-11-02"
        assert res["end_date"] == "2026-11-08"
        assert res["is_default"] is False

    def test_case_d_conflict_detection(self):
        # 3 days vs 7 calendar days
        res = parse_trip_duration("Plan a 3-day trip from November 2 to November 8", reference_date=datetime.date(2026, 1, 1))
        assert res["has_conflict"] is True
        assert "3-day" in res["conflict_message"]
        assert "7 calendar days" in res["conflict_message"]

    def test_validate_itinerary_structure_mismatch(self):
        itinerary = {"days": [{"day_number": 1}, {"day_number": 2}]}
        validation = validate_itinerary_structure(itinerary, requested_days=3)
        assert validation["valid"] is False
        assert "contains 2 days, but 3 days were requested" in validation["errors"][0]


class TestVerifiedLinksAndActions:
    """2. Verified place links, search URLs, directions, and URL validation."""

    def test_google_maps_search_url_encoding(self):
        url = build_google_maps_search_url("Gion Karyo", "Higashiyama, Kyoto")
        assert "https://www.google.com/maps/search/?api=1&query=" in url
        assert "Gion%20Karyo" in url
        assert "Higashiyama" in url

    def test_google_maps_directions_url_consecutive_stops(self):
        url = build_google_maps_directions_url(
            destination_name="Kiyomizu-dera",
            origin_name="Gion-Shijo Station",
            travel_mode="walking",
        )
        assert "https://www.google.com/maps/dir/?api=1" in url
        assert "destination=Kiyomizu-dera" in url
        assert "origin=Gion-Shijo%20Station" in url
        assert "travelmode=walking" in url

    def test_validate_web_url_security(self):
        assert validate_web_url("https://www.japan.travel") == "https://www.japan.travel"
        assert validate_web_url("http://museum.org") == "http://museum.org"
        assert validate_web_url("javascript:alert(1)") is None
        assert validate_web_url("ftp://example.com") is None
        assert validate_web_url("") is None


class TestAuthenticFoodAndDietarySafety:
    """3. Authentic local food discovery, regional context, and allergy safety."""

    def test_culinary_context_retrieval(self):
        tokyo = get_culinary_context("Tokyo")
        assert tokyo is not None
        assert any(d["dish"] == "Monjayaki" for d in tokyo["signature_dishes"])

        kyoto = get_culinary_context("Kyoto")
        assert kyoto is not None
        assert any("Yudofu" in d["dish"] for d in kyoto["signature_dishes"])

    def test_evidence_record_formatting(self):
        record = format_evidence_record(
            entity_name="Okutan Kiyomizu",
            source="Google Places API (New)",
            verification_status="verified",
            details={"rating": 4.5, "review_count": 850},
        )
        assert record["entity_name"] == "Okutan Kiyomizu"
        assert record["verification_status"] == "verified"
        assert "checked_at" in record


class TestBestTimeToVisitEngine:
    """4. Best-time-to-visit intelligence with daylight and weather."""

    @patch("urllib.request.urlopen")
    def test_evaluate_best_visit_time_astronomical(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = (
            b'{"daily": {"time": ["2026-10-14"], "sunrise": ["2026-10-14T06:05"], "sunset": ["2026-10-14T17:20"]}}'
        )
        mock_urlopen.return_value.__enter__.return_value = mock_response

        res = evaluate_best_visit_time(
            attraction_name="Shibuya Sky",
            attraction_type="viewpoint",
            latitude=35.6580,
            longitude=139.7016,
            target_date="2026-10-14",
        )
        assert res["attraction_name"] == "Shibuya Sky"
        assert res["sunrise_local"] == "06:05"
        assert res["sunset_local"] == "17:20"
        assert "Sunset is at 17:20" in res["rationale"]
        assert res["verification_status"] == "verified"


class TestSourceBackedBudgetCalculator:
    """5. Deterministic source-backed budget calculation."""

    def test_calculate_trip_budget_math(self):
        expenses = [
            {"category": "accommodation", "amount": 200.0, "currency": "USD", "unit": "per_night", "is_verified": True, "source": "Official Hotel", "description": "Hotel"},
            {"category": "food", "amount": 50.0, "currency": "USD", "unit": "per_person", "is_verified": False, "source": "Estimated", "description": "Meals", "day": 1},
            {"category": "activities", "amount": 25.0, "currency": "USD", "unit": "per_person", "is_verified": True, "source": "Temple Ticket", "description": "Entry fee", "day": 1},
        ]
        # Group size 2, 3 days (2 nights)
        res = calculate_trip_budget(expenses, group_size=2, num_days=3, target_currency="USD")
        # Accommodation: 200 * 2 nights = 400
        # Food: 50 * 2 people = 100
        # Activities: 25 * 2 people = 50
        # Total = 550 USD
        assert res["total_group_cost"] == 550.0
        assert res["total_per_person_cost"] == 275.0
        assert res["category_breakdown"]["accommodation"] == 400.0
        assert res["category_breakdown"]["food"] == 100.0
        assert res["category_breakdown"]["activities"] == 50.0
        assert res["verification_summary"]["verified_costs_total"] == 450.0
        assert res["verification_summary"]["estimated_costs_total"] == 100.0


class TestSeasonalEventsDiscovery:
    """6. Seasonal events filtering and verification."""

    def test_seasonal_events_date_filter(self):
        # Kyoto Jidai Matsuri takes place on October 22
        oct_events = find_seasonal_events("Kyoto", "2026-10-20", "2026-10-25")
        assert oct_events["count"] >= 1
        assert any(e["name"] == "Jidai Matsuri (Festival of the Ages)" for e in oct_events["events_found"])

        # In November, Jidai Matsuri does not overlap
        nov_events = find_seasonal_events("Kyoto", "2026-11-01", "2026-11-10")
        assert not any(e["name"] == "Jidai Matsuri (Festival of the Ages)" for e in nov_events["events_found"])


class TestFoodPassportAndPersistence:
    """7. Food passport user interactions and fallbacks."""

    def test_food_passport_lifecycle(self):
        user_id = "test_traveler_qa"
        add_res = food_passport.add_or_update_dish(
            user_id=user_id,
            dish_name="Yudofu",
            destination="Kyoto",
            status="want_to_try",
            notes="Must try in Nanzen-ji neighborhood",
        )
        assert add_res["status"] == "success"

        dishes = food_passport.list_passport_dishes(user_id=user_id, destination="Kyoto")
        assert any(d["dish_name"] == "Yudofu" for d in dishes)

        # Update to tried with rating
        food_passport.add_or_update_dish(
            user_id=user_id,
            dish_name="Yudofu",
            destination="Kyoto",
            status="tried",
            rating=5,
        )
        updated_dishes = food_passport.list_passport_dishes(user_id=user_id, status="tried")
        assert any(d["dish_name"] == "Yudofu" and d["rating"] == 5 for d in updated_dishes)

        # Cleanup
        del_res = food_passport.remove_dish(user_id=user_id, dish_name="Yudofu", destination="Kyoto")
        assert del_res["status"] == "success"


class TestOfflineTripPack:
    """8. Offline trip pack generation and connectivity disclosure."""

    def test_generate_offline_trip_pack(self):
        itinerary = [
            {"day": 1, "morning": "Fushimi Inari", "lunch": "Inari Sushi", "evening": "Gion"},
        ]
        pack = generate_offline_trip_pack(
            trip_name="Autumn Kyoto Trip",
            destination="Kyoto",
            duration_days=1,
            itinerary_days=itinerary,
            start_date="2026-11-02",
            end_date="2026-11-02",
        )
        assert pack["trip_name"] == "Autumn Kyoto Trip"
        assert pack["duration_days"] == 1
        assert "connectivity_notice" in pack
        assert "offline trip pack is fully viewable without internet connection" in pack["connectivity_notice"]
        assert len(pack["days"]) == 1


class TestToolRegistrationAndIntegrity:
    """9. Agent tool registration integrity."""

    def test_agent_toolset_and_no_video_model(self):
        tool_names = [t.__name__ if hasattr(t, "__name__") else t.__class__.__name__ for t in root_agent.tools]
        assert "generate_destination_video" not in tool_names
        assert "plan_trip_duration" in tool_names
        assert "discover_authentic_cuisine" in tool_names
        assert "search_destination_experiences" in tool_names
        assert "get_best_visit_time" in tool_names
        assert "calculate_budget_plan" in tool_names
        assert "get_seasonal_events" in tool_names
        assert "manage_food_passport" in tool_names
        assert "compile_offline_pack" in tool_names


class TestItineraryCompletionAndA2uiPreservation:
    """10. Verify that A2UI overview cards do not discard accompanying multi-day itinerary schedules."""

    def test_a2ui_callback_preserves_daily_itinerary_prose(self):
        from app.a2ui_utils import a2ui_callback
        from google.genai import types
        from google.adk.models.llm_response import LlmResponse
        from unittest.mock import MagicMock

        mixed_output = """Here is your 7-day Tokyo itinerary from November 2 to November 8.

```json
[
  {"beginRendering": {"surfaceId": "tokyo-overview", "root": "root-card"}},
  {"surfaceUpdate": {"surfaceId": "tokyo-overview", "components": [
    {"id": "root-card", "component": {"Card": {"child": "col1"}}},
    {"id": "col1", "component": {"Column": {"children": {"explicitList": ["t1"]}}}},
    {"id": "t1", "component": {"Text": {"text": {"literalString": "Tokyo Shitamachi & Ramen Journey"}, "usageHint": "h2"}}}
  ]}}
]
```

### Day 1: Historic Asakusa & Chuka Soba
* **Morning**: Senso-ji Temple and Nakamise-dori.
* **Lunch**: Traditional Chuka Soba at Ramen Yoroiya.
* **Afternoon**: Walkable Kappa-bashi kitchen town.
* **Evening**: Asakusa underground food street.

### Day 2: Yanaka Ginza & Shitamachi Atmosphere
* **Morning**: Yanaka Cemetery and walking paths.
* **Lunch**: Niboshi ramen in Nippori.
* **Afternoon**: Traditional craft shops.
* **Evening**: Nezu shrine twilight walk.
"""
        initial_response = LlmResponse(
            content=types.Content(role="model", parts=[types.Part(text=mixed_output)])
        )
        ctx = MagicMock()
        result = a2ui_callback(ctx, initial_response)

        assert result is not None
        # Check that we have both A2UI parts and Text parts
        parts = result.content.parts
        assert len(parts) >= 2

        # Verify A2UI parts exist
        a2ui_parts = [p for p in parts if p.inline_data and b"tokyo-overview" in p.inline_data.data]
        assert len(a2ui_parts) >= 1

        # Verify text parts preserve the daily itinerary
        text_parts = [p for p in parts if p.text and "Day 1: Historic Asakusa" in p.text]
        assert len(text_parts) == 1
        assert "Day 2: Yanaka Ginza" in text_parts[0].text
        assert "Chuka Soba" in text_parts[0].text

