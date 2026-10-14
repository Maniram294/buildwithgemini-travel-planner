"""Unit and integration tests for Phase 4: Context-Aware Trip Copilot and Intelligent Replanning."""

import pytest
from app.trip_models import CanonicalTripState, DaySchedule, Activity, CostItem, VerificationRecord
from app.copilot_engine import TripCopilotEngine
from app.multi_agent.orchestrator import MultiAgentTravelOrchestrator
from app.trip_validator import validate_canonical_trip


@pytest.fixture
def copilot_engine():
    return TripCopilotEngine()


@pytest.fixture
def active_italy_trip():
    orch = MultiAgentTravelOrchestrator()
    return orch.build_canonical_trip("I'm visiting Italy for 7 days. Rome, Florence, Venice.")


@pytest.fixture
def active_japan_trip():
    orch = MultiAgentTravelOrchestrator()
    return orch.build_canonical_trip("Plan a 7-day trip to Japan covering Tokyo and Kyoto.")


def test_intent_classification(copilot_engine, active_italy_trip):
    """Test deterministic categorization of user intent."""
    assert copilot_engine.classify_intent("What is the schedule for Day 3?", active_italy_trip) == "information"
    assert copilot_engine.classify_intent("How much does this trip cost?", active_italy_trip) == "information"
    assert copilot_engine.classify_intent("Find authentic trattorias in Florence", active_italy_trip) == "discovery"
    assert copilot_engine.classify_intent("Recommend nearby cafes in Rome", active_italy_trip) == "discovery"
    assert copilot_engine.classify_intent("Compare Rome Colosseum vs Pantheon", active_italy_trip) == "comparison"
    assert copilot_engine.classify_intent("Replace tomorrow's lunch with Da Enzo Trattoria", active_italy_trip) == "modification"
    assert copilot_engine.classify_intent("Relax pace on Day 4", active_italy_trip) == "modification"
    assert copilot_engine.classify_intent("Make Day 2 cheaper", active_italy_trip) == "modification"
    assert copilot_engine.classify_intent("Plan a new trip to Kerala", active_italy_trip) == "new_trip"


def test_information_request_does_not_modify_trip(copilot_engine, active_italy_trip):
    """Scenario 1: Ask a question about Day 3; verify that the trip remains completely unchanged."""
    initial_dump = active_italy_trip.model_dump()
    res = copilot_engine.process_message("What are our activities on Day 3?", active_trip=active_italy_trip, selected_day=3)
    
    assert res["intent"] == "information"
    assert res["modified_trip"] is None
    assert "Day 3" in res["reply"]
    # Verify active trip object was not mutated
    assert active_italy_trip.model_dump() == initial_dump


def test_discovery_requests_relevant_places(copilot_engine, active_italy_trip):
    """Scenario 2: Request nearby restaurants; verify results are relevant to planned location."""
    res = copilot_engine.process_message("Find nearby authentic trattorias for Day 2", active_trip=active_italy_trip, selected_day=2)
    assert res["intent"] == "discovery"
    assert res["modified_trip"] is None
    assert "Rome" in res["reply"]
    assert len(res["proposals"]) > 0


def test_targeted_meal_replacement(copilot_engine, active_italy_trip):
    """Scenario 3: Replace a meal; verify that only the intended meal changes."""
    day2_lunch_orig = next(a for a in active_italy_trip.days[1].activities if a.slot == "Lunch")
    day1_dump = active_italy_trip.days[0].model_dump()
    day3_dump = active_italy_trip.days[2].model_dump()

    res = copilot_engine.process_message(
        "Replace Day 2 lunch with authentic Roman Carbonara at Trattoria Da Enzo al 29",
        active_trip=active_italy_trip,
        selected_day=2,
    )

    assert res["intent"] == "modification"
    assert res["modified_trip"] is not None
    mod_trip = CanonicalTripState.model_validate(res["modified_trip"])

    # Day 2 lunch must be updated
    day2_lunch_new = next(a for a in mod_trip.days[1].activities if a.slot == "Lunch")
    assert "Trattoria Da Enzo al 29" in day2_lunch_new.title
    assert day2_lunch_new.title != day2_lunch_orig.title

    # Unaffected days must remain identical
    assert mod_trip.days[0].model_dump() == day1_dump
    assert mod_trip.days[2].model_dump() == day3_dump
    assert len(mod_trip.intercity_transfers) == len(active_italy_trip.intercity_transfers)


def test_budget_recalculation_on_cheaper_alternative(copilot_engine, active_italy_trip):
    """Scenario 4: Request a cheaper alternative; verify the updated budget."""
    orig_total = active_italy_trip.total_budget_per_person
    orig_day2_sub = active_italy_trip.days[1].daily_budget_subtotal

    res = copilot_engine.process_message(
        "Find a cheaper restaurant for Day 2 dinner to cut budget",
        active_trip=active_italy_trip,
        selected_day=2,
    )

    assert res["intent"] == "modification"
    mod_trip = CanonicalTripState.model_validate(res["modified_trip"])
    new_day2_sub = mod_trip.days[1].daily_budget_subtotal
    new_total = mod_trip.total_budget_per_person

    # Budget must decrease deterministically
    assert new_day2_sub < orig_day2_sub
    assert new_total < orig_total
    transfer_sum = sum((t.estimated_cost.amount if t.estimated_cost else 0.0) for t in mod_trip.intercity_transfers)
    assert round(sum(d.daily_budget_subtotal for d in mod_trip.days) + transfer_sum, 2) == round(new_total, 2)


def test_relax_pacing_less_walking(copilot_engine, active_italy_trip):
    """Scenario 5: Request less walking / relaxed pace; verify revised schedule."""
    res = copilot_engine.process_message(
        "Relax pace on Day 3 and reduce walking",
        active_trip=active_italy_trip,
        selected_day=3,
    )

    assert res["intent"] == "modification"
    mod_trip = CanonicalTripState.model_validate(res["modified_trip"])
    day3 = mod_trip.days[2]
    assert "minimal walking" in day3.transit_overview.lower() or "relaxed" in day3.transit_overview.lower()


def test_weather_adaptation_rainy_day(copilot_engine, active_italy_trip):
    """Scenario 6: Adaptive replanning for bad weather."""
    res = copilot_engine.process_message(
        "It looks like rain on Day 2, find indoor alternative",
        active_trip=active_italy_trip,
        selected_day=2,
    )

    assert res["intent"] == "modification"
    mod_trip = CanonicalTripState.model_validate(res["modified_trip"])
    day2 = mod_trip.days[1]
    museum_acts = [a for a in day2.activities if "museum" in a.title.lower() or "gallery" in a.title.lower()]
    assert len(museum_acts) > 0


def test_cross_trip_context_isolation(copilot_engine, active_italy_trip, active_japan_trip):
    """Scenario 7: Switch between Italy and Japan; verify that Copilot uses the correct active trip without leaking."""
    res_italy = copilot_engine.process_message("What city are we in on Day 1?", active_trip=active_italy_trip, selected_day=1)
    assert "Rome" in res_italy["reply"]
    assert "Tokyo" not in res_italy["reply"]

    res_japan = copilot_engine.process_message("What city are we in on Day 1?", active_trip=active_japan_trip, selected_day=1)
    assert "Tokyo" in res_japan["reply"]
    assert "Rome" not in res_japan["reply"]
