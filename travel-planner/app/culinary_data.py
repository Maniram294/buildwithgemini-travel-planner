"""Regional culinary knowledge base grounding regional food specialties across world destinations."""

from typing import Any, Dict, List, Optional

# Verified destination culinary knowledge linking destinations to authentic regional dishes,
# cultural significance, traditional markets/food streets, and typical venue types.
REGIONAL_SPECIALTIES: Dict[str, Dict[str, Any]] = {
    "tokyo": {
        "destination": "Tokyo, Japan",
        "food_culture_summary": (
            "Tokyo cuisine blends refined Edomae (historic Edo) traditions with cutting-edge culinary specialization. "
            "Rather than generalist dining, Tokyo's best culinary experiences happen at single-specialty shops (ramen-ya, "
            "yakitori-ya, tempura-ya, sushiya) and historic department store depachika food halls."
        ),
        "signature_dishes": [
            {
                "dish": "Edomae Nigiri Sushi",
                "cultural_context": "Originating in 1820s Edo as street food, fast-cured with red vinegar and soy.",
                "typical_ordering_advice": "Sit at the counter for omakase or visit classic Toyosu/Tsukiji outer market sushi shops."
            },
            {
                "dish": "Monjayaki",
                "cultural_context": "Tokyo's beloved runny, savory pan-fried batter, famously eaten in Tsukishima along Monja Street.",
                "typical_ordering_advice": "Cook it yourself on the teppan grill with cabbage, mentaiko (pollock roe), and mochi."
            },
            {
                "dish": "Tsukemen (Dipping Noodles)",
                "cultural_context": "Invented in Tokyo by Kazuo Yamagishi (Taishoken); cold thick noodles dipped into concentrated pork/fish broth.",
                "typical_ordering_advice": "Order soup-wari (hot broth to dilute the remaining dipping soup) at the end."
            },
            {
                "dish": "Yakitori & Kushiyaki",
                "cultural_context": "Skewered chicken grilled over white binchotan charcoal, standard evening salaryman fare.",
                "typical_ordering_advice": "Choose between tare (sweet soy glaze) or shio (mineral salt)."
            },
            {
                "dish": "Fukagawa Meshi",
                "cultural_context": "Historic Edo fishermen's dish of fresh clams simmered with miso and scallions over steamed rice.",
                "typical_ordering_advice": "Best enjoyed in historic neighborhoods of Koto and Fukagawa."
            }
        ],
        "food_neighborhoods": [
            {"neighborhood": "Tsukishima Monja Street", "vibe": "Dozens of lively retro Monjayaki restaurants."},
            {"neighborhood": "Tsukiji Outer Market", "vibe": "Tamagoyaki, fresh sashimi bowls, grilled seafood skewers in the morning."},
            {"neighborhood": "Omoide Yokocho & Golden Gai (Shinjuku)", "vibe": "Narrow alleys with tiny yakitori stalls and historic drinking holes."},
            {"neighborhood": "Sunamachi Ginza / Yanaka Ginza", "vibe": "Traditional shitamachi shopping streets with croquettes, yakitori, and street snacks."}
        ]
    },
    "kyoto": {
        "destination": "Kyoto, Japan",
        "food_culture_summary": (
            "Kyoto's culinary identity (Kyo-ryori) is grounded in centuries of imperial banquet culture, Buddhist vegetarian "
            "(shojin ryori) aesthetics, and delicate dashi broths that emphasize pristine seasonal ingredients rather than heavy seasoning."
        ),
        "signature_dishes": [
            {
                "dish": "Kaiseki Ryori",
                "cultural_context": "Multi-course traditional dinner with origins in tea ceremony cuisine, reflecting the current season.",
                "typical_ordering_advice": "Reserve in advance in Gion or Pontocho; lunch menus are often half the dinner price."
            },
            {
                "dish": "Yudofu & Shojin Ryori",
                "cultural_context": "Simmered artisan tofu in kelp broth, perfected by Zen Buddhist monks in Nanzen-ji and Arashiyama.",
                "typical_ordering_advice": "Eat with sweet ginger soy or ponzu at temple-adjacent specialty eateries."
            },
            {
                "dish": "Kyo-Tsukemono & Obanzai",
                "cultural_context": "Kyoto home-style small dishes and preserved heritage vegetables (Kyo-yasai).",
                "typical_ordering_advice": "Visit an obanzai counter eatery where seasonal dishes are displayed in large earthenware bowls."
            },
            {
                "dish": "Uji Matcha Parfait & Wagashi",
                "cultural_context": "Kyoto is the heart of Japanese green tea, using ceremonial grade Uji matcha in confections.",
                "typical_ordering_advice": "Pair fresh seasonal wagashi with bitter usucha whisked tea in traditional teahouses."
            },
            {
                "dish": "Nishin Soba",
                "cultural_context": "Buckwheat soba topped with sweet-simmered dried Pacific herring, a Kyoto classic since 1882.",
                "typical_ordering_advice": "Available at traditional soba shops around Higashiyama."
            }
        ],
        "food_neighborhoods": [
            {"neighborhood": "Nishiki Market ('Kyoto's Kitchen')", "vibe": "Narrow covered arcade with over 100 stalls selling dashi, tsukemono, yuba, and skewered sweets."},
            {"neighborhood": "Pontocho Alley", "vibe": "Atmospheric lantern-lit alley along the Kamogawa river, with riverside kawayuka dining in warmer months."},
            {"neighborhood": "Gion Shirakawa", "vibe": "Preserved historic wooden machiya townhouses housing high-end kaiseki and intimate tea houses."}
        ]
    },
    "istanbul": {
        "destination": "Istanbul, Turkey",
        "food_culture_summary": (
            "A bridge between Europe, Central Asia, and the Middle East, Istanbul's food ranges from Ottoman palace feasts "
            "to incredible Anatolian regional kebabs, mezze taverns (meyhanes), and vibrant Black Sea fish counters."
        ),
        "signature_dishes": [
            {
                "dish": "Balık Ekmek & Midye Dolma",
                "cultural_context": "Freshly grilled mackerel sandwiches on crusty bread eaten along the Golden Horn and Karaköy.",
                "typical_ordering_advice": "Squeeze fresh lemon juice over the fish and pair with fermented turnip juice (şalgam)."
            },
            {
                "dish": "Cağ Kebabı & İskender Kebab",
                "cultural_context": "Horizontal marinated lamb kebab cooked over wood fire, or thinly sliced döner over toasted pide with tomato sauce and browned butter.",
                "typical_ordering_advice": "Order with fresh sheep's milk yogurt."
            },
            {
                "dish": "Karaköy Baklava with Kaymak",
                "cultural_context": "Forty paper-thin layers of filo pastry soaked in sugar syrup and filled with Antep pistachios, served with clotted water-buffalo cream.",
                "typical_ordering_advice": "Eat upside down so the buttered top crust hits your tongue first."
            },
            {
                "dish": "Menemen & Serpme Kahvaltı (Turkish Breakfast)",
                "cultural_context": "Eggs softly scrambled with tomatoes, green peppers, and oregano; centerpiece of legendary Turkish multi-plate breakfasts.",
                "typical_ordering_advice": "Dip fresh simit (sesame bread rings) directly into the copper pan."
            }
        ],
        "food_neighborhoods": [
            {"neighborhood": "Karaköy & Eminönü", "vibe": "Bustling ferry docks with fish sandwiches, street vendors, and heritage pastry shops."},
            {"neighborhood": "Kadıköy Fish Market (Asian side)", "vibe": "Vibrant local market lined with produce, pickle shops, cheese makers, and top-tier Anatolian lokantas."},
            {"neighborhood": "Beyoğlu & Nevizade Street", "vibe": "Lively meyhane taverns with cold and hot mezze, raki, and live fasıl music."}
        ]
    },
    "paris": {
        "destination": "Paris, France",
        "food_culture_summary": (
            "Classic French bistro cuisine centered on terroir, slow-cooked braises, artisanal charcuterie, natural wine bars, "
            "and neighborhood boulangeries with strictly regulated traditional baguettes (baguette de tradition)."
        ),
        "signature_dishes": [
            {
                "dish": "Boeuf Bourguignon / Confit de Canard",
                "cultural_context": "Pillars of traditional French bistro cooking, slow cooked with red wine or rendered duck fat.",
                "typical_ordering_advice": "Look for the 'Fait Maison' (housemade) label on chalkboard menus."
            },
            {
                "dish": "Artisanal Cheese Board (AOC Fromages)",
                "cultural_context": "Selection of raw-milk Comté, Roquefort, and Camembert, served after main courses.",
                "typical_ordering_advice": "Visit a dedicated fromagerie (e.g. Laurent Dubois) or order after dinner with crusty bread."
            },
            {
                "dish": "Croque Monsieur / Madame",
                "cultural_context": "Classic café comfort food with Parisian ham, gruyère, and béchamel broiled on country bread.",
                "typical_ordering_advice": "Order as a 'Madame' for a fried egg on top."
            }
        ],
        "food_neighborhoods": [
            {"neighborhood": "Le Marais", "vibe": "Historic Jewish quarter bakeries, falafel on Rue des Rosiers, and trendy neo-bistros."},
            {"neighborhood": "Marché d'Aligre (12th arr.)", "vibe": "Lively authentic market square with produce stalls, flea market, and wine bars."},
            {"neighborhood": "Rue Cler / Rue Montorgueil", "vibe": "Pedestrian cobblestone market streets lined with poissonneries, boucheries, and pastry shops."}
        ]
    }
}


def get_culinary_context(destination: str) -> Optional[Dict[str, Any]]:
    """Retrieve grounded culinary specialties, signature dishes, and food districts for a destination."""
    dest_clean = destination.lower().strip()
    for key, data in REGIONAL_SPECIALTIES.items():
        if key in dest_clean or dest_clean in key:
            return data
    return None
