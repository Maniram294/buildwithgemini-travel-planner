"""Unit tests for Phase 2: Reliable Trip Data and Deterministic Validation."""

import pytest
from app.multi_agent.orchestrator import MultiAgentTravelOrchestrator
from app.trip_models import CanonicalTripState, DaySchedule, Activity, CostItem, VerificationRecord
from app.trip_validator import validate_canonical_trip, ValidationResult


def test_validator_accepts_valid_canonical_italy_trip():
    """Verify that an authentic 7-day Italy trip passes all deterministic validation checks."""
    orchestrator = MultiAgentTravelOrchestrator()
    prompt = "I'm visiting Italy for 7 days. Plan Rome, Florence, Venice."
    trip = orchestrator.build_canonical_trip(prompt)

    result = validate_canonical_trip(trip, expected_destination="Italy", expected_days=7)
    assert result.is_valid is True
    assert len(result.errors) == 0
    assert result.verified_activities_count > 0
    assert result.total_activities_count == 28


def test_validator_rejects_duration_mismatch():
    """Verify that duration mismatches (e.g. 5 days when 7 requested) are rejected."""
    orchestrator = MultiAgentTravelOrchestrator()
    prompt = "I'm visiting Italy for 7 days."
    trip = orchestrator.build_canonical_trip(prompt)

    # Validate against expected_days=5
    result = validate_canonical_trip(trip, expected_destination="Italy", expected_days=5)
    assert result.is_valid is False
    assert any("Duration mismatch" in err for err in result.errors)


def test_validator_detects_destination_mismatch():
    """Verify that if a prompt is for Kerala, but an Italy trip is supplied, destination mismatch is caught."""
    orchestrator = MultiAgentTravelOrchestrator()
    trip = orchestrator.build_canonical_trip("Italy 7 days")

    # Pass expected destination as Kerala
    result = validate_canonical_trip(trip, expected_destination="Kerala", expected_days=7)
    assert result.is_valid is False
    assert any("Destination mismatch" in err for err in result.errors)


def test_validator_detects_budget_inconsistency():
    """Verify that corrupted or inconsistent budget totals trigger a validation error."""
    orchestrator = MultiAgentTravelOrchestrator()
    trip = orchestrator.build_canonical_trip("Italy 7 days")

    trip_dict = trip.model_dump()
    # Corrupt total budget to an arbitrary non-matching figure
    trip_dict["total_budget_per_person"] = 9999.00

    result = validate_canonical_trip(trip_dict, expected_destination="Italy", expected_days=7)
    assert result.is_valid is False
    assert any("Budget calculation mismatch" in err for err in result.errors)


def test_validator_detects_duplicate_day_numbers():
    """Verify that duplicate or skipped day numbers are flagged as errors."""
    orchestrator = MultiAgentTravelOrchestrator()
    trip = orchestrator.build_canonical_trip("Italy 7 days")

    trip_dict = trip.model_dump()
    # Force Day 2 to have day_number 1 (creating a duplicate)
    trip_dict["days"][1]["day_number"] = 1

    result = validate_canonical_trip(trip_dict, expected_destination="Italy", expected_days=7)
    assert result.is_valid is False
    assert any("Duplicate day number" in err for err in result.errors)


def test_validator_detects_duplicate_activities():
    """Verify that duplicate activities within the same day generate a warning."""
    orchestrator = MultiAgentTravelOrchestrator()
    trip = orchestrator.build_canonical_trip("Italy 7 days")

    trip_dict = trip.model_dump()
    # Duplicate first activity title in the second activity
    act1_title = trip_dict["days"][0]["activities"][0]["title"]
    trip_dict["days"][0]["activities"][1]["title"] = act1_title

    result = validate_canonical_trip(trip_dict, expected_destination="Italy", expected_days=7)
    assert any("Duplicate activity title" in warn for warn in result.warnings)
