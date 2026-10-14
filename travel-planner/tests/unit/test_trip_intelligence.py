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
"""Unit tests for authentic travel intelligence, duration parsing, and cuisine discovery."""

import datetime
from unittest.mock import MagicMock, patch
import pytest

from app.trip_utils import parse_trip_duration, validate_itinerary_structure
from app.culinary_data import get_culinary_context, REGIONAL_SPECIALTIES
from app.agent import (
    plan_trip_duration,
    discover_authentic_cuisine,
    search_destination_experiences,
    root_agent,
)


class TestTripDurationHandling:
    """Test suite for Requirement 2: Intelligent trip-duration handling."""

    def test_case_a_no_dates_no_duration_defaults_to_seven_days(self):
        """Case A: No dates and no duration mentioned defaults to exactly 7 days with explicit default flag."""
        prompts = [
            "Plan a trip to Kyoto.",
            "I want to explore Istanbul.",
            "Help me plan a vacation in Vietnam.",
            "Show me around Tokyo",
        ]
        for prompt in prompts:
            res = parse_trip_duration(prompt)
            assert res["num_days"] == 7
            assert res["is_default"] is True
            assert res["has_conflict"] is False
            assert "defaulting to a 7-day" in res["explanation"]

    def test_case_b_explicit_days(self):
        """Case B: Specified number of days produces exact duration without silent default."""
        test_cases = [
            ("Plan a three-day trip to Jaipur.", 3),
            ("I have 5 days in Singapore.", 5),
            ("Create a 10-day itinerary for Japan.", 10),
            ("Plan a 1-day food tour in Osaka.", 1),
            ("Plan a two weeks vacation across Italy.", 14),
        ]
        for prompt, expected_days in test_cases:
            res = parse_trip_duration(prompt)
            assert res["num_days"] == expected_days
            assert res["is_default"] is False
            assert res["has_conflict"] is False

    def test_case_c_calendar_date_range_inclusive(self):
        """Case C: Travel dates calculate inclusive calendar days."""
        # Nov 2 through Nov 8 is 7 calendar days (2, 3, 4, 5, 6, 7, 8)
        prompt_1 = "I'm visiting Tokyo from November 2 to November 8."
        res_1 = parse_trip_duration(prompt_1, reference_date=datetime.date(2026, 1, 1))
        assert res_1["num_days"] == 7
        assert res_1["start_date"] == "2026-11-02"
        assert res_1["end_date"] == "2026-11-08"
        assert res_1["is_default"] is False
        assert res_1["has_conflict"] is False

        # Dec 10 through Dec 14 is 5 calendar days (10, 11, 12, 13, 14)
        prompt_2 = "Plan my trip from December 10 through December 14."
        res_2 = parse_trip_duration(prompt_2, reference_date=datetime.date(2026, 1, 1))
        assert res_2["num_days"] == 5
        assert res_2["start_date"] == "2026-12-10"
        assert res_2["end_date"] == "2026-12-14"

    def test_case_d_duration_date_conflict(self):
        """Case D: Stated duration conflicting with date range triggers conflict flag and clarification."""
        prompt = "Plan a 3-day trip from November 2 to November 8."
        res = parse_trip_duration(prompt, reference_date=datetime.date(2026, 1, 1))
        assert res["has_conflict"] is True
        assert res["conflict_message"] is not None
        assert "3-day trip" in res["conflict_message"]
        assert "7 calendar days" in res["conflict_message"]


