"""Unit tests for Phase 3: Multi-Agent Travel Orchestration, Intelligence, and Verification."""

import pytest
from app.multi_agent.orchestrator import MultiAgentTravelOrchestrator
from app.multi_agent.verification_agent import PlacesAndFoodVerificationAgent
from app.multi_agent.logistics_agent import TransportationAndLogisticsAgent
from app.multi_agent.qa_agent import QualityAssuranceAndConsistencyAgent
from app.trip_models import CanonicalTripState
from app.trip_validator import validate_canonical_trip


def test_phase3_italy_seven_days_master_prompt():
    """Verify master prompt for Italy produces a realistic, validated, 7-day schedule covering Rome, Florence, and Venice."""
    orchestrator = MultiAgentTravelOrchestrator()
    prompt = (
        "I'm visiting Italy for 7 days. I love authentic Italian cuisine, historic landmarks, "
        "scenic streets, and hidden local gems. Create a realistic day-by-day itinerary covering "
        "Rome, Florence, and Venice. Include authentic local restaurants, Google Maps links, "
        "transportation between cities, suitable visiting times, weather information where available, "
        "and an estimated daily and total budget."
    )
    trip: CanonicalTripState = orchestrator.build_canonical_trip(prompt)

    # 1. 7 days present and matched to cities
    assert trip.duration_days == 7
    assert len(trip.days) == 7
    cities = [d.city for d in trip.days]
    assert cities[0:3] == ["Rome", "Rome", "Rome"]
    assert cities[3:5] == ["Florence", "Florence"]
    assert cities[5:7] == ["Venice", "Venice"]

    # 2. Intercity transfers present and verified
    assert len(trip.intercity_transfers) >= 2
    trans_rf = trip.intercity_transfers[0]
    assert trans_rf.from_city == "Rome" and trans_rf.to_city == "Florence"
    assert trans_rf.verification.status == "verified"
    trans_fv = trip.intercity_transfers[1]
    assert trans_fv.from_city == "Florence" and trans_fv.to_city == "Venice"
    assert trans_fv.verification.status == "verified"

    # 3. Budget consistency
    subtotals = sum(d.daily_budget_subtotal for d in trip.days)
    transfers = sum(t.estimated_cost.amount for t in trip.intercity_transfers)
    assert abs(trip.total_budget_per_person - (subtotals + transfers)) < 0.05

    # 4. Deterministic trip validator acceptance
    val = validate_canonical_trip(trip, expected_destination="Italy", expected_days=7)
    assert val.is_valid, f"Validation failed: {val.errors}"
    assert val.verified_activities_count > 15


def test_phase3_japan_multi_agent_workflow():
    """Verify Japan prompt produces valid Tokyo/Kyoto itinerary with Shinkansen transfer."""
    orchestrator = MultiAgentTravelOrchestrator()
    prompt = "Plan a 7-day trip to Japan covering Tokyo and Kyoto with authentic food and temples."
    trip: CanonicalTripState = orchestrator.build_canonical_trip(prompt)

    assert trip.duration_days == 7
    assert len(trip.days) == 7
    assert "Japan" in trip.destination or "Tokyo" in trip.destination

    cities = [d.city for d in trip.days]
    assert "Tokyo" in cities
    assert "Kyoto" in cities

    # Shinkansen transfer
    assert len(trip.intercity_transfers) >= 1
    t = trip.intercity_transfers[0]
    assert t.from_city == "Tokyo" and t.to_city == "Kyoto"
    assert "Shinkansen" in t.mode

    val = validate_canonical_trip(trip, expected_destination="Japan", expected_days=7)
    assert val.is_valid, f"Validation failed: {val.errors}"


def test_phase3_kerala_multi_agent_workflow():
    """Verify Kerala prompt produces authentic Kochi, Alleppey, and Munnar days with local rail/road corridors."""
    orchestrator = MultiAgentTravelOrchestrator()
    prompt = "Plan a 5-day trip to Kerala covering Kochi, Alleppey, and Munnar with authentic backwaters and Malabar cuisine."
    trip: CanonicalTripState = orchestrator.build_canonical_trip(prompt)

    assert trip.duration_days == 5
    assert len(trip.days) == 5
    assert "Kerala" in trip.destination or "Kochi" in trip.destination

    cities = [d.city for d in trip.days]
    assert "Kochi" in cities
    assert "Alleppey" in cities
    assert "Munnar" in cities

    # Backwaters & hill transfers
    assert len(trip.intercity_transfers) >= 2

    val = validate_canonical_trip(trip, expected_destination="Kerala", expected_days=5)
    assert val.is_valid, f"Validation failed: {val.errors}"


def test_phase3_geographic_proximity_haversine():
    """Verify Haversine distance calculation and intra-city geographic feasibility checks."""
    l = TransportationAndLogisticsAgent()
    # Rome Colosseum (41.8902, 12.4922) to Pantheon (41.8986, 12.4769) is ~1.5 - 2 km
    dist_km = l.calculate_haversine_distance_km(41.8902, 12.4922, 41.8986, 12.4769)
    assert 1.0 <= dist_km <= 3.0

    # Tokyo (35.6762, 139.6503) to Kyoto (35.0116, 135.7681) is ~370 km direct line
    dist_tokyo_kyoto = l.calculate_haversine_distance_km(35.6762, 139.6503, 35.0116, 135.7681)
    assert 350.0 <= dist_tokyo_kyoto <= 400.0


def test_phase3_tool_failure_safe_degradation():
    """Verify graceful fallback and safe handling when API keys are absent or network is degraded."""
    v = PlacesAndFoodVerificationAgent(api_key="NON_EXISTENT_KEY")
    acts = v.search_live_experiences("Atlantis", max_results=3)
    assert isinstance(acts, list)

    dining = v.search_live_dining("Atlantis", max_results=3)
    assert isinstance(dining, list)

    act = v.verify_place("Sample Landmark", "Atlantis", "Landmark", is_cost_verified=False)
    assert act.title == "Sample Landmark"
    assert act.verification.status == "partially_verified"
