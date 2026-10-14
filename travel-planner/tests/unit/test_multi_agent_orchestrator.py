"""Unit tests for the Multi-Agent Travel Orchestrator and Canonical Trip State."""

import pytest
from app.multi_agent.orchestrator import MultiAgentTravelOrchestrator
from app.multi_agent.verification_agent import PlacesAndFoodVerificationAgent
from app.multi_agent.logistics_agent import TransportationAndLogisticsAgent
from app.multi_agent.qa_agent import QualityAssuranceAndConsistencyAgent
from app.trip_models import CanonicalTripState


def test_multi_agent_italy_7day_orchestration():
    orchestrator = MultiAgentTravelOrchestrator()
    prompt = (
        "I'm visiting Italy for 7 days. I love authentic Italian cuisine, historic landmarks, "
        "scenic streets, and hidden local gems. Create a realistic day-by-day itinerary covering "
        "Rome, Florence, and Venice. Include authentic local restaurants, must-visit attractions, "
        "Google Maps links, transportation between cities, the best times to visit attractions, "
        "weather information where available, and an estimated daily and total budget."
    )
    trip: CanonicalTripState = orchestrator.build_canonical_trip(prompt)

    # 1. Verification of Duration and Destination
    assert trip.duration_days == 7
    assert len(trip.days) == 7
    assert "Rome" in trip.destination or "Italy" in trip.destination
    assert trip.currency == "EUR"

    # 2. Check City Progression: Rome (Days 1-3), Florence (Days 4-5), Venice (Days 6-7)
    cities = [d.city for d in trip.days]
    assert cities[0] == "Rome"
    assert cities[1] == "Rome"
    assert cities[2] == "Rome"
    assert cities[3] == "Florence"
    assert cities[4] == "Florence"
    assert cities[5] == "Venice"
    assert cities[6] == "Venice"

    # 3. Check Intercity Transfers
    assert len(trip.intercity_transfers) >= 2
    transfer_1 = trip.intercity_transfers[0]
    assert transfer_1.from_city == "Rome"
    assert transfer_1.to_city == "Florence"
    assert transfer_1.day == 4
    assert transfer_1.duration_minutes == 95
    assert "Frecciarossa" in transfer_1.mode
    assert transfer_1.verification.status == "verified"

    transfer_2 = trip.intercity_transfers[1]
    assert transfer_2.from_city == "Florence"
    assert transfer_2.to_city == "Venice"
    assert transfer_2.day == 6
    assert transfer_2.duration_minutes == 125

    # 4. Check Activity Integrity and Working URLs
    for day in trip.days:
        assert len(day.activities) == 4
        slots = [a.slot for a in day.activities]
        assert slots == ["Morning", "Lunch", "Afternoon", "Evening"]
        for act in day.activities:
            assert act.google_maps_url.startswith("https://www.google.com/maps/search/?api=1&query=")
            assert act.directions_url.startswith("https://www.google.com/maps/dir/?api=1&destination=")
            assert act.estimated_cost is not None
            assert act.estimated_cost.currency == "EUR"

    # 5. Check Feasibility Report
    report = trip.feasibility_report
    assert report.overall_score >= 80
    assert report.verification_rate >= 70.0
    assert report.schedule_conflicts == 0
    assert report.pacing_rating in ["Optimal", "Relaxed"]
    assert report.verified_places_count > 15


def test_verification_agent_url_generation():
    v = PlacesAndFoodVerificationAgent()
    act = v.verify_place(
        name="Uffizi Gallery",
        city="Florence",
        category="Art Museum",
        slot="Afternoon",
        cost_amount=25.0,
        currency="EUR",
        is_cost_verified=True,
        origin_name="Trattoria Mario",
    )
    assert act.title == "Uffizi Gallery"
    assert "Uffizi" in act.google_maps_url
    assert "origin=Trattoria%20Mario" in act.directions_url
    assert act.verification.status == "verified"
    assert act.coordinates.lat == 43.7677
    assert act.coordinates.lng == 11.2553


def test_logistics_agent_rail_corridors():
    l = TransportationAndLogisticsAgent()
    t = l.plan_intercity_transfer("Rome", "Florence", day=4)
    assert t.duration_minutes == 95
    assert t.departure_station == "Roma Termini"
    assert t.arrival_station == "Firenze Santa Maria Novella (SMN)"
    assert t.verification.status == "verified"