class TestCulinaryAndPlacesDiscovery:
    """Test suite for Requirements 3 & 4: Authentic local cuisine and destination discovery."""

    def test_regional_culinary_grounding(self):
        """Ensure destination culinary context returns rich grounded data without hallucination."""
        kyoto_data = get_culinary_context("Kyoto")
        assert kyoto_data is not None
        assert "Kyo-ryori" in kyoto_data["food_culture_summary"]
        dishes = [d["dish"] for d in kyoto_data["signature_dishes"]]
        assert any("Kaiseki" in d for d in dishes)
        assert any("Yudofu" in d for d in dishes)

        tokyo_data = get_culinary_context("Tokyo")
        assert tokyo_data is not None
        dishes_tokyo = [d["dish"] for d in tokyo_data["signature_dishes"]]
        assert any("Monjayaki" in d for d in dishes_tokyo)
        assert any("Tsukemen" in d for d in dishes_tokyo)

    @patch("urllib.request.urlopen")
    def test_discover_authentic_cuisine_with_places_api(self, mock_urlopen):
        """Test discover_authentic_cuisine returns verified places and grounds data."""
        mock_response = MagicMock()
        mock_response.read.return_value = (
            b'{"places": [{"displayName": {"text": "Okutan Kiyomizu"}, '
            b'"formattedAddress": "3-chome Kiyomizu, Higashiyama, Kyoto", '
            b'"rating": 4.5, "userRatingCount": 850, "priceLevel": "PRICE_LEVEL_MODERATE", '
            b'"regularOpeningHours": {"weekdayDescriptions": ["Mon: 11am-5pm"]}, '
            b'"googleMapsUri": "https://maps.google.com/?cid=123", '
            b'"primaryTypeDisplayName": {"text": "Tofu Restaurant"}}]}'
        )
        mock_urlopen.return_value.__enter__.return_value = mock_response

        with patch.dict("os.environ", {"GOOGLE_MAPS_API_KEY": "fake_key_for_test"}):
            res = discover_authentic_cuisine("Kyoto", specialty_or_dish="Yudofu", neighborhood="Higashiyama")
            assert res["destination"] == "Kyoto"
            assert res["regional_culinary_context"] is not None
            assert len(res["verified_places"]) == 1
            place = res["verified_places"][0]
            assert place["name"] == "Okutan Kiyomizu"
            assert place["rating"] == 4.5
            assert place["review_count"] == 850
            assert place["google_maps_url"] == "https://maps.google.com/?cid=123"
            assert "Verified Google Places API" in place["verification_source"]

    @patch("urllib.request.urlopen")
    def test_search_destination_experiences_mocked(self, mock_urlopen):
        """Test search_destination_experiences retrieves verified attractions with real addresses."""
        mock_response = MagicMock()
        mock_response.read.return_value = (
            b'{"places": [{"displayName": {"text": "Kiyomizu-dera"}, '
            b'"formattedAddress": "1 Chome-294 Kiyomizu, Higashiyama Ward, Kyoto", '
            b'"rating": 4.7, "userRatingCount": 35000, '
            b'"primaryTypeDisplayName": {"text": "Buddhist Temple"}, '
            b'"googleMapsUri": "https://maps.google.com/?cid=456", '
            b'"location": {"latitude": 34.9948, "longitude": 135.7850}}]}'
        )
        mock_urlopen.return_value.__enter__.return_value = mock_response

        with patch.dict("os.environ", {"GOOGLE_MAPS_API_KEY": "fake_key_for_test"}):
            res = search_destination_experiences("Kyoto", experience_category="cultural landmarks")
            assert res["count"] == 1
            attraction = res["places"][0]
            assert attraction["name"] == "Kiyomizu-dera"
            assert attraction["rating"] == 4.7
            assert attraction["google_maps_url"] == "https://maps.google.com/?cid=456"


class TestItineraryStructureAndQuality:
    """Test suite for Requirement 5 & 6: Usable itinerary structure and validation."""

    def test_validate_itinerary_structure(self):
        """Verify itinerary validator enforces requested days and meal/activity stops."""
        sample_valid_itinerary = {
            "days": [
                {
                    "day_number": 1,
                    "morning": {"activity": "Visit Fushimi Inari"},
                    "lunch": {"restaurant": "Nezameya", "dish": "Inari sushi"},
                    "afternoon": {"activity": "Tofuku-ji garden"},
                    "evening": {"restaurant": "Gion Karyo", "dish": "Kaiseki"},
                },
                {
                    "day_number": 2,
                    "morning": {"activity": "Arashiyama Bamboo Grove"},
                    "lunch": {"restaurant": "Yudofu Sagano", "dish": "Yudofu"},
                    "afternoon": {"activity": "Tenryu-ji Temple"},
                    "evening": {"restaurant": "Pontocho Robin", "dish": "Obanzai"},
                },
                {
                    "day_number": 3,
                    "morning": {"activity": "Kinkaku-ji"},
                    "lunch": {"restaurant": "Kura", "dish": "Nishin Soba"},
                    "afternoon": {"activity": "Ryoan-ji Rock Garden"},
                    "evening": {"restaurant": "Gion Duck Noodles", "dish": "Duck Ramen"},
                },
            ]
        }
        res = validate_itinerary_structure(sample_valid_itinerary, requested_days=3)
        assert res["valid"] is True
        assert len(res["errors"]) == 0
        assert len(res["warnings"]) == 0

        # Check mismatch in days
        res_mismatch = validate_itinerary_structure(sample_valid_itinerary, requested_days=7)
        assert res_mismatch["valid"] is False
        assert "Itinerary contains 3 days, but 7 days were requested." in res_mismatch["errors"][0]


class TestVideoFeatureRemoval:
    """Test suite for Requirement 9: Video generation removal from tool scope."""

    def test_video_tool_not_in_root_agent(self):
        """Confirm generate_destination_video is NOT registered in root_agent.tools."""
        tool_names = [t.__name__ if hasattr(t, "__name__") else t.__class__.__name__ for t in root_agent.tools]
        assert "generate_destination_video" not in tool_names
        assert "plan_trip_duration" in tool_names
        assert "discover_authentic_cuisine" in tool_names
        assert "search_destination_experiences" in tool_names
