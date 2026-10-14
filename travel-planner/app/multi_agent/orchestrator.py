"""Agent A: Multi-Agent Travel Orchestrator. Coordinates specialized agents B-H to produce canonical trip intelligence."""

from __future__ import annotations

import datetime
import re
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
        is_japan = any(kw in user_request.lower() for kw in ["japan", "tokyo", "kyoto", "osaka", "japanese"])
        is_kerala = any(kw in user_request.lower() for kw in ["kerala", "kochi", "cochin", "alleppey", "munnar"])

        start_date = duration_info.get("start_date") or "2026-11-02"

        if is_italy:
            return self._build_canonical_italy_trip(num_days=num_days, start_date=start_date)
        if is_japan:
            return self._build_canonical_japan_trip(num_days=num_days, start_date=start_date)
        if is_kerala:
            return self._build_canonical_kerala_trip(num_days=num_days, start_date=start_date)

        # Dynamic destination builder with live Places API / culinary discovery
        return self._build_canonical_dynamic_trip(user_request, num_days, start_date=start_date)

    def _build_canonical_japan_trip(self, num_days: int = 7, start_date: Optional[str] = None) -> CanonicalTripState:
        """Synthesize canonical Japan (Tokyo & Kyoto) trip plan with verified Shinkansen and authentic dining."""
        s_date = start_date or "2026-11-02"
        v = self.verification_agent
        l = self.logistics_agent

        # Tokyo days (1 to 4), Kyoto days (5 to 7)
        tokyo_days = min(num_days, 4)
        kyoto_days = max(0, num_days - tokyo_days)

        day_defs = [
            {
                "day_number": 1,
                "city": "Tokyo",
                "district": "Asakusa & Ueno",
                "theme": "Historic Shitamachi & Ancient Temples",
                "summary": "Walk the ancient approach to Senso-ji, sample street snacks along Nakamise-dori, and explore traditional craft lanes.",
                "transit_overview": "Ginza Line Subway and pedestrian streets (~3.2 km).",
                "sunrise": "06:05 AM",
                "sunset": "04:45 PM",
                "golden_hour": "Sunset along the Sumida River promenade facing Tokyo Skytree.",
                "activities": [
                    ("Senso-ji Temple & Kaminarimon", "Asakusa, Tokyo", "Historic Temple", "Morning", "08:30 - 11:30", 0.0, True, None, "08:30 (avoid midday crowds)", "Tokyo's oldest temple founded in 645 AD; pass beneath the massive red Kaminarimon lantern."),
                    ("Namiki Yabusoba", "Asakusa, Tokyo", "Historic Soba Restaurant", "Lunch", "12:00 - 13:30", 18.0, True, "Senso-ji Temple", "12:00 lunch window", "Century-old Edo soba specialist serving handmade buckwheat noodles with concentrated dipping tsuyu."),
                    ("Ueno Park & Tokyo National Museum", "Taito, Tokyo", "Art & National Heritage", "Afternoon", "14:00 - 17:00", 6.5, True, "Namiki Yabusoba", "14:15 admission", "Japan's oldest national museum housing samurai armor, ancient ceramics, and National Treasures."),
                    ("Omoide Yokocho Yakitori Alleys", "Shinjuku, Tokyo", "Atmospheric Dining Alley", "Evening", "18:00 - 21:00", 35.0, False, "Ueno Park", "18:30 dinner", "Charcoal-grilled yakitori skewers over binchotan in lantern-lit postwar alleyways."),
                ],
            },
            {
                "day_number": 2,
                "city": "Tokyo",
                "district": "Tsukiji & Ginza",
                "theme": "Edomae Culinary Heritage & Modern Architecture",
                "summary": "Explore Tsukiji Outer Market seafood stalls followed by the historic tea gardens of Hamarikyu.",
                "transit_overview": "Oedo Line & Hibiya Line subway routes (~2.5 km).",
                "sunrise": "06:06 AM",
                "sunset": "04:44 PM",
                "golden_hour": "Hamarikyu Gardens reflection pond against the Shiodome skyline.",
                "activities": [
                    ("Tsukiji Outer Market Tasting Walk", "Chuo, Tokyo", "Historic Market", "Morning", "08:00 - 11:00", 25.0, True, None, "08:30 morning market hours", "Sample fresh tamagoyaki, grilled scallops, and fresh Edomae nigiri sushi from multi-generation purveyors."),
                    ("Sushi Daiwa / Tsukiji Sushiko", "Tsukiji, Tokyo", "Authentic Sushi-ya", "Lunch", "11:30 - 13:00", 35.0, True, "Tsukiji Outer Market", "11:30 counter seating", "Seasonal nigiri prepared with red-vinegared sushi rice and pristine morning fish."),
                    ("Hamarikyu Gardens & Matcha Teahouse", "Chuo, Tokyo", "Edo-Period Garden", "Afternoon", "13:30 - 16:00", 3.0, True, "Tsukiji Market", "14:00 tea service", "Historic Tokugawa shogun duck hunting garden featuring a tidal pond and wooden teahouse over the water."),
                    ("Tsukishima Monja Street", "Chuo, Tokyo", "Local Culinary Street", "Evening", "17:30 - 20:30", 28.0, True, "Hamarikyu Gardens", "18:00 dinner", "Cook savory monjayaki batter on a tabletop teppan grill with cabbage, mentaiko, and mochi."),
                ],
            },
            {
                "day_number": 3,
                "city": "Tokyo",
                "district": "Meiji Jingu & Shibuya",
                "theme": "Sacred Cedar Forest & Electric City Scramble",
                "summary": "Morning reflection under towering cryptomeria trees at Meiji Shrine, progressing into modern Shibuya culture.",
                "transit_overview": "JR Yamanote Line pedestrian circuit (~3.8 km).",
                "sunrise": "06:07 AM",
                "sunset": "04:43 PM",
                "golden_hour": "Shibuya Sky observation deck at 4:30 PM for sunset over Mount Fuji.",
                "activities": [
                    ("Meiji Jingu Shrine", "Shibuya, Tokyo", "Shinto Shrine", "Morning", "08:30 - 11:30", 0.0, True, None, "08:30 quiet morning light", "Pass through towering 1,500-year-old Taiwanese cypress Torii gates into a tranquil 170-acre evergreen forest."),
                    ("Tonkatsu Maisen Aoyama", "Shibuya, Tokyo", "Specialty Cutlet Restaurant", "Lunch", "12:00 - 13:30", 22.0, True, "Meiji Jingu", "12:00 early seating", "Housed in a former 1930s public bathhouse; feast on tender Kurobuta pork panko-crusted cutlets."),
                    ("Nezu Museum & Japanese Iris Garden", "Minato, Tokyo", "Art Museum & Garden", "Afternoon", "14:00 - 16:30", 9.0, True, "Tonkatsu Maisen", "14:15 admission", "Pre-modern Japanese and East Asian art collection set beside an authentic moss-covered stroll garden."),
                    ("Shibuya Scramble & Izakaya Crawl", "Shibuya, Tokyo", "Scenic Urban Quarter", "Evening", "17:00 - 21:00", 38.0, False, "Nezu Museum", "17:30 twilight", "Experience the world's busiest pedestrian intersection followed by local sashimi and draft beer at Nonbei Yokocho."),
                ],
            },
            {
                "day_number": 4,
                "city": "Tokyo",
                "district": "Yanaka Shitamachi & Ueno",
                "theme": "Old Edo Nostalgia & Artisan Tea Culture",
                "summary": "Wander the pre-war alleys of Yanaka, visit historic wooden temples, and enjoy traditional craft shops.",
                "transit_overview": "Pedestrian stroll (~3.0 km).",
                "sunrise": "06:08 AM",
                "sunset": "04:42 PM",
                "golden_hour": "Sunset from Yanaka's Yuyake Dandan stairs overlooking the retro shopping street.",
                "activities": [
                    ("Yanaka Ginza Historic Shopping Street", "Taito, Tokyo", "Historic Neighborhood", "Morning", "09:30 - 12:00", 10.0, True, None, "09:30 - 11:30", "Experience traditional shitamachi atmosphere with handmade croquettes, manju sweets, and woodblock print shops."),
                    ("Kayaba Coffee", "Yanaka, Tokyo", "Historic Kissaten", "Lunch", "12:15 - 13:45", 14.0, True, "Yanaka Ginza", "12:15 seating", "1938 wooden machiya townhouse famous for its fluffy egg sandwiches and dark roast siphon coffee."),
                    ("Tokyo National Museum Gardens", "Ueno, Tokyo", "Traditional Garden", "Afternoon", "14:15 - 16:30", 6.5, True, "Kayaba Coffee", "14:30 admission", "Stroll through seasonal tea houses and autumn foliage behind the museum main hall."),
                    ("Ameyoko Market & Street Izakaya", "Ueno, Tokyo", "Bustling Open-Air Market", "Evening", "17:00 - 20:30", 30.0, False, "Ueno Gardens", "17:30 market stroll", "Lively market beneath the train tracks featuring fresh street seafood, gyoza, and yakitori."),
                ],
            },
            {
                "day_number": 5,
                "city": "Kyoto",
                "district": "Higashiyama & Gion",
                "theme": "Shinkansen to Kyoto & Lantern-Lit Preservation District",
                "summary": "Board Tokaido Shinkansen to Kyoto; explore wooden machiya preservation lanes and historic Kiyomizu-dera.",
                "transit_overview": "Tokaido Shinkansen (135 mins) + Keihan Main Line / walking (~2.8 km).",
                "sunrise": "06:22 AM",
                "sunset": "05:01 PM",
                "golden_hour": "Pontecho Alley lantern-lighting alongside the Kamogawa River at dusk.",
                "activities": [
                    ("Tokaido Shinkansen High-Speed Rail", "Kyoto", "Scenic Rail Transit", "Morning", "08:30 - 11:30", 85.0, True, "Tokyo Station", "08:33 Nozomi train", "High-speed Shinkansen passing Mount Fuji with punctual arrival into Kyoto Station."),
                    ("Gion Karyo / Omen Ginkakuji", "Gion, Kyoto", "Traditional Kyoto Cuisine", "Lunch", "12:15 - 13:45", 25.0, True, "Kyoto Station", "12:15 lunch seating", "Seasonal Kyoto udon paired with local seasonal vegetables (Kyo-yasai) and fragrant sesame dashi."),
                    ("Kiyomizu-dera & Sannenzaka Lanes", "Higashiyama, Kyoto", "Ancient Temple & World Heritage", "Afternoon", "14:15 - 17:00", 3.5, True, "Gion Lunch", "14:30 temple entry", "Dramatic 778 AD wooden stage cantilevered over the hillside without a single nail; walk preserved stone lanes."),
                    ("Gion Shirakawa Evening Stroll", "Gion, Kyoto", "Preserved Geisha Quarter", "Evening", "17:30 - 21:00", 45.0, False, "Kiyomizu-dera", "18:00 evening walk", "Canal-side stone paths lined with weeping willows, historic wooden ochaya teahouses, and Kaiseki dining."),
                ],
            },
            {
                "day_number": 6,
                "city": "Kyoto",
                "district": "Arashiyama & Sagano",
                "theme": "Bamboo Groves & Zen Rock Gardens",
                "summary": "Morning immersion in the soaring Arashiyama Bamboo Grove, Tenryu-ji Zen garden, and scenic Katsura River.",
                "transit_overview": "JR San-in Line from Kyoto station + walking (~3.4 km).",
                "sunrise": "06:23 AM",
                "sunset": "05:00 PM",
                "golden_hour": "Togetsukyo Bridge viewing sunset over the Arashiyama mountain ridge.",
                "activities": [
                    ("Arashiyama Bamboo Grove", "Ukyo, Kyoto", "Natural Landmark", "Morning", "08:00 - 10:30", 0.0, True, None, "08:00 early morning serenity", "Listen to the rustle of towering green bamboo stalks before daytime visitors arrive."),
                    ("Shigetsu (Shojin Ryori at Tenryu-ji)", "Arashiyama, Kyoto", "Buddhist Vegetarian Temple Food", "Lunch", "11:30 - 13:00", 28.0, True, "Bamboo Grove", "11:30 reserved temple lunch", "Multi-dish Michelin-selected Zen Buddhist vegetarian meal overlooking Tenryu-ji's 14th-century pond garden."),
                    ("Tenryu-ji Temple & Sogenchi Garden", "Arashiyama, Kyoto", "Zen Temple & World Heritage", "Afternoon", "13:30 - 16:00", 4.0, True, "Shigetsu", "13:30 garden entry", "Masterpiece garden created by Muso Soseki framing the Arashiyama mountains as borrowed scenery (shakkei)."),
                    ("Pontocho Alley Kaiseki Dining", "Nakagyo, Kyoto", "Historic Dining Lane", "Evening", "17:30 - 21:00", 55.0, True, "Tenryu-ji", "18:30 dinner reservation", "Narrow pedestrian corridor illuminated by red paper lanterns; enjoy seasonal Kyo-ryori along the Kamogawa."),
                ],
            },
            {
                "day_number": 7,
                "city": "Kyoto",
                "district": "Fushimi & Southern Kyoto",
                "theme": "10,000 Vermilion Torii Gates & Historic Sake Breweries",
                "summary": "Hike through the mountain shrine trails of Fushimi Inari and explore historic Fushimi canal sake cellars.",
                "transit_overview": "JR Nara Line from Kyoto station (~3.5 km walking trail).",
                "sunrise": "06:24 AM",
                "sunset": "04:59 PM",
                "golden_hour": "Sunset over Kyoto basin from Yotsutsuji intersection on Mount Inari.",
                "activities": [
                    ("Fushimi Inari Taisha", "Fushimi, Kyoto", "Historic Shinto Shrine", "Morning", "08:00 - 11:30", 0.0, True, None, "08:00 morning ascent", "Hike through the Senbon Torii tunnel of thousands of vermilion gates climbing the sacred wooded mountain."),
                    ("Nezameya (Eel & Inari Sushi)", "Fushimi, Kyoto", "Historic Eatery (Founded 1540)", "Lunch", "12:00 - 13:30", 24.0, True, "Fushimi Inari", "12:00 lunch", "Charcoal-grilled freshwater unagi and fox-eared inari sushi served since the era of Toyotomi Hideyoshi."),
                    ("Fushimi Sake District & Gekkeikan Okura", "Fushimi, Kyoto", "Historic Brewery & Museum", "Afternoon", "14:00 - 16:30", 4.0, True, "Nezameya", "14:15 admission", "Stroll willow-lined canals beside 400-year-old wooden sake storehouses; sample pure spring water and sake tasting."),
                    ("Kyoto Station Skyway & Farewell Feast", "Shimogyo, Kyoto", "Viewpoint & Dining", "Evening", "17:30 - 21:00", 48.0, False, "Fushimi Brewery", "18:00 sunset view", "Take the aerial glass skyway 15 floors above Kyoto, followed by celebratory sukiyaki dinner at Mishima-tei."),
                ],
            },
        ]

        days = []
        for defn in day_defs[:num_days]:
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
                    currency="USD",
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
                currency="USD",
                sunrise=defn["sunrise"],
                sunset=defn["sunset"],
                golden_hour_advice=defn["golden_hour"],
            )
            days.append(day_obj)

        transfers = []
        if num_days >= 5:
            transfers.append(l.plan_intercity_transfer("Tokyo", "Kyoto", day=5))

        trip = CanonicalTripState(
            trip_id="trip_japan_canonical",
            title=f"{num_days}-Day Verified Cultural & Culinary Journey in Japan",
            destination="Japan (Tokyo, Kyoto)",
            duration_days=len(days),
            start_date=s_date,
            end_date="2026-11-08",
            currency="USD",
            days=days,
            intercity_transfers=transfers,
        )

        transfer_costs = sum((t.estimated_cost.amount if t.estimated_cost else 0.0) for t in trip.intercity_transfers)
        total_cost = sum(d.daily_budget_subtotal for d in trip.days) + transfer_costs
        trip.total_budget_per_person = round(total_cost, 2)
        trip.total_group_budget = round(total_cost * trip.group_size, 2)
        trip.feasibility_report = self.qa_agent.evaluate_trip_feasibility(trip)
        return trip

    def _build_canonical_kerala_trip(self, num_days: int = 5, start_date: Optional[str] = None) -> CanonicalTripState:
        """Synthesize canonical Kerala (Kochi, Munnar, Alleppey) trip plan."""
        s_date = start_date or "2026-11-02"
        v = self.verification_agent
        l = self.logistics_agent

        day_defs = [
            {
                "day_number": 1,
                "city": "Kochi",
                "district": "Fort Kochi & Mattancherry",
                "theme": "Colonial Heritage, Chinese Fishing Nets & Spice Markets",
                "summary": "Walk the historic seaside promenade of Fort Kochi, see Cantilevered Chinese Fishing Nets, and tour the historic spice bazaar.",
                "transit_overview": "Walkable historic quarter and local tuk-tuks (~3.0 km).",
                "sunrise": "06:14 AM",
                "sunset": "06:05 PM",
                "golden_hour": "Sunset over Fort Kochi beach with silhouettes of Chinese fishing nets at 5:45 PM.",
                "activities": [
                    ("Fort Kochi Chinese Fishing Nets", "Fort Kochi", "Cultural Heritage", "Morning", "08:30 - 11:30", 2.0, True, None, "08:30 early morning fishermen activity", "14th-century cantilevered fishing nets operating along the Arabian sea channel."),
                    ("Grand Pavilion / Seagull", "Fort Kochi", "Authentic Kerala Seafood", "Lunch", "12:30 - 14:00", 12.0, True, "Chinese Fishing Nets", "12:30 lunch window", "Traditional Karimeen Pollichathu (pearl spot fish baked in banana leaf) and Appam with stew."),
                    ("Mattancherry Palace & Jew Town", "Mattancherry, Kochi", "Historic Palace & Bazaar", "Afternoon", "14:30 - 17:00", 1.5, True, "Seagull Restaurant", "14:30 admission", "Dutch Palace featuring 16th-century Hindu mythological murals and Paradesi Synagogue in the antique quarter."),
                    ("Kathakali Dance Performance", "Fort Kochi", "Classical Performing Arts", "Evening", "17:30 - 20:30", 8.0, True, "Jew Town", "17:30 makeup ritual / 18:30 show", "Witness intricate face painting and dynamic Mudra expression in Kerala's 500-year-old dance drama."),
                ],
            },
            {
                "day_number": 2,
                "city": "Kochi",
                "district": "Ernakulam & Marine Drive",
                "theme": "Backwater Gateway & Traditional Malabar Cooking",
                "summary": "Morning cruise along Vembanad Lake backwater channels and explore Broadway spice markets.",
                "transit_overview": "State Water Transport boats and Metro Line (~3.5 km).",
                "sunrise": "06:14 AM",
                "sunset": "06:05 PM",
                "golden_hour": "Sunset cruise along Marine Drive looking toward Bolgatty Island.",
                "activities": [
                    ("Vembanad Lake Ferry & Marine Drive", "Ernakulam, Kochi", "Scenic Water Transit", "Morning", "09:00 - 11:30", 1.0, True, None, "09:00 tranquil morning water", "Public water ferry crossing the backwaters; views of shipyard and island fishing communities."),
                    ("Paragon Restaurant", "Lulu / Marine Drive, Kochi", "Malabar Biryani Specialist", "Lunch", "12:30 - 14:00", 9.0, True, "Marine Drive", "12:30 lunch", "World-renowned Malabar mutton/chicken biryani flavored with jeerakasala rice, ghee, and roasted cashews."),
                    ("Hill Palace Museum", "Tripunithura, Kochi", "Royal Palace & Heritage Park", "Afternoon", "14:30 - 17:00", 2.0, True, "Paragon Restaurant", "14:30 admission", "Largest archaeological museum in Kerala housing Cochin Maharaja crowns, royal palanquins, and paintings."),
                    ("Evening Spice Tasting & Cultural Stroll", "Ernakulam, Kochi", "Market Experience", "Evening", "17:30 - 20:30", 15.0, False, "Hill Palace", "18:00 bazaar walk", "Sample fresh cardamom, Malabar black pepper, and banana chips fried in pure coconut oil."),
                ],
            },
            {
                "day_number": 3,
                "city": "Alleppey",
                "district": "Punnamada & Vembanad Backwaters",
                "theme": "Tranquil Houseboat Kettuvallam Cruise",
                "summary": "Transfer to Alleppey for a traditional thatched-roof Kettuvallam houseboat cruise through palm-fringed canals.",
                "transit_overview": "Scenic coastal rail/drive from Kochi (75 mins) + tranquil canal boat navigation.",
                "sunrise": "06:13 AM",
                "sunset": "06:06 PM",
                "golden_hour": "Sun sinking behind paddy fields and coconut groves from the upper deck of the houseboat.",
                "activities": [
                    ("Coastal Rail Transfer to Alleppey", "Alleppey", "Scenic Transit", "Morning", "08:30 - 10:30", 12.0, True, "Kochi Station", "08:30 departure", "Scenic coastal journey past Vembanad lake arriving at the Alappuzha jetty."),
                    ("Traditional Houseboat Lunch on Water", "Punnamada, Alleppey", "Onboard Backwater Dining", "Lunch", "12:00 - 14:00", 20.0, True, "Alleppey Jetty", "12:30 served fresh", "Freshly caught lake fish curry, red matta rice, avial, and thoran prepared by an onboard private chef."),
                    ("Village Canoe Excursion into Narrow Canals", "Kuttanad, Alleppey", "Ecological Tour", "Afternoon", "14:30 - 17:00", 10.0, True, "Houseboat Anchorage", "15:00 paddle tour", "Glide through quiet residential canals below sea level; see duck farming, coir making, and village life."),
                    ("Alleppey Beach & Historic Pier Sunset", "Alleppey", "Coastal Landmark", "Evening", "17:30 - 20:30", 8.0, False, "Backwaters", "17:45 sunset", "Stroll along the historic 150-year-old sea pier and lighthouse followed by local Kerala parotta and curry."),
                ],
            },
            {
                "day_number": 4,
                "city": "Munnar",
                "district": "Tea Gardens & Western Ghats",
                "theme": "Misty Tea Plantations & Mountain Waterfalls",
                "summary": "Ascend into the cool misty mountains of Munnar, carpeted in emerald tea estates and spice gardens.",
                "transit_overview": "Mountain hill drive past waterfalls (~4.0 hours, 130 km).",
                "sunrise": "06:11 AM",
                "sunset": "06:04 PM",
                "golden_hour": "Sunset over Chithirapuram tea slopes with rolling mountain mist.",
                "activities": [
                    ("Hill Road to Munnar & Cheeyappara Falls", "Munnar", "Scenic Mountain Transit", "Morning", "08:00 - 11:30", 25.0, True, "Alleppey", "08:00 mountain start", "Winding ascent through lush rainforest past seven-step Cheeyappara and Valara waterfalls."),
                    ("Rapsy Restaurant / Silver Spoon", "Munnar Town", "Local Hill Station Cafe", "Lunch", "12:30 - 14:00", 8.0, True, "Munnar Center", "12:30 lunch", "Hot Kerala parotta, spicy beef roast or vegetable kurma, and cardamom-infused mountain tea."),
                    ("KDHP Tea Museum & Factory Experience", "Nullatanni, Munnar", "Industrial Heritage Museum", "Afternoon", "14:30 - 17:00", 2.5, True, "Rapsy Restaurant", "14:30 demonstration", "Learn orthodox and CTC tea processing history; participate in tea tasting of high-grown black teas."),
                    ("Top Station & Kundala Lake Twilight", "Munnar", "Panoramic Viewpoint", "Evening", "17:15 - 20:15", 5.0, False, "Tea Museum", "17:30 twilight vistas", "Panoramic lookout on the Kerala-Tamil Nadu border offering dramatic views of the Western Ghats peaks."),
                ],
            },
            {
                "day_number": 5,
                "city": "Munnar",
                "district": "Eravikulam & Marayoor",
                "theme": "Nilgiri Tahr Wildlife & Sandalwood Forests",
                "summary": "Morning safari into Eravikulam National Park beneath Anamudi peak, concluding with spice garden exploration.",
                "transit_overview": "Park shuttle bus and mountain trails (~3.0 km).",
                "sunrise": "06:11 AM",
                "sunset": "06:04 PM",
                "golden_hour": "Golden sunlight bathing the high-altitude shola grassland plateau.",
                "activities": [
                    ("Eravikulam National Park (Rajamalai)", "Munnar", "Wildlife Sanctuary", "Morning", "08:00 - 11:30", 5.5, True, None, "08:00 first park safari", "Spot endangered Nilgiri Tahr mountain goats grazing beneath Anamudi, South India's highest peak (2,695m)."),
                    ("Saravana Bhavan / Cloud Street", "Munnar", "Traditional South Indian Dining", "Lunch", "12:00 - 13:30", 6.0, True, "Eravikulam Park", "12:00 lunch", "Crisp Ghee Roast Dosas, Idli with coconut chutney, and filter coffee."),
                    ("Marayoor Sandalwood Forest & Dolmens", "Marayoor, Munnar", "Ancient Heritage & Forest", "Afternoon", "14:00 - 16:30", 2.0, True, "Saravana Bhavan", "14:15 site tour", "Natural sandalwood reserve and prehistoric Megalithic dolmens (Muniyaras) dating back to the Iron Age."),
                    ("Spice Plantation Tour & Farewell Dinner", "Munnar", "Agro-Tourism & Dining", "Evening", "17:00 - 20:30", 18.0, True, "Marayoor", "17:30 guided spice walk", "Smell fresh vanilla, nutmeg, cinnamon, and pepper vines followed by traditional Sadya meal served on plantain leaves."),
                ],
            },
        ]

        days = []
        for defn in day_defs[:num_days]:
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
                    currency="USD",
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
                currency="USD",
                sunrise=defn["sunrise"],
                sunset=defn["sunset"],
                golden_hour_advice=defn["golden_hour"],
            )
            days.append(day_obj)

        transfers = []
        if num_days >= 3:
            transfers.append(l.plan_intercity_transfer("Kochi", "Alleppey", day=3))
        if num_days >= 4:
            transfers.append(l.plan_intercity_transfer("Kochi", "Munnar", day=4))

        trip = CanonicalTripState(
            trip_id="trip_kerala_canonical",
            title=f"{num_days}-Day Verified Natural & Cultural Journey in Kerala",
            destination="Kerala (Kochi, Alleppey, Munnar)",
            duration_days=len(days),
            start_date=s_date,
            end_date="2026-11-08",
            currency="USD",
            days=days,
            intercity_transfers=transfers,
        )

        transfer_costs = sum((t.estimated_cost.amount if t.estimated_cost else 0.0) for t in trip.intercity_transfers)
        total_cost = sum(d.daily_budget_subtotal for d in trip.days) + transfer_costs
        trip.total_budget_per_person = round(total_cost, 2)
        trip.total_group_budget = round(total_cost * trip.group_size, 2)
        trip.feasibility_report = self.qa_agent.evaluate_trip_feasibility(trip)
        return trip

    def _build_canonical_dynamic_trip(self, user_request: str, num_days: int, start_date: str = "2026-11-02") -> CanonicalTripState:
        """Dynamic multi-agent synthesis discovering real venues via Google Places API and culinary database."""
        v = self.verification_agent
        l = self.logistics_agent

        # Extract destination keywords
        cleaned = re.sub(r"[^\w\s]", " ", user_request)
        tokens = [w for w in cleaned.split() if w.lower() not in {"plan", "trip", "visit", "tour", "authentic", "realistic", "food", "specialties", "verified", "places", "days", "for", "in", "to", "and", "the", "a", "my"}]
        dest_name = tokens[0].title() if tokens else "Curated Destination"

        # Query live Google Places API for real experiences and dining in destination
        live_attractions = v.search_live_experiences(dest_name, category="historic landmarks cultural attractions", max_results=8)
        live_dining = v.search_live_dining(dest_name, max_results=8)

        days = []
        for d in range(1, num_days + 1):
            attr1 = live_attractions[(d * 2 - 2) % len(live_attractions)] if live_attractions else None
            attr2 = live_attractions[(d * 2 - 1) % len(live_attractions)] if live_attractions else None
            dine1 = live_dining[(d * 2 - 2) % len(live_dining)] if live_dining else None
            dine2 = live_dining[(d * 2 - 1) % len(live_dining)] if live_dining else None

            title_m = attr1.get("name") if attr1 else f"{dest_name} Cultural Landmark"
            title_l = dine1.get("name") if dine1 else f"Authentic {dest_name} Osteria"
            title_a = attr2.get("name") if attr2 else f"{dest_name} Historic District"
            title_e = dine2.get("name") if dine2 else f"{dest_name} Evening Dining & Viewpoint"

            acts = [
                v.verify_place(title_m, dest_name, category="Cultural Landmark", slot="Morning", time_window="09:00 - 11:30", cost_amount=15.0, currency="USD", is_cost_verified=(attr1 is not None)),
                v.verify_place(title_l, dest_name, category="Authentic Dining", slot="Lunch", time_window="12:30 - 14:00", cost_amount=22.0, currency="USD", is_cost_verified=(dine1 is not None), origin_name=title_m),
                v.verify_place(title_a, dest_name, category="Scenic Attraction", slot="Afternoon", time_window="14:30 - 17:00", cost_amount=10.0, currency="USD", is_cost_verified=(attr2 is not None), origin_name=title_l),
                v.verify_place(title_e, dest_name, category="Evening Venue", slot="Evening", time_window="17:30 - 20:30", cost_amount=35.0, currency="USD", is_cost_verified=(dine2 is not None), origin_name=title_a),
            ]
            day_subtotal = sum((a.estimated_cost.amount if a.estimated_cost else 0.0) for a in acts)

            days.append(DaySchedule(
                day_number=d,
                city=dest_name,
                district="Historic Core",
                theme=f"{dest_name} Cultural Exploration (Day {d})",
                summary=f"Curated day {d} exploration discovering authentic highlights in {dest_name}.",
                transit_overview="Pedestrian exploration and local transit.",
                activities=acts,
                daily_budget_subtotal=round(day_subtotal, 2),
                currency="USD",
                sunrise="06:30 AM",
                sunset="06:00 PM",
            ))

        trip = CanonicalTripState(
            trip_id=f"trip_{dest_name.lower()[:8]}_canonical",
            title=f"{num_days}-Day Verified Exploration in {dest_name}",
            destination=dest_name,
            duration_days=num_days,
            start_date=start_date,
            currency="USD",
            days=days,
        )
        total_cost = sum(d.daily_budget_subtotal for d in trip.days)
        trip.total_budget_per_person = round(total_cost, 2)
        trip.total_group_budget = round(total_cost * trip.group_size, 2)
        trip.feasibility_report = self.qa_agent.evaluate_trip_feasibility(trip)
        return trip

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

        transfer_costs = sum((t.estimated_cost.amount if t.estimated_cost else 0.0) for t in trip.intercity_transfers)
        total_cost = sum(d.daily_budget_subtotal for d in trip.days) + transfer_costs
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
                v.verify_place(f"{dest_guess} Heritage Landmark", dest_guess, category="Cultural Landmark", slot="Morning", time_window="09:00 - 11:30", cost_amount=15.0, currency="USD", is_cost_verified=False),
                v.verify_place(f"Authentic {dest_guess} Trattoria", dest_guess, category="Local Dining", slot="Lunch", time_window="12:30 - 14:00", cost_amount=20.0, currency="USD", is_cost_verified=False),
                v.verify_place(f"{dest_guess} Historic Quarter", dest_guess, category="Scenic District", slot="Afternoon", time_window="14:30 - 17:00", cost_amount=5.0, currency="USD", is_cost_verified=False),
                v.verify_place(f"{dest_guess} Sunset Lookout & Dinner", dest_guess, category="Viewpoint & Dining", slot="Evening", time_window="17:30 - 20:30", cost_amount=35.0, currency="USD", is_cost_verified=False),
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
