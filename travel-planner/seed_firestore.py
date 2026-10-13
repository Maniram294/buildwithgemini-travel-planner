"""Seed script for populating destinations into Firestore."""
from google.cloud import firestore

FIRESTORE_PROJECT_ID = "qwiklabs-gcp-03-fe98c55ba1b5"

DESTINATIONS = [
    {
        "id": "kyoto-japan",
        "name": "Kyoto",
        "country": "Japan",
        "travel_style": "cultural",
        "budget_tier": "moderate",
        "highlights": ["Fushimi Inari Taisha", "Kinkaku-ji", "Arashiyama Bamboo Grove"],
        "best_season": "Spring (Cherry Blossoms) & Autumn",
        "estimated_daily_cost_usd": 150,
        "description": "Historic imperial capital famous for classical Buddhist temples, serene gardens, imperial palaces, and traditional wooden houses.",
    },
    {
        "id": "reykjavik-iceland",
        "name": "Reykjavik & South Coast",
        "country": "Iceland",
        "travel_style": "adventure",
        "budget_tier": "luxury",
        "highlights": ["Golden Circle", "Blue Lagoon", "Skogafoss Waterfall", "Northern Lights"],
        "best_season": "Summer (Hiking) or Winter (Aurora Borealis)",
        "estimated_daily_cost_usd": 280,
        "description": "Gateway to volcanic landscapes, hot springs, dramatic waterfalls, and midnight sun or winter auroras.",
    },
    {
        "id": "oaxaca-mexico",
        "name": "Oaxaca",
        "country": "Mexico",
        "travel_style": "foodie",
        "budget_tier": "budget",
        "highlights": ["Mercado 20 de Noviembre", "Monte Alban", "Hierve el Agua", "Mezcal tastings"],
        "best_season": "October to March",
        "estimated_daily_cost_usd": 70,
        "description": "Culinary capital renowned for mole varieties, vibrant indigenous arts, and colonial architecture.",
    },
    {
        "id": "queenstown-new-zealand",
        "name": "Queenstown",
        "country": "New Zealand",
        "travel_style": "adventure",
        "budget_tier": "moderate",
        "highlights": ["Milford Sound Cruise", "Bungee Jumping", "Lake Wakatipu", "Remarkables Skiing"],
        "best_season": "December to February (Summer) or July to August (Winter)",
        "estimated_daily_cost_usd": 200,
        "description": "World-famous adventure capital surrounded by dramatic Southern Alps and pristine alpine lakes.",
    },
    {
        "id": "florence-italy",
        "name": "Florence & Tuscany",
        "country": "Italy",
        "travel_style": "cultural",
        "budget_tier": "moderate",
        "highlights": ["Uffizi Gallery", "Duomo di Firenze", "Chianti Wine Region", "Ponte Vecchio"],
        "best_season": "May to September",
        "estimated_daily_cost_usd": 180,
        "description": "Birthplace of the Renaissance, celebrated for masterwork art, world-class Tuscan cuisine, and rolling vineyard hills.",
    },
]


def seed_database():
    print(f"Connecting to Firestore project: {FIRESTORE_PROJECT_ID}...")
    db = firestore.Client(project=FIRESTORE_PROJECT_ID)
    collection_ref = db.collection("destinations")

    for dest in DESTINATIONS:
        doc_id = dest["id"]
        doc_ref = collection_ref.document(doc_id)
        doc_ref.set(dest)
        print(f"✓ Seeded destination: {dest['name']} ({doc_id})")

    print("\nDatabase seeding completed successfully!")


if __name__ == "__main__":
    seed_database()
