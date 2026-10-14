"""Unit tests for Phase 5 UI & Frontend Integration."""

import json
import pytest
from app.multi_agent.orchestrator import MultiAgentTravelOrchestrator
from app.trip_models import CanonicalTripState
from app.trip_validator import validate_canonical_trip


def test_phase5_saved_trips_data_structure():
    """Verify that canonical trip state satisfies the exact schema consumed by the saved trips manager."""
    orchestrator = MultiAgentTravelOrchestrator()
    prompt = "I'm visiting Italy for 7 days. Rome, Florence, Venice."
    trip = orchestrator.build_canonical_trip(prompt)

    # Convert to serialized JSON payload as stored in localStorage['travel_planner_saved_trips']
    trip_dict = trip.model_dump()
    json_str = json.dumps(trip_dict)
    reloaded = json.loads(json_str)

    assert "destination" in reloaded
    assert "duration_days" in reloaded
    assert len(reloaded["days"]) == 7
    assert len(reloaded["intercity_transfers"]) >= 2
    assert reloaded["feasibility_report"]["overall_score"] > 80

    # Ensure validator accepts reloaded dictionary
    val = validate_canonical_trip(reloaded, expected_destination="Italy", expected_days=7)
    assert val.is_valid


def test_phase5_dynamic_transit_corridors_across_destinations():
    """Verify that intercity transfers carry correct modes and days for Italy, Japan, and Kerala."""
    orchestrator = MultiAgentTravelOrchestrator()

    # Italy
    trip_it = orchestrator.build_canonical_trip("Italy 7 days")
    days_with_transfer_it = [t.day for t in trip_it.intercity_transfers]
    assert 4 in days_with_transfer_it
    assert 6 in days_with_transfer_it
    assert all("rail" in t.mode.lower() or "freccia" in t.mode.lower() for t in trip_it.intercity_transfers)

    # Japan (Transfer from Tokyo to Kyoto occurs on Day 5)
    trip_jp = orchestrator.build_canonical_trip("Japan 7 days Tokyo and Kyoto")
    assert any("shinkansen" in t.mode.lower() or "bullet" in t.mode.lower() for t in trip_jp.intercity_transfers)
    assert any(t.day == 5 for t in trip_jp.intercity_transfers)

    # Kerala
    trip_kl = orchestrator.build_canonical_trip("Kerala 7 days Kochi, Munnar, Alappuzha")
    assert any("backwater" in t.mode.lower() or "rail" in t.mode.lower() or "scenic" in t.mode.lower() for t in trip_kl.intercity_transfers)
