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
    },
    "italy": {
        "destination": "Italy (Rome, Florence, Venice)",
        "food_culture_summary": (
            "Italian culinary culture is fiercely regional and hyper-seasonal, guided by 'cucina povera' principles "
            "where minimal, exceptional ingredients shine. From Roman four classic pastas to Tuscan chianina beef and "
            "Venetian lagoon cicchetti, dining is tied to historic osterie, trattorie, and bacari."
        ),
        "signature_dishes": [
            {
                "dish": "Cacio e Pepe & Carbonara (Rome)",
                "cultural_context": "Pillars of Roman cucina povera: Pecorino Romano DOP, toasted black pepper, guanciale, and farm eggs.",
                "typical_ordering_advice": "Enjoy in a traditional trattoria in Trastevere or Testaccio; pair with Frascati Superiore wine."
            },
            {
                "dish": "Bistecca alla Fiorentina (Florence)",
                "cultural_context": "Thick T-bone steak from ancient Chianina cattle, grilled rare over smoking oak coals with sea salt and Tuscan olive oil.",
                "typical_ordering_advice": "Ordered strictly by weight (al chilo) and served rare (al sangue); visit classic spots near San Lorenzo."
            },
            {
                "dish": "Venetian Cicchetti & Spritz (Venice)",
                "cultural_context": "Bite-sized bar snacks served on crusty bread in historic Venetian bacari (wine bars), washed down with an 'ombra' of local wine.",
                "typical_ordering_advice": "Try Baccalà mantecato (whipped salt cod) and Polpette in San Polo and Cannaregio bacari."
            },
            {
                "dish": "Ribollita & Pappa al Pomodoro (Tuscany)",
                "cultural_context": "Hearty Tuscan bread soups made with cavolo nero (Tuscan black kale), cannellini beans, and day-old sourdough.",
                "typical_ordering_advice": "Drizzle generously with fresh peppery Tuscan extra virgin olive oil."
            },
            {
                "dish": "Risotto al Nero di Seppia (Venice)",
                "cultural_context": "Iconic Venetian lagoon risotto stained jet black with fresh cuttlefish ink, simmered in rich seafood stock.",
                "typical_ordering_advice": "Best enjoyed at waterfront osterie in Burano or Dorsoduro."
            }
        ],
        "food_neighborhoods": [
            {"neighborhood": "Trastevere & Testaccio (Rome)", "vibe": "Historic cobblestone alleys packed with authentic family trattorias, pizza al taglio, and traditional tripperie."},
            {"neighborhood": "San Lorenzo & Oltrarno (Florence)", "vibe": "Historic food market bustling with tripe sandwiches (lampredotto) and artisan neighborhood osterie across the Arno."},
            {"neighborhood": "Cannaregio & San Polo (Venice)", "vibe": "Canal-side bacari where locals gather standing for evening cicchetti and natural Venetian wines."}
        ]
    },
    "rome": {
        "destination": "Rome, Italy",
        "food_culture_summary": (
            "Roman cuisine is rooted in bold, rustic flavors: Pecorino Romano, guanciale, artichokes, and hearty pastas. "
            "Eating in Rome revolves around neighborhood trattorias and historic bakeries (forni)."
        ),
        "signature_dishes": [
            {
                "dish": "Tonnarelli Cacio e Pepe",
                "cultural_context": "Handmade egg pasta with sharp Pecorino Romano DOP and freshly cracked black pepper.",
                "typical_ordering_advice": "Look for creamy emulsion without added cream; visit Da Enzo al 29 or Felice a Testaccio."
            },
            {
                "dish": "Carciofi alla Giudia / alla Romana",
                "cultural_context": "Historic Roman Jewish ghetto fried whole artichoke, crisp like potato chips with a tender heart.",
                "typical_ordering_advice": "Order in the Portico d'Ottavia Jewish Ghetto during peak spring artichoke season."
            },
            {
                "dish": "Rigatoni all'Amatriciana",
                "cultural_context": "Crispy cured pork jowl (guanciale), San Marzano tomatoes, chili, and grated Pecorino Romano.",
                "typical_ordering_advice": "Classic Roman comfort meal; authentic versions never contain onion or garlic."
            }
        ],
        "food_neighborhoods": [
            {"neighborhood": "Testaccio", "vibe": "The cradle of Roman cuisine with the bustling Testaccio covered market."},
            {"neighborhood": "Trastevere", "vibe": "Lively bohemian streets with vine-covered trattorias and evening piazzas."}
        ]
    },
    "florence": {
        "destination": "Florence, Italy",
        "food_culture_summary": (
            "Florentine dining celebrates Tuscan simplicity, olive oil, legumes, and world-renowned meats. "
            "From rustic market stalls serving panino con lampredotto to historic wine windows (buchette del vino)."
        ),
        "signature_dishes": [
            {
                "dish": "Bistecca alla Fiorentina",
                "cultural_context": "High-cut Chianina T-bone steak seared over glowing wood embers, dressed simply with sea salt and olive oil.",
                "typical_ordering_advice": "Never ask for it well-done; share a 1.2kg cut with wine from Chianti Classico."
            },
            {
                "dish": "Panino con Lampredotto",
                "cultural_context": "Centuries-old Florentine street food made from slow-simmered beef tripe with salsa verde on crusty semelle bread.",
                "typical_ordering_advice": "Ask for 'bagnato' (bread dipped in rich cooking broth) at street kiosks like Da Nerbone."
            },
            {
                "dish": "Pici al Ragù di Cinghiale",
                "cultural_context": "Thick hand-rolled Tuscan pici pasta tossed with slow-braised wild boar sauce.",
                "typical_ordering_advice": "Order in cozy trattorie across the Arno in the Oltrarno artisan district."
            }
        ],
        "food_neighborhoods": [
            {"neighborhood": "Oltrarno (Santo Spirito)", "vibe": "Artisan workshops, quiet squares, and Florentine wine bars away from tour crowds."},
            {"neighborhood": "Mercato Centrale / San Lorenzo", "vibe": "Historic iron-and-glass market with traditional butchers downstairs and artisanal food stalls upstairs."}
        ]
    },
    "venice": {
        "destination": "Venice, Italy",
        "food_culture_summary": (
            "Venetian cuisine reflects its maritime empire and lagoon ecosystem: fresh Adriatic fish, creamy polenta, "
            "and the social culture of the bacaro crawl (andar a cicheti)."
        ),
        "signature_dishes": [
            {
                "dish": "Baccalà Mantecato",
                "cultural_context": "Air-whipped Norwegian stockfish emulsified with olive oil into a cloud-like mousse, served on grilled white polenta.",
                "typical_ordering_advice": "A staple cicchetto at Cantina Do Mori and Cantinone Già Schiavi."
            },
            {
                "dish": "Sarde in Saor",
                "cultural_context": "Historic preservation dish of sweet-and-sour fried sardines layered with caramelized onions, pine nuts, and sultanas.",
                "typical_ordering_advice": "Best served at room temperature after marinating for at least 24 hours."
            },
            {
                "dish": "Bigoli in Salsa",
                "cultural_context": "Thick whole-wheat Venetian pasta tossed in a melted sauce of slow-cooked salt-cured anchovies and sweet onions.",
                "typical_ordering_advice": "Traditional Friday fasting dish, rich in savory lagoon umami."
            }
        ],
        "food_neighborhoods": [
            {"neighborhood": "Cannaregio (Fondamenta dei Ormesini)", "vibe": "Canal-side promenade lined with relaxed bacari where locals drink spritz at twilight."},
            {"neighborhood": "Dorsoduro", "vibe": "Student-friendly bars, Campo Santa Margherita, and scenic canal-front cicchetti bars near the squero (gondola boatyard)."}
        ]
    },
    "hyderabad": {
        "destination": "Hyderabad, India",
        "food_culture_summary": (
            "Hyderabadi cuisine is a legendary synthesis of royal Mughlai opulence, Persian influences, and fiery Telugu spices. "
            "Renowned for slow-cooking (dum) techniques, aromatic saffron and cardamom, rich gravies, and historic Irani cafe tea culture."
        ),
        "signature_dishes": [
            {
                "dish": "Hyderabadi Dum Biryani",
                "cultural_context": "Kacchi yakhni style where marinated raw mutton or chicken and parboiled basmati rice are sealed in a handi with dough and slow-cooked over coals.",
                "typical_ordering_advice": "Order at iconic heritage institutions like Paradise (Secunderabad), Bawarchi (RTC X Roads), or Shadab (Ghansi Bazaar)."
            },
            {
                "dish": "Hyderabadi Haleem",
                "cultural_context": "GI-tagged royal porridge of shredded meat, pounded whole wheat, lentils, and pure ghee simmered for 12 hours.",
                "typical_ordering_advice": "Traditionally prepared during Ramadan, also served year-round at Pista House and Sarvi."
            },
            {
                "dish": "Irani Chai & Osmania Biscuits",
                "cultural_context": "Thick caramelized milk decoction tea brought by Zoroastrian Persian immigrants in the early 20th century, paired with sweet-and-salty Osmania biscuits.",
                "typical_ordering_advice": "Drink standing outside Nimrah Cafe and Bakery facing the historic Charminar at sunrise."
            },
            {
                "dish": "Mirchi ka Salan",
                "cultural_context": "Spicy, nutty curry made with long green bhavnagri chilies, roasted peanuts, sesame seeds, coconut, and tamarind.",
                "typical_ordering_advice": "Essential accompaniment to authentic Dum Biryani, balancing rich spices with tangy tamarind."
            },
            {
                "dish": "Double ka Meetha",
                "cultural_context": "Decadent Hyderabadi bread pudding soaked in saffron-infused reduced milk (rabri), topped with fried cashews, almonds, and silver vark.",
                "typical_ordering_advice": "Traditional grand finale to Nizami wedding feasts and celebratory dinners."
            }
        ],
        "food_neighborhoods": [
            {"neighborhood": "Old City (Charminar & Laad Bazaar)", "vibe": "Narrow historic lanes with smoky kebabs, sweet shops, and century-old Irani tea counters."},
            {"neighborhood": "RTC X Roads & Musheerabad", "vibe": "Hub of iconic competing Biryani kitchens frequented by moviegoers and locals alike."},
            {"neighborhood": "Banjara Hills & Jubilee Hills", "vibe": "Refined modern Andhra and Telangana dining, microbreweries, and upscale Nizami fine-dining restaurants."}
        ]
    },
    "kerala": {
        "destination": "Kerala, India",
        "food_culture_summary": (
            "Kerala cuisine ('God's Own Country') is characterized by abundant use of coconut, black pepper, curry leaves, "
            "mustard seeds, and fresh seafood from the Malabar coast and backwaters. Meals balance vegetarian Sadya feasts "
            "served on banana leaves with spicy Malabar and Syrian Christian seafood and meat preparations."
        ),
        "signature_dishes": [
            {
                "dish": "Karimeen Pollichathu",
                "cultural_context": "Pearl spot fish marinated in shallots, ginger, garlic, and fiery red chili paste, wrapped tightly in a banana leaf and slow-roasted on a tawa.",
                "typical_ordering_advice": "Best enjoyed on a backwater houseboat or at traditional toddy shops (shappu) around Alappuzha and Kumarakom."
            },
            {
                "dish": "Kerala Sadya (Avial & Sambar)",
                "cultural_context": "Elaborate vegetarian feast with up to 24 dishes served on a fresh plantain leaf, centered on Avial, Thoran, Kalan, and red Matta rice.",
                "typical_ordering_advice": "Traditionally served for Onam and festive celebrations; order at Mothers Veg Plaza (Trivandrum) or Grand Hotel (Kochi)."
            },
            {
                "dish": "Appam with Vegetable or Mutton Stew",
                "cultural_context": "Fermented rice pancake with a soft, pillowy center and crispy lacy edges, paired with fragrant coconut-milk-based stew infused with whole spices.",
                "typical_ordering_advice": "Classic Syrian Christian breakfast staple, widely available across Fort Kochi bakeries and heritage cafes."
            },
            {
                "dish": "Malabar Porotta & Beef Roast / Pepper Fry",
                "cultural_context": "Flaky, multi-layered unleavened wheat flatbread paired with slow-roasted meat tossed in caramelized coconut flakes, green chilies, and curry leaves.",
                "typical_ordering_advice": "Iconic evening dinner street food at Malabar tea shops and Paragons in Kozhikode or Kochi."
            },
            {
                "dish": "Thalassery Biryani",
                "cultural_context": "Malabar Muslim fragrant biryani prepared with short-grain Kaima (Jeerakasala) rice, tender chicken or mutton, fried onions, cashews, and raisins.",
                "typical_ordering_advice": "Distinct from long-grain Hyderabadi Dum Biryani; try at Paragon or Kayees Rahmathullah Cafe in Mattancherry."
            }
        ],
        "food_neighborhoods": [
            {"neighborhood": "Fort Kochi & Mattancherry", "vibe": "Colonial cafe culture, Jewish spice market streets, and historic fresh fish grilled to order near Chinese Nets."},
            {"neighborhood": "Kozhikode (Calicut) Beach & SM Street", "vibe": "The culinary epicenter of Malabar: Halwa stalls, Banana chip fryers, and heritage biryani institutions."},
            {"neighborhood": "Alappuzha Backwaters & Canal Shacks", "vibe": "Floating kitchens, spicy clay-pot fish curry meals, and freshly caught lake prawns."}
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

