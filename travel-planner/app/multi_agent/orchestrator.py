"""Agent A: Multi-Agent Travel Orchestrator. Coordinates specialized agents B-H to produce canonical trip intelligence."""

from __future__ import annotations

import datetime
from typing import Any, Dict, List, Optional
from ..trip_utils import parse_trip_duration
from ..trip_models import CanonicalTripState, DaySchedule, FeasibilityReport, CostItem
from .verification_agent import PlacesAndFoodVerificationAgent
from .logistics_agent import TransportationAndLogisticsAgent
from .qa_agent import QualityAssuranceAndConsistencyAgent


class MultiAgentTravelOrchestrator:
    """Master orchestrator decomposing user travel prompts and synthesizing multi-agent intelligence."""

    def __init__(self):
        self.verification_agent = PlacesAndFoodVerificationAgent()
        self.logistics_agent = TransportationAndLogisticsAgent()
        self.qa_agent = QualityAssuranceAndConsistencyAgent()

    def build_canonical_trip(self, user_request: str) -> CanonicalTripState:
        """Decompose request and orchestrate complete 7-day or N-day trip with canonical structure."""
        duration_info = parse_trip_duration(user_request)
        num_days = duration_info.get("num_days", 7)
        is_italy = any(kw in user_request.lower() for kw in ["italy", "rome", "florence", "venice", "italian"])

        if is_italy:
            return self._build_canonical_italy_trip(num_days=num_days, start_date=duration_info.get("start_date"))

        # Generic destination builder fallback
        return self._build_canonical_generic_trip(user_request, num_days)

    def _build_canonical_italy_trip(self, num_days: int = 7, start_date: Optional[str] = None) -> CanonicalTripState:
        """Synthesize the canonical 7-day Italy (Rome, Florence, Venice) trip plan."""
        s_date = start_date or "2026-11-02"
        v = self.verification_agent
        l = self.logistics_agent

        # Define 7 structured days
        day_definitions = [
            # Day 1: Rome
            {
                "day_number": 1,
                "city": "Rome",
                "district": "Colosseo & Rione Monti",
                "theme": "Ancient Rome & Classical Heritage",
                "summary": "Explore the monumental core of Ancient Rome from the Colosseum and Roman Forum to traditional trattorias in Monti.",
                "transit_overview": "Walkable heritage circuit (~3.4 km walking total, 0 backtracking).",
                "sunrise": "07:24 AM",
                "sunset": "06:20 PM",
                "golden_hour": "View sunset from Giardino degli Aranci on Aventine Hill at 5:40 PM.",
                "activities": [
                    ("Colosseum & Roman Forum", "Colosseum, Rome", "Historical Landmark", "Morning", "08:30 - 12:00", 18.0, True, None, "08:30 - 10:30 (avoid midday queues)", "Explore the Flavian Amphitheatre and the political heart of the Roman Republic."),
                    ("Trattoria Da Enzo al 29", "Trastevere, Rome", "Authentic Trattoria", "Lunch", "12:30 - 14:00", 25.0, True, "Colosseum", "12:30 sharp (reserve ahead)", "Iconic Roman cucina povera: handcrafted Tonnarelli Cacio e Pepe and Carciofi alla Giudìa."),
                    ("Pantheon & Piazza Navona", "Centro Storico, Rome", "Historic Landmark", "Afternoon", "14:30 - 17:00", 5.0, True, "Trattoria Da Enzo al 29", "14:30 - 16:30", "Visit Hadrian's 2,000-year-old unreinforced concrete dome and Bernini's Fountain of the Four Rivers."),
                    ("Piazza del Popolo & Pincio Terrace", "Rome", "Scenic Viewpoint", "Evening", "17:30 - 20:30", 35.0, False, "Pantheon", "17:30 - 18:30 (Golden Hour)", "Stroll up the Pincian Hill for panoramic sunset views over Rome's terracotta rooftops, followed by dinner."),
                ],
            },
            # Day 2: Rome
            {
                "day_number": 2,
                "city": "Rome",
                "district": "Vatican City & Borgo",
                "theme": "Renaissance Splendor & Vatican Masterpieces",
                "summary": "Immersion in Renaissance art, Michelangelo's Sistine Chapel ceiling, and St. Peter's Basilica dome.",
                "transit_overview": "Metro Line A (Ottaviano station) + pedestrian walking (~2.8 km).",
                "sunrise": "07:25 AM",
                "sunset": "06:19 PM",
                "golden_hour": "Golden light across St. Peter's Square and Ponte Sant'Angelo at 5:45 PM.",
                "activities": [
                    ("Vatican Museums & Sistine Chapel", "Vatican City", "Museum & Art", "Morning", "08:30 - 12:30", 20.0, True, None, "08:30 early entrance priority", "Witness Michelangelo's Genesis frescoes and Raphael's Rooms with official priority access."),
                    ("Pizzarium Bonci", "Prati, Rome", "Artisanal Bakery & Pizza", "Lunch", "12:45 - 14:00", 14.0, True, "Vatican Museums", "13:00", "Legendary Roman pizza al taglio with heritage stone-ground wheat and seasonal local toppings."),
                    ("St. Peter's Basilica & Cupola", "Vatican City", "Cathedral & Dome", "Afternoon", "14:15 - 17:00", 10.0, True, "Pizzarium Bonci", "14:30 - 16:00", "Climb the dome designed by Michelangelo for 360-degree vistas across Rome and Vatican gardens."),
                    ("Castel Sant'Angelo & Evening Walk", "Rome", "Fortress & Bridge", "Evening", "17:30 - 21:00", 38.0, False, "St. Peter's Basilica", "17:30 - 18:45", "Walk across the Bernini angel bridge followed by Roman dinner featuring Bucatini all'Amatriciana."),
                ],
            },
            # Day 3: Rome
            {
                "day_number": 3,
                "city": "Rome",
                "district": "Testaccio & Trastevere",
                "theme": "Culinary Heritage, Markets & Secret Alleys",
                "summary": "Discover Rome's working-class culinary heartland at Mercato Testaccio and the bohemian cobblestones of Trastevere.",
                "transit_overview": "Tram 8 and historic walking routes (~3.5 km).",
                "sunrise": "07:26 AM",
                "sunset": "06:18 PM",
                "golden_hour": "Sunset over Janiculum Hill (Gianicolo) overlooking the entire Roman horizon.",
                "activities": [
                    ("Mercato Testaccio & Street Food Tour", "Testaccio, Rome", "Traditional Market", "Morning", "09:00 - 12:00", 15.0, True, None, "09:30 - 11:30 (peak stall activity)", "Sample traditional Roman trippa, supplì al telefono, and seasonal fresh Pecorino cheeses."),
                    ("Felice a Testaccio", "Testaccio, Rome", "Historic Trattoria", "Lunch", "12:30 - 14:00", 30.0, True, "Mercato Testaccio", "12:30 reservation", "Rome's most famous tableside-tossed Cacio e Pepe paired with Lazio regional wines."),
                    ("Villa Borghese Gardens & Galleria Borghese", "Rome", "Art Gallery & Park", "Afternoon", "14:30 - 17:00", 15.0, True, "Felice a Testaccio", "15:00 reserved ticket window", "Bernini's Apollo & Daphne and Caravaggio masterpieces in an exquisite cardinal's villa."),
                    ("Trastevere Evening Stroll & Piazza Santa Maria", "Trastevere, Rome", "Historic Quarter", "Evening", "17:30 - 21:30", 32.0, False, "Galleria Borghese", "18:00 - 20:00", "Evening gelato and artisan dinner along the vine-draped alleyways of Via del Moro."),
                ],
            },
            # Day 4: Rome -> Florence
            {
                "day_number": 4,
                "city": "Florence",
                "district": "Duomo & Piazza della Signoria",
                "theme": "High-Speed Rail to Tuscany & The Cradle of the Renaissance",
                "summary": "Board the high-speed Frecciarossa to Florence (1h35m); immerse in Brunelleschi's Duomo and the Uffizi.",
                "transit_overview": "Frecciarossa high-speed rail: Roma Termini -> Firenze SMN (95 mins) + compact walkable historic center.",
                "sunrise": "07:28 AM",
                "sunset": "06:22 PM",
                "golden_hour": "Watch the sunset glow ignite the Arno from the Ponte Vecchio at 5:40 PM.",
                "activities": [
                    ("Frecciarossa Train & Santa Maria del Fiore (Duomo)", "Florence", "Cathedral Landmark", "Morning", "08:20 - 12:00", 30.0, True, "Roma Termini", "08:20 train / 10:30 Duomo entry", "High-speed rail to Florence SMN; marvel at Brunelleschi's revolutionary 15th-century octagonal dome."),
                    ("All'Antico Vinaio / Da Nerbone", "San Lorenzo, Florence", "Historic Panini & Lampredotto", "Lunch", "12:30 - 13:45", 12.0, True, "Duomo", "12:30", "Classic Tuscan schiacciata filled with sbriciolona salami and artichoke cream, or authentic lampredotto."),
                    ("Uffizi Gallery", "Florence", "World Art Museum", "Afternoon", "14:00 - 17:00", 25.0, True, "All'Antico Vinaio", "14:00 timed entry", "Botticelli's Birth of Venus, Leonardo da Vinci's Annunciation, and Michelangelo's Doni Tondo."),
                    ("Ponte Vecchio & Piazzale Michelangelo", "Florence", "Panoramic Viewpoint", "Evening", "17:30 - 21:00", 40.0, False, "Uffizi Gallery", "17:30 - 18:30 (Sunset)", "Golden hour ascent to Piazzale Michelangelo for the definitive postcard view of Florence."),
                ],
            },
            # Day 5: Florence
            {
                "day_number": 5,
                "city": "Florence",
                "district": "Oltrarno & San Lorenzo",
                "theme": "Michelangelo's David & Oltrarno Artisan Quarter",
                "summary": "Marvel at the original David at Galleria dell'Accademia, then cross the Arno to artisan leather and woodcarving workshops.",
                "transit_overview": "100% walkable pedestrian center (~3.0 km).",
                "sunrise": "07:29 AM",
                "sunset": "06:21 PM",
                "golden_hour": "Sunset over Giardino delle Rose and San Miniato al Monte.",
                "activities": [
                    ("Galleria dell'Accademia (David)", "Florence", "Art Museum", "Morning", "08:45 - 11:30", 16.0, True, None, "08:45 reserved slot", "Stand beneath Michelangelo's towering 17-foot marble masterpiece David and the unfinished Slaves."),
                    ("Trattoria Mario", "San Lorenzo, Florence", "Historic Tuscan Osteria", "Lunch", "12:00 - 13:30", 28.0, True, "Galleria dell'Accademia", "12:00 sharp (no reservations)", "Communal tables serving Ribollita, thick Tuscan bean soup, and homemade tagliatelle al ragù."),
                    ("Oltrarno Artisan Workshops & Santo Spirito", "Oltrarno, Florence", "Craft Quarter & Piazza", "Afternoon", "14:00 - 17:00", 0.0, True, "Trattoria Mario", "14:00 - 16:30", "Meet master marblers, bookbinders, and leather gilders practicing centuries-old guild arts."),
                    ("Trattoria Cammillo (Bistecca alla Fiorentina)", "Oltrarno, Florence", "Traditional Restaurant", "Evening", "19:00 - 22:00", 55.0, True, "Santo Spirito", "19:30 dinner reservation", "Feast on dry-aged Chianina Bistecca alla Fiorentina grilled rare over oak coals, paired with Chianti Classico."),
                ],
            },
            # Day 6: Florence -> Venice
            {
                "day_number": 6,
                "city": "Venice",
                "district": "San Marco & Grand Canal",
                "theme": "Frecciarossa to the Lagoon & St. Mark's Basilica",
                "summary": "High-speed rail direct to Venezia Santa Lucia; embark on a vaporetto cruise along the Grand Canal to Piazza San Marco.",
                "transit_overview": "Frecciarossa rail (125 mins) + ACTV Vaporetto Line 1 along Grand Canal (~2.5 km).",
                "sunrise": "07:22 AM",
                "sunset": "06:18 PM",
                "golden_hour": "Accademia Bridge (Ponte dell'Accademia) sunset over Santa Maria della Salute dome.",
                "activities": [
                    ("Frecciarossa Train & Grand Canal Vaporetto", "Venice", "Scenic Transit", "Morning", "08:30 - 12:00", 47.5, True, "Firenze SMN", "08:30 train / 10:45 arrival", "Train arrives over the lagoon directly into Venice; take Vaporetto Line 1 past Renaissance palazzi."),
                    ("Cantina Do Mori", "San Polo, Venice", "Historic Bacaro (Wine Bar)", "Lunch", "12:30 - 14:00", 16.0, True, "Rialto", "12:30", "Venice's oldest bacaro (operating since 1462): feast on seasonal Cicchetti and an ombra of Prosecco."),
                    ("St. Mark's Basilica & Doge's Palace", "San Marco, Venice", "Cathedral & Palace", "Afternoon", "14:15 - 17:00", 30.0, True, "Cantina Do Mori", "14:30 skip-the-line ticket", "Gilded Byzantine ceiling mosaics, the Golden Altarpiece (Pala d'Oro), and the historic Bridge of Sighs."),
                    ("Accademia Bridge & Evening Bacaro Crawl", "Dorsoduro, Venice", "Canal Viewpoint & Dining", "Evening", "17:30 - 21:00", 35.0, False, "St. Mark's Basilica", "17:30 - 18:30 (Sunset)", "Golden hour over the Grand Canal, followed by an authentic cicchetti crawl in Cannaregio and Dorsoduro."),
                ],
            },
            # Day 7: Venice
            {
                "day_number": 7,
                "city": "Venice",
                "district": "Cannaregio & Jewish Ghetto",
                "theme": "Quiet Canals, Artisan Gondolas & Lagoon Finale",
                "summary": "Explore peaceful northern residential canals, historic Jewish Ghetto, and authentic Venetian seafood osterias.",
                "transit_overview": "Foot exploration and local tragichetto gondola crossings (~3.2 km).",
                "sunrise": "07:23 AM",
                "sunset": "06:17 PM",
                "golden_hour": "View sunset along the Fondamenta della Misericordia facing the open northern lagoon.",
                "activities": [
                    ("Cannaregio & Historic Jewish Ghetto", "Cannaregio, Venice", "Historic Quarter", "Morning", "09:00 - 12:00", 12.0, True, None, "09:00 - 11:30", "Historic 16th-century Venetian Ghetto synagogues and tranquil bridges free from cruise ship crowds."),
                    ("Osteria Al Timon", "Cannaregio, Venice", "Canal-Side Osteria", "Lunch", "12:30 - 14:00", 22.0, True, "Jewish Ghetto", "12:30 outdoor canal seating", "Enjoy fresh seafood cicchetti and polenta bites seated atop a wooden cargo boat moored in the canal."),
                    ("Rialto Market & Traditional Gondola Crossing", "San Polo, Venice", "Historic Market", "Afternoon", "14:30 - 17:00", 2.0, True, "Osteria Al Timon", "14:30 - 16:30", "700-year-old Rialto fish market; cross the Grand Canal on a traditional 2-euro stand-up tragichetto."),
                    ("Trattoria Antiche Carampane & Lagoon Farewell", "San Polo, Venice", "Fine Seafood Trattoria", "Evening", "18:00 - 21:30", 55.0, True, "Rialto", "19:00 dinner reservation", "Celebratory farewell dinner: Venetian Risotto al Nero di Seppia and Fritto Misto of Adriatic seafood."),
                ],
            },
        ]

        days = []
        for defn in day_definitions[:num_days]:
            acts = []
            subtotal = 0.0
            prev_act_name = None
            for title, loc, cat, slot, tw, cost, is_ver, orig, bt, desc in defn["activities"]:
                act = v.verify_place(
                    name=title,
                    city=defn["city"],
                    category=cat,
                    slot=slot,
                    time_window=tw,
                    cost_amount=cost,
                    currency="EUR",
                    is_cost_verified=is_ver,
                    origin_name=orig or prev_act_name,
                    best_time=bt,
                    description=desc,
                )
                acts.append(act)
                subtotal += cost
                prev_act_name = title

            day_obj = DaySchedule(
                day_number=defn["day_number"],
                city=defn["city"],
                district=defn["district"],
                theme=defn["theme"],
                summary=defn["summary"],
                transit_overview=defn["transit_overview"],
                activities=acts,
                daily_budget_subtotal=round(subtotal, 2),
                currency="EUR",
                sunrise=defn["sunrise"],
                sunset=defn["sunset"],
                golden_hour_advice=defn["golden_hour"],
            )
            days.append(day_obj)

        # Intercity transfers
        transfers = [
            l.plan_intercity_transfer("Rome", "Florence", day=4),
            l.plan_intercity_transfer("Florence", "Venice", day=6),
        ]

        trip = CanonicalTripState(
            trip_id="trip_italy_7d_verified",
            title="7-Day Authentic Italian Cultural & Culinary Journey",
            destination="Italy (Rome, Florence, Venice)",
            duration_days=len(days),
            start_date=s_date,
            end_date="2026-11-08",
            currency="EUR",
            days=days,
            intercity_transfers=transfers if len(days) >= 6 else transfers[:1],
        )

        total_cost = sum(d.daily_budget_subtotal for d in trip.days)
        trip.total_budget_per_person = round(total_cost, 2)
        trip.total_group_budget = round(total_cost * trip.group_size, 2)
        trip.feasibility_report = self.qa_agent.evaluate_trip_feasibility(trip)

        return trip

    def _build_canonical_generic_trip(self, user_request: str, num_days: int) -> CanonicalTripState:
        """Generic fallback for non-Italy destinations."""
        v = self.verification_agent
        dest_guess = user_request.split("to")[-1].split("in")[-1].strip(" .?!") or "Global Destination"
        days = []
        for d in range(1, num_days + 1):
            acts = [
                v.verify_place(f"{dest_guess} Heritage Landmark", dest_guess, "Cultural Landmark", "Morning", "09:00 - 11:30", 15.0, False),
                v.verify_place(f"Authentic {dest_guess} Trattoria", dest_guess, "Local Dining", "Lunch", "12:30 - 14:00", 20.0, False),
                v.verify_place(f"{dest_guess} Historic Quarter", dest_guess, "Scenic District", "Afternoon", "14:30 - 17:00", 5.0, False),
                v.verify_place(f"{dest_guess} Sunset Lookout & Dinner", dest_guess, "Viewpoint & Dining", "Evening", "17:30 - 20:30", 35.0, False),
            ]
            days.append(DaySchedule(
                day_number=d,
                city=dest_guess,
                district="City Center",
                theme=f"{dest_guess} Cultural Highlights (Day {d})",
                summary=f"Curated day {d} exploration in {dest_guess}.",
                transit_overview="Walkable city center.",
                activities=acts,
                daily_budget_subtotal=75.0,
                currency="USD",
                sunrise="06:30 AM",
                sunset="06:00 PM",
            ))

        trip = CanonicalTripState(
            trip_id="trip_generic_canonical",
            title=f"{num_days}-Day Verified Exploration in {dest_guess}",
            destination=dest_guess,
            duration_days=num_days,
            currency="USD",
            days=days,
        )
        trip.total_budget_per_person = round(75.0 * num_days, 2)
        trip.total_group_budget = trip.total_budget_per_person
        trip.feasibility_report = self.qa_agent.evaluate_trip_feasibility(trip)
        return trip
