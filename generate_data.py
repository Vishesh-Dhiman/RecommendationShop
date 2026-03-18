import json, random, math

random.seed(42)

# ── Product definitions ───────────────────────────────────────────────────────
PRODUCTS_RAW = {
    "Electronics": {
        "Headphones": [
            {"name": "boAt Rockerz 450 Bluetooth Headphone",    "brand": "boAt",    "base_price": 1299,  "rating": 4.2, "tags": ["wireless","bass","over-ear"]},
            {"name": "boAt Rockerz 550 Bluetooth Headphone",    "brand": "boAt",    "base_price": 1799,  "rating": 4.3, "tags": ["wireless","bass","over-ear","40hr"]},
            {"name": "boAt Rockerz 650 ANC Headphone",         "brand": "boAt",    "base_price": 2999,  "rating": 4.4, "tags": ["anc","wireless","premium","over-ear"]},
            {"name": "Sony WH-1000XM4 Wireless Headphone",     "brand": "Sony",    "base_price": 19990, "rating": 4.7, "tags": ["anc","premium","wireless","30hr","hi-res"]},
            {"name": "Sony WH-CH720N Wireless Headphone",      "brand": "Sony",    "base_price": 9990,  "rating": 4.5, "tags": ["anc","wireless","lightweight","35hr"]},
            {"name": "JBL Tune 760NC Wireless Headphone",      "brand": "JBL",     "base_price": 4999,  "rating": 4.3, "tags": ["anc","wireless","50hr","foldable"]},
            {"name": "JBL Tune 510BT Wireless Headphone",      "brand": "JBL",     "base_price": 2499,  "rating": 4.2, "tags": ["wireless","40hr","foldable","on-ear"]},
            {"name": "Sennheiser HD 450BT Headphone",          "brand": "Sennheiser","base_price": 7990,"rating": 4.4, "tags": ["anc","wireless","30hr","premium"]},
            {"name": "Noise One Over Ear Headphone",           "brand": "Noise",   "base_price": 1499,  "rating": 4.0, "tags": ["wireless","32hr","foldable","budget"]},
            {"name": "PTron Basspods Passive Headphone",       "brand": "PTron",   "base_price": 599,   "rating": 3.8, "tags": ["wired","bass","budget","over-ear"]},
        ],
        "Earbuds": [
            {"name": "boAt Airdopes 141 TWS Earbuds",          "brand": "boAt",    "base_price": 899,   "rating": 4.1, "tags": ["tws","42hr","budget","wireless"]},
            {"name": "boAt Airdopes 181 TWS Earbuds",          "brand": "boAt",    "base_price": 1299,  "rating": 4.2, "tags": ["tws","enx","50hr","wireless"]},
            {"name": "boAt Airdopes 311 Pro TWS Earbuds",      "brand": "boAt",    "base_price": 1799,  "rating": 4.3, "tags": ["tws","anc","60hr","premium"]},
            {"name": "OnePlus Nord Buds 2",                    "brand": "OnePlus", "base_price": 2999,  "rating": 4.3, "tags": ["anc","36hr","tws","ip55"]},
            {"name": "OnePlus Buds Pro 2",                     "brand": "OnePlus", "base_price": 7999,  "rating": 4.5, "tags": ["anc","premium","39hr","tws"]},
            {"name": "realme Buds Air 5 Pro",                  "brand": "realme",  "base_price": 3999,  "rating": 4.3, "tags": ["anc","tws","38hr","ip55"]},
            {"name": "Noise Buds VS104 TWS Earbuds",           "brand": "Noise",   "base_price": 1299,  "rating": 4.0, "tags": ["tws","50hr","budget","ip44"]},
            {"name": "Sony WF-1000XM5 TWS Earbuds",           "brand": "Sony",    "base_price": 24990, "rating": 4.7, "tags": ["anc","premium","36hr","hi-res"]},
            {"name": "Samsung Galaxy Buds2 Pro",               "brand": "Samsung", "base_price": 9999,  "rating": 4.5, "tags": ["anc","hi-fi","29hr","tws"]},
            {"name": "JBL Wave Beam TWS Earbuds",              "brand": "JBL",     "base_price": 1999,  "rating": 4.1, "tags": ["tws","32hr","ip54","budget"]},
        ],
        "Smartphones": [
            {"name": "Redmi Note 13 5G (128GB)",               "brand": "Redmi",   "base_price": 14999, "rating": 4.3, "tags": ["5g","120hz","108mp","budget"]},
            {"name": "Redmi Note 13 Pro 5G (256GB)",           "brand": "Redmi",   "base_price": 21999, "rating": 4.4, "tags": ["5g","200mp","amoled","67w"]},
            {"name": "Redmi Note 13 Pro+ 5G (256GB)",         "brand": "Redmi",   "base_price": 26999, "rating": 4.5, "tags": ["5g","200mp","amoled","120w","curved"]},
            {"name": "realme 12 Pro+ 5G (256GB)",              "brand": "realme",  "base_price": 27999, "rating": 4.4, "tags": ["5g","periscope","67w","amoled"]},
            {"name": "POCO X6 Pro 5G (256GB)",                 "brand": "POCO",    "base_price": 22999, "rating": 4.5, "tags": ["5g","gaming","144hz","67w"]},
            {"name": "Samsung Galaxy A55 5G (256GB)",          "brand": "Samsung", "base_price": 32999, "rating": 4.4, "tags": ["5g","amoled","50mp","ip67"]},
            {"name": "Samsung Galaxy A35 5G (256GB)",          "brand": "Samsung", "base_price": 24999, "rating": 4.3, "tags": ["5g","amoled","50mp","waterproof"]},
            {"name": "iQOO Z9 5G (128GB)",                     "brand": "iQOO",    "base_price": 17999, "rating": 4.4, "tags": ["5g","gaming","44w","amoled"]},
            {"name": "OnePlus Nord CE4 5G (256GB)",            "brand": "OnePlus", "base_price": 24999, "rating": 4.3, "tags": ["5g","100w","amoled","50mp"]},
            {"name": "Motorola Edge 50 Fusion 5G",             "brand": "Motorola","base_price": 22999, "rating": 4.2, "tags": ["5g","68w","pmoled","ip68"]},
        ],
        "Smartwatches": [
            {"name": "boAt Wave Call 2 Smartwatch",            "brand": "boAt",    "base_price": 1499,  "rating": 4.0, "tags": ["calling","7day","budget","1.83inch"]},
            {"name": "boAt Ultima Vertex Smartwatch",          "brand": "boAt",    "base_price": 2499,  "rating": 4.1, "tags": ["amoled","calling","100sports","bluetooth"]},
            {"name": "Noise ColorFit Ultra 3 Smartwatch",      "brand": "Noise",   "base_price": 3499,  "rating": 4.2, "tags": ["amoled","calling","bt","gps"]},
            {"name": "Noise ColorFit Caliber Smartwatch",      "brand": "Noise",   "base_price": 1799,  "rating": 4.0, "tags": ["1.69inch","7day","calling","budget"]},
            {"name": "Samsung Galaxy Watch6 44mm",             "brand": "Samsung", "base_price": 26999, "rating": 4.5, "tags": ["health","gps","premium","amoled"]},
            {"name": "Amazfit GTR 4 Smartwatch",               "brand": "Amazfit", "base_price": 11999, "rating": 4.3, "tags": ["gps","14day","amoled","150sports"]},
            {"name": "Amazfit Bip 5 Smartwatch",               "brand": "Amazfit", "base_price": 5999,  "rating": 4.2, "tags": ["10day","calls","large-display","budget"]},
            {"name": "Fire-Boltt Ninja Call Pro Plus",         "brand": "Fire-Boltt","base_price": 1299,"rating": 3.9, "tags": ["calling","budget","7day","1.83inch"]},
            {"name": "Titan Smart 2 Smartwatch",               "brand": "Titan",   "base_price": 7999,  "rating": 4.2, "tags": ["calling","premium","sleep","Indian-brand"]},
            {"name": "Fastrack Optimus Pro 2 Smartwatch",      "brand": "Fastrack","base_price": 3999,  "rating": 4.0, "tags": ["calling","100sports","Indian-brand","amoled"]},
        ],
        "Laptops": [
            {"name": "Lenovo IdeaPad Slim 3 (i5 13th Gen)",   "brand": "Lenovo",  "base_price": 44990, "rating": 4.3, "tags": ["student","intel","15.6inch","512gb"]},
            {"name": "Lenovo IdeaPad Slim 5 (Ryzen 7)",       "brand": "Lenovo",  "base_price": 54990, "rating": 4.4, "tags": ["amd","thin","16inch","1tb","oled"]},
            {"name": "HP Pavilion 15 (i5 13th Gen)",          "brand": "HP",      "base_price": 49990, "rating": 4.2, "tags": ["student","intel","15.6inch","fhd"]},
            {"name": "HP 15s (Ryzen 5 7520U)",                "brand": "HP",      "base_price": 39990, "rating": 4.3, "tags": ["amd","budget","student","8gb"]},
            {"name": "ASUS VivoBook 16X (i5 13th Gen)",       "brand": "ASUS",    "base_price": 57990, "rating": 4.4, "tags": ["16inch","fhd","oled","intel"]},
            {"name": "ASUS ROG Strix G15 (Ryzen 9)",          "brand": "ASUS",    "base_price": 99990, "rating": 4.6, "tags": ["gaming","144hz","rtx4070","premium"]},
            {"name": "Acer Aspire Lite (Ryzen 5)",            "brand": "Acer",    "base_price": 36990, "rating": 4.1, "tags": ["budget","amd","student","thin"]},
            {"name": "Dell Inspiron 15 (i5 12th Gen)",        "brand": "Dell",    "base_price": 52990, "rating": 4.3, "tags": ["intel","fhd","office","reliable"]},
            {"name": "Apple MacBook Air M2",                  "brand": "Apple",   "base_price": 99900, "rating": 4.8, "tags": ["m2","premium","thin","macos","18hr"]},
            {"name": "MSI Thin GF63 Gaming Laptop",           "brand": "MSI",     "base_price": 64990, "rating": 4.3, "tags": ["gaming","144hz","rtx4050","i5"]},
        ],
    },
    "Fashion": {
        "Men's T-Shirts": [
            {"name": "Allen Solly Men's Regular Fit T-Shirt",  "brand": "Allen Solly","base_price": 699,  "rating": 4.2, "tags": ["cotton","regular","office","men"]},
            {"name": "Allen Solly Men's Polo T-Shirt",         "brand": "Allen Solly","base_price": 899,  "rating": 4.3, "tags": ["polo","cotton","men","collar"]},
            {"name": "Raymond Men's Solid T-Shirt",            "brand": "Raymond", "base_price": 799,   "rating": 4.1, "tags": ["cotton","solid","men","premium"]},
            {"name": "US Polo Assn Men's Polo T-Shirt",        "brand": "US Polo", "base_price": 1299,  "rating": 4.4, "tags": ["polo","premium","men","cotton"]},
            {"name": "Van Heusen Men's Regular Fit T-Shirt",   "brand": "Van Heusen","base_price": 799, "rating": 4.2, "tags": ["regular","men","cotton","office"]},
            {"name": "Roadster Men's Graphic T-Shirt",         "brand": "Roadster","base_price": 499,   "rating": 4.0, "tags": ["graphic","casual","men","budget"]},
            {"name": "HRX Men's Dry-Fit T-Shirt",              "brand": "HRX",     "base_price": 599,   "rating": 4.1, "tags": ["sports","dryfit","men","gym"]},
            {"name": "Puma Men's Solid Regular T-Shirt",       "brand": "Puma",    "base_price": 799,   "rating": 4.3, "tags": ["sports","regular","men","premium"]},
            {"name": "Nike Dri-FIT Men's T-Shirt",             "brand": "Nike",    "base_price": 1499,  "rating": 4.5, "tags": ["sports","dri-fit","men","premium"]},
            {"name": "Adidas Men's Training T-Shirt",          "brand": "Adidas",  "base_price": 1299,  "rating": 4.4, "tags": ["sports","training","men","adidas"]},
        ],
        "Men's Jeans": [
            {"name": "Levi's 511 Slim Fit Men's Jeans",        "brand": "Levi's",  "base_price": 2499,  "rating": 4.5, "tags": ["slim","denim","men","premium"]},
            {"name": "Levi's 514 Regular Fit Men's Jeans",     "brand": "Levi's",  "base_price": 2299,  "rating": 4.4, "tags": ["regular","denim","men","premium"]},
            {"name": "Pepe Jeans Men's Slim Fit Jeans",        "brand": "Pepe",    "base_price": 1999,  "rating": 4.3, "tags": ["slim","denim","men","stretchable"]},
            {"name": "Roadster Men's Skinny Fit Jeans",        "brand": "Roadster","base_price": 999,   "rating": 4.0, "tags": ["skinny","denim","men","budget"]},
            {"name": "Flying Machine Men's Slim Fit Jeans",    "brand": "Flying Machine","base_price": 1499,"rating": 4.2, "tags": ["slim","denim","men","mid-rise"]},
            {"name": "Wrangler Men's Regular Fit Jeans",       "brand": "Wrangler","base_price": 1799,  "rating": 4.3, "tags": ["regular","denim","men","sturdy"]},
            {"name": "Lee Men's Regular Fit Jeans",            "brand": "Lee",     "base_price": 1999,  "rating": 4.3, "tags": ["regular","denim","men","stretchable"]},
            {"name": "Jack & Jones Men's Slim Fit Jeans",      "brand": "Jack & Jones","base_price": 2499,"rating": 4.4, "tags": ["slim","premium","men","denim"]},
            {"name": "H&M Men's Slim Fit Jeans",               "brand": "H&M",     "base_price": 1999,  "rating": 4.2, "tags": ["slim","budget","men","denim"]},
            {"name": "Spykar Men's Skinny Fit Jeans",          "brand": "Spykar",  "base_price": 1699,  "rating": 4.1, "tags": ["skinny","denim","men","Indian-brand"]},
        ],
        "Women's Kurtas": [
            {"name": "Biba Women's Straight Kurta",            "brand": "Biba",    "base_price": 1299,  "rating": 4.4, "tags": ["ethnic","cotton","women","straight"]},
            {"name": "Biba Women's Floral Print Kurta",        "brand": "Biba",    "base_price": 1499,  "rating": 4.5, "tags": ["ethnic","floral","women","festive"]},
            {"name": "W Women's Solid Straight Kurta",         "brand": "W",       "base_price": 1099,  "rating": 4.3, "tags": ["ethnic","solid","women","regular"]},
            {"name": "Libas Women's Straight Kurta",           "brand": "Libas",   "base_price": 799,   "rating": 4.2, "tags": ["ethnic","budget","women","cotton"]},
            {"name": "Varanga Women's A-Line Kurta",           "brand": "Varanga", "base_price": 999,   "rating": 4.3, "tags": ["ethnic","a-line","women","printed"]},
            {"name": "Global Desi Women's Printed Kurta",      "brand": "Global Desi","base_price": 1399,"rating": 4.4, "tags": ["ethnic","printed","women","boho"]},
            {"name": "Aurelia Women's Flared Kurta",           "brand": "Aurelia", "base_price": 1699,  "rating": 4.5, "tags": ["ethnic","flared","women","festive"]},
            {"name": "Sangria Women's Embroidered Kurta",      "brand": "Sangria", "base_price": 1199,  "rating": 4.3, "tags": ["ethnic","embroidered","women","party"]},
            {"name": "Jaipur Kurti Women's Cotton Kurta",      "brand": "Jaipur Kurti","base_price": 699,"rating": 4.2, "tags": ["ethnic","cotton","women","Indian"]},
            {"name": "Nayo Women's Anarkali Kurta",            "brand": "Nayo",    "base_price": 899,   "rating": 4.1, "tags": ["ethnic","anarkali","women","festive"]},
        ],
        "Sneakers": [
            {"name": "Nike Air Max 270 Men's Sneakers",        "brand": "Nike",    "base_price": 10995, "rating": 4.6, "tags": ["running","premium","men","airmax"]},
            {"name": "Nike Revolution 7 Men's Sneakers",       "brand": "Nike",    "base_price": 3995,  "rating": 4.4, "tags": ["running","men","lightweight","budget"]},
            {"name": "Adidas Ultraboost 22 Sneakers",          "brand": "Adidas",  "base_price": 14999, "rating": 4.7, "tags": ["running","premium","boost","men"]},
            {"name": "Adidas Duramo SL Sneakers",              "brand": "Adidas",  "base_price": 2999,  "rating": 4.3, "tags": ["running","budget","men","lightweight"]},
            {"name": "Puma Anzarun Lite Sneakers",             "brand": "Puma",    "base_price": 2499,  "rating": 4.3, "tags": ["casual","men","budget","versatile"]},
            {"name": "Skechers Go Walk 7 Sneakers",            "brand": "Skechers","base_price": 3999,  "rating": 4.4, "tags": ["walking","comfort","men","memory-foam"]},
            {"name": "Reebok Classic Leather Sneakers",        "brand": "Reebok",  "base_price": 5999,  "rating": 4.4, "tags": ["classic","leather","men","retro"]},
            {"name": "Campus Men's Running Shoes",             "brand": "Campus",  "base_price": 899,   "rating": 4.0, "tags": ["running","budget","men","Indian"]},
            {"name": "Sparx Men's Running Shoes",              "brand": "Sparx",   "base_price": 699,   "rating": 3.9, "tags": ["running","budget","men","Indian"]},
            {"name": "New Balance Fresh Foam 1080 Sneakers",   "brand": "New Balance","base_price": 13999,"rating": 4.6, "tags": ["running","premium","cushion","men"]},
        ],
    },
    "Books": {
        "Self-Help": [
            {"name": "Atomic Habits by James Clear",           "brand": "Penguin", "base_price": 399,   "rating": 4.8, "tags": ["habits","productivity","bestseller","english"]},
            {"name": "The Psychology of Money",                "brand": "Jaico",   "base_price": 349,   "rating": 4.7, "tags": ["finance","money","bestseller","english"]},
            {"name": "Think and Grow Rich",                    "brand": "Fingerprint","base_price": 199, "rating": 4.5, "tags": ["motivation","money","classic","english"]},
            {"name": "Rich Dad Poor Dad",                      "brand": "Manjul",  "base_price": 249,   "rating": 4.6, "tags": ["finance","investment","classic","english"]},
            {"name": "The 5 AM Club by Robin Sharma",          "brand": "Jaico",   "base_price": 299,   "rating": 4.4, "tags": ["morning","routine","productivity","english"]},
            {"name": "Ikigai by Hector Garcia",                "brand": "Hachette","base_price": 299,   "rating": 4.6, "tags": ["life","purpose","japanese","english"]},
            {"name": "The Subtle Art of Not Giving a F*ck",   "brand": "HarperCollins","base_price": 349,"rating": 4.5, "tags": ["mindset","life","bestseller","english"]},
            {"name": "Deep Work by Cal Newport",               "brand": "Piatkus", "base_price": 449,   "rating": 4.6, "tags": ["focus","productivity","career","english"]},
            {"name": "Sochiye Aur Amir Baniye (Hindi)",        "brand": "Manjul",  "base_price": 149,   "rating": 4.4, "tags": ["motivation","hindi","classic","money"]},
            {"name": "Lok Vyavhar by Dale Carnegie (Hindi)",   "brand": "Diamond", "base_price": 199,   "rating": 4.6, "tags": ["personality","hindi","relations","classic"]},
        ],
        "Technical": [
            {"name": "Python Crash Course by Eric Matthes",    "brand": "No Starch","base_price": 649,  "rating": 4.7, "tags": ["python","coding","beginner","programming"]},
            {"name": "Let Us C by Yashavant Kanetkar",         "brand": "BPB",     "base_price": 399,   "rating": 4.5, "tags": ["c","programming","engineering","Indian"]},
            {"name": "Data Structures by Reema Thareja",       "brand": "Oxford",  "base_price": 599,   "rating": 4.3, "tags": ["dsa","engineering","cs","textbook"]},
            {"name": "Head First Java",                        "brand": "O'Reilly","base_price": 849,   "rating": 4.6, "tags": ["java","oop","beginner","programming"]},
            {"name": "Introduction to Algorithms (CLRS)",      "brand": "MIT Press","base_price": 999,  "rating": 4.7, "tags": ["algorithms","advanced","cs","reference"]},
            {"name": "The Web Developer Bootcamp (Udemy Book)","brand": "Packt",   "base_price": 499,   "rating": 4.4, "tags": ["web","html","css","js","beginner"]},
            {"name": "Machine Learning by Tom Mitchell",       "brand": "McGraw",  "base_price": 749,   "rating": 4.5, "tags": ["ml","ai","engineering","advanced"]},
            {"name": "Clean Code by Robert C. Martin",         "brand": "Pearson", "base_price": 799,   "rating": 4.7, "tags": ["coding","bestpractice","professional","career"]},
            {"name": "Computer Networks by Tanenbaum",         "brand": "Pearson", "base_price": 649,   "rating": 4.4, "tags": ["networking","engineering","textbook","cs"]},
            {"name": "Operating System Concepts (Galvin)",     "brand": "Wiley",   "base_price": 899,   "rating": 4.5, "tags": ["os","engineering","textbook","cs"]},
        ],
        "Fiction": [
            {"name": "The Alchemist by Paulo Coelho",          "brand": "HarperCollins","base_price": 199,"rating": 4.7, "tags": ["fiction","classic","inspirational","english"]},
            {"name": "Harry Potter Box Set (7 Books)",         "brand": "Bloomsbury","base_price": 2499, "rating": 4.9, "tags": ["fiction","fantasy","series","english"]},
            {"name": "The God of Small Things",                "brand": "Penguin", "base_price": 299,   "rating": 4.5, "tags": ["fiction","Indian","booker","english"]},
            {"name": "2 States by Chetan Bhagat",              "brand": "Rupa",    "base_price": 199,   "rating": 4.3, "tags": ["fiction","Indian","romance","hindi-english"]},
            {"name": "Five Point Someone by Chetan Bhagat",    "brand": "Rupa",    "base_price": 175,   "rating": 4.2, "tags": ["fiction","Indian","college","english"]},
            {"name": "The White Tiger by Aravind Adiga",       "brand": "HarperCollins","base_price": 299,"rating": 4.4, "tags": ["fiction","Indian","booker","english"]},
            {"name": "Mujhe Pehchano by Sudha Murthy (Hindi)", "brand": "Penguin", "base_price": 199,   "rating": 4.5, "tags": ["fiction","Indian","hindi","inspirational"]},
            {"name": "Devdas by Sarat Chandra (Hindi)",        "brand": "Rajpal",  "base_price": 149,   "rating": 4.3, "tags": ["fiction","classic","hindi","Indian"]},
            {"name": "Godan by Munshi Premchand (Hindi)",      "brand": "Lokbharti","base_price": 199,  "rating": 4.6, "tags": ["fiction","hindi","classic","Indian"]},
            {"name": "The Immortals of Meluha by Amish",       "brand": "Westland","base_price": 299,   "rating": 4.5, "tags": ["fiction","Indian","mythology","fantasy"]},
        ],
    },
    "Home & Kitchen": {
        "Kitchen Appliances": [
            {"name": "Prestige Iris 750W Mixer Grinder",       "brand": "Prestige","base_price": 2299,  "rating": 4.3, "tags": ["mixer","Indian","kitchen","750w"]},
            {"name": "Prestige Delight 1.5L Electric Kettle",  "brand": "Prestige","base_price": 799,   "rating": 4.4, "tags": ["kettle","electric","kitchen","Indian"]},
            {"name": "Bajaj Rex 500W Mixer Grinder",           "brand": "Bajaj",   "base_price": 1799,  "rating": 4.2, "tags": ["mixer","Indian","kitchen","500w","budget"]},
            {"name": "Philips HL7756 750W Mixer Grinder",      "brand": "Philips", "base_price": 3499,  "rating": 4.5, "tags": ["mixer","premium","kitchen","750w"]},
            {"name": "Havells Cesta 1.7L Electric Kettle",     "brand": "Havells", "base_price": 999,   "rating": 4.3, "tags": ["kettle","electric","kitchen","1.7l"]},
            {"name": "Morphy Richards ICON 1.7L Kettle",       "brand": "Morphy Richards","base_price": 1299,"rating": 4.4, "tags": ["kettle","glass","kitchen","premium"]},
            {"name": "Kent Atta Maker 2L",                     "brand": "Kent",    "base_price": 3499,  "rating": 4.3, "tags": ["atta-maker","Indian","kitchen","2l"]},
            {"name": "Pigeon Amaze 1.5L Induction Cooktop",    "brand": "Pigeon",  "base_price": 1299,  "rating": 4.2, "tags": ["induction","Indian","kitchen","budget"]},
            {"name": "Prestige PIC 15.0+ Induction Cooktop",   "brand": "Prestige","base_price": 2299,  "rating": 4.4, "tags": ["induction","Indian","kitchen","2000w"]},
            {"name": "LG MS2043DB 20L Microwave Oven",         "brand": "LG",      "base_price": 5999,  "rating": 4.4, "tags": ["microwave","kitchen","20l","solo"]},
        ],
        "Bedding": [
            {"name": "Swayam Cotton Double Bedsheet",          "brand": "Swayam",  "base_price": 799,   "rating": 4.2, "tags": ["cotton","double","bedsheet","Indian"]},
            {"name": "Bombay Dyeing Cotton Double Bedsheet",   "brand": "Bombay Dyeing","base_price": 1199,"rating": 4.4, "tags": ["cotton","double","premium","Indian"]},
            {"name": "D'Decor 100% Cotton Bedsheet",           "brand": "D'Decor", "base_price": 1499,  "rating": 4.5, "tags": ["cotton","premium","double","soft"]},
            {"name": "Story@Home Microfiber Double Bedsheet",  "brand": "Story@Home","base_price": 599,  "rating": 4.1, "tags": ["microfiber","budget","double","bedsheet"]},
            {"name": "Wakefit Orthopedic Memory Foam Pillow",  "brand": "Wakefit", "base_price": 1299,  "rating": 4.5, "tags": ["pillow","memory-foam","orthopedic","sleep"]},
            {"name": "Sleepyhead Original 3-Layer Foam Pillow","brand": "Sleepyhead","base_price": 999,  "rating": 4.4, "tags": ["pillow","foam","sleep","comfort"]},
            {"name": "DODO Comfy Fibre Filled Quilt",          "brand": "DODO",    "base_price": 1499,  "rating": 4.3, "tags": ["quilt","winter","double","soft"]},
            {"name": "Raymond Home Striped Blanket",           "brand": "Raymond", "base_price": 999,   "rating": 4.3, "tags": ["blanket","winter","premium","Indian"]},
            {"name": "Trident Cotton Bath Towel Set",          "brand": "Trident", "base_price": 799,   "rating": 4.3, "tags": ["towel","cotton","bathroom","Indian"]},
            {"name": "Spaces Atrium Cotton Bath Towel",        "brand": "Spaces",  "base_price": 599,   "rating": 4.2, "tags": ["towel","cotton","bathroom","soft"]},
        ],
    },
    "Sports & Fitness": {
        "Fitness Equipment": [
            {"name": "Boldfit Resistance Bands Set (5 bands)", "brand": "Boldfit", "base_price": 599,   "rating": 4.3, "tags": ["resistance","fitness","home-gym","budget"]},
            {"name": "Boldfit Pro Skipping Rope",              "brand": "Boldfit", "base_price": 299,   "rating": 4.2, "tags": ["skipping","cardio","fitness","budget"]},
            {"name": "Lifelong Yoga Mat (6mm)",                "brand": "Lifelong","base_price": 499,   "rating": 4.2, "tags": ["yoga","mat","fitness","6mm"]},
            {"name": "Strauss Yoga Mat (8mm) Anti-Slip",       "brand": "Strauss", "base_price": 699,   "rating": 4.4, "tags": ["yoga","mat","anti-slip","8mm"]},
            {"name": "Kore K-DM-15 15kg Dumbbell Set",        "brand": "Kore",    "base_price": 999,   "rating": 4.1, "tags": ["dumbbell","home-gym","15kg","fitness"]},
            {"name": "Powermark PB-1000 Adjustable Dumbbell", "brand": "Powermark","base_price": 3499, "rating": 4.4, "tags": ["dumbbell","adjustable","premium","home-gym"]},
            {"name": "Nivia Storm Football (Size 5)",          "brand": "Nivia",   "base_price": 699,   "rating": 4.3, "tags": ["football","outdoor","size5","Indian"]},
            {"name": "SG Cricket Bat English Willow",          "brand": "SG",      "base_price": 1999,  "rating": 4.4, "tags": ["cricket","bat","english-willow","Indian"]},
            {"name": "Cosco Jump Rope with Counter",           "brand": "Cosco",   "base_price": 399,   "rating": 4.2, "tags": ["skipping","counter","fitness","Indian"]},
            {"name": "Rx Zeal Adjustable Dumbbell 20kg",       "brand": "Rx Zeal","base_price": 4999,  "rating": 4.5, "tags": ["dumbbell","adjustable","20kg","premium"]},
        ],
        "Sports Nutrition": [
            {"name": "MuscleBlaze Whey Protein 1kg (Chocolate)","brand": "MuscleBlaze","base_price": 1799,"rating": 4.5, "tags": ["whey","protein","chocolate","1kg","Indian"]},
            {"name": "MuscleBlaze Whey Protein 2kg (Chocolate)","brand": "MuscleBlaze","base_price": 3299,"rating": 4.5, "tags": ["whey","protein","chocolate","2kg","Indian"]},
            {"name": "MuscleBlaze Raw Whey 1kg Unflavoured",   "brand": "MuscleBlaze","base_price": 1499,"rating": 4.4, "tags": ["whey","raw","unflavoured","1kg","Indian"]},
            {"name": "Optimum Nutrition Gold Standard 1kg",    "brand": "ON",      "base_price": 3299,  "rating": 4.7, "tags": ["whey","premium","1kg","imported","gold"]},
            {"name": "Optimum Nutrition Gold Standard 2kg",    "brand": "ON",      "base_price": 5999,  "rating": 4.7, "tags": ["whey","premium","2kg","imported","gold"]},
            {"name": "Fast&Up Reload Electrolyte (20 tabs)",   "brand": "Fast&Up", "base_price": 199,   "rating": 4.4, "tags": ["electrolyte","hydration","sports","Indian"]},
            {"name": "HealthKart HK Vitals Multivitamin 60tab","brand": "HK Vitals","base_price": 399,  "rating": 4.3, "tags": ["multivitamin","health","60tabs","Indian"]},
            {"name": "Nakpro Creatine Monohydrate 300g",       "brand": "Nakpro",  "base_price": 799,   "rating": 4.4, "tags": ["creatine","strength","300g","Indian"]},
            {"name": "Gritzo SuperMilk Night Protein (Kids)",  "brand": "Gritzo",  "base_price": 999,   "rating": 4.3, "tags": ["kids","protein","night","chocolate"]},
            {"name": "Oziva Protein & Herbs for Women 1kg",    "brand": "Oziva",   "base_price": 1599,  "rating": 4.4, "tags": ["women","protein","herbs","1kg","Indian"]},
        ],
    },
    "Beauty & Personal Care": {
        "Skincare": [
            {"name": "Dot & Key Vitamin C Serum 30ml",         "brand": "Dot & Key","base_price": 595,  "rating": 4.5, "tags": ["serum","vitamin-c","brightening","Indian"]},
            {"name": "Minimalist Niacinamide 10% Serum 30ml",  "brand": "Minimalist","base_price": 399, "rating": 4.6, "tags": ["serum","niacinamide","pores","Indian"]},
            {"name": "Minimalist Vitamin C 10% Serum 30ml",    "brand": "Minimalist","base_price": 349, "rating": 4.5, "tags": ["serum","vitamin-c","brightening","Indian"]},
            {"name": "Plum Bright Years Cell Renewal Serum",   "brand": "Plum",    "base_price": 695,   "rating": 4.4, "tags": ["serum","anti-aging","vegan","Indian"]},
            {"name": "Neutrogena Oil-Free Acne Wash 200ml",    "brand": "Neutrogena","base_price": 599, "rating": 4.4, "tags": ["facewash","acne","oil-free","imported"]},
            {"name": "Cetaphil Gentle Skin Cleanser 500ml",    "brand": "Cetaphil","base_price": 699,   "rating": 4.6, "tags": ["cleanser","sensitive","gentle","imported"]},
            {"name": "Lakme 9to5 Moisturizer SPF 30 50g",      "brand": "Lakme",   "base_price": 249,   "rating": 4.3, "tags": ["moisturizer","spf30","Indian","daily"]},
            {"name": "Lotus Herbals Safe Sun SPF 70 100g",     "brand": "Lotus",   "base_price": 399,   "rating": 4.4, "tags": ["sunscreen","spf70","Indian","herbal"]},
            {"name": "Mamaearth Vitamin C Face Cream 50g",     "brand": "Mamaearth","base_price": 349,  "rating": 4.3, "tags": ["cream","vitamin-c","Indian","toxinfree"]},
            {"name": "Forest Essentials Face Moisturiser 50ml","brand": "Forest Essentials","base_price": 1650,"rating": 4.6, "tags": ["premium","ayurvedic","moisturiser","Indian"]},
        ],
        "Hair Care": [
            {"name": "Indulekha Bhringa Hair Oil 100ml",       "brand": "Indulekha","base_price": 299,  "rating": 4.4, "tags": ["hair-oil","ayurvedic","Indian","growth"]},
            {"name": "Mamaearth Onion Hair Oil 250ml",         "brand": "Mamaearth","base_price": 349,  "rating": 4.3, "tags": ["hair-oil","onion","Indian","growth"]},
            {"name": "WOW Skin Science Onion Oil 200ml",       "brand": "WOW",     "base_price": 399,   "rating": 4.3, "tags": ["hair-oil","onion","Indian","growth"]},
            {"name": "Parachute Advansed Coconut Hair Oil 300ml","brand": "Parachute","base_price": 149,"rating": 4.5, "tags": ["coconut-oil","Indian","classic","hair"]},
            {"name": "L'Oreal Paris Total Repair 5 Shampoo",   "brand": "L'Oreal", "base_price": 349,   "rating": 4.4, "tags": ["shampoo","repair","imported","damage"]},
            {"name": "Dove Intense Repair Shampoo 650ml",      "brand": "Dove",    "base_price": 349,   "rating": 4.4, "tags": ["shampoo","repair","damage","650ml"]},
            {"name": "Tresemme Keratin Smooth Shampoo 580ml",  "brand": "Tresemme","base_price": 399,   "rating": 4.3, "tags": ["shampoo","keratin","smooth","580ml"]},
            {"name": "Biotique Bio Green Apple Shampoo 340ml", "brand": "Biotique","base_price": 199,   "rating": 4.2, "tags": ["shampoo","herbal","Indian","budget"]},
            {"name": "Wow Apple Cider Vinegar Shampoo 300ml",  "brand": "WOW",     "base_price": 349,   "rating": 4.3, "tags": ["shampoo","acv","scalp","Indian"]},
            {"name": "Pantene Pro-V Anti Hair Fall Shampoo 650ml","brand": "Pantene","base_price": 399, "rating": 4.3, "tags": ["shampoo","anti-hairfall","630ml","repair"]},
        ],
    },
}

# ── Build flat product list ───────────────────────────────────────────────────
products = []
pid = 1

COLORS_BY_CAT = {
    "Electronics":          "#E8F4FD",
    "Fashion":              "#FEF9E7",
    "Books":                "#EAFAF1",
    "Home & Kitchen":       "#FDF2F8",
    "Sports & Fitness":     "#FEF5E7",
    "Beauty & Personal Care":"#F9EBEA",
}

for category, subcats in PRODUCTS_RAW.items():
    for subcategory, items in subcats.items():
        for item in items:
            # popularity: based on rating + some noise
            popularity = round(item["rating"] * 1000 + random.randint(200, 5000))
            reviews    = random.randint(150, 12000)
            discount   = random.choice([0, 5, 10, 10, 15, 15, 20, 20, 25, 30])
            mrp        = round(item["base_price"] * (1 + discount / 100))

            products.append({
                "id":          pid,
                "name":        item["name"],
                "brand":       item["brand"],
                "category":    category,
                "subcategory": subcategory,
                "price":       item["base_price"],
                "mrp":         mrp,
                "discount":    discount,
                "rating":      item["rating"],
                "reviews":     reviews,
                "popularity":  popularity,
                "tags":        item["tags"],
                "color_hex":   COLORS_BY_CAT[category],
                "in_stock":    True,
                "description": f"{item['name']} by {item['brand']}. Category: {subcategory}. Tags: {', '.join(item['tags'])}.",
            })
            pid += 1

print(f"Total products: {len(products)}")

# ── Users ─────────────────────────────────────────────────────────────────────
users = [
    {
        "id": "u1", "username": "rahul_tech", "password": "rahul123",
        "name": "Rahul Sharma", "avatar": "RS",
        "interests": ["Electronics", "Books"],
        "viewed": [1, 2, 11, 31, 41, 51, 61],
        "cart":   [3, 32],
        "searched": ["headphone", "python", "laptop"],
        "purchases": [2, 12, 62],
    },
    {
        "id": "u2", "username": "priya_fashion", "password": "priya123",
        "name": "Priya Singh", "avatar": "PS",
        "interests": ["Fashion", "Beauty & Personal Care"],
        "viewed": [101, 102, 111, 121, 131, 141, 151],
        "cart":   [103, 122],
        "searched": ["kurta", "serum", "sneakers"],
        "purchases": [104, 112, 152],
    },
    {
        "id": "u3", "username": "amit_fitness", "password": "amit123",
        "name": "Amit Kumar", "avatar": "AK",
        "interests": ["Sports & Fitness", "Electronics"],
        "viewed": [181, 182, 191, 1, 21, 31],
        "cart":   [183, 192],
        "searched": ["protein", "dumbbell", "smartwatch"],
        "purchases": [184, 193, 41],
    },
    {
        "id": "u4", "username": "sneha_home", "password": "sneha123",
        "name": "Sneha Patel", "avatar": "SP",
        "interests": ["Home & Kitchen", "Beauty & Personal Care"],
        "viewed": [161, 162, 171, 151, 152],
        "cart":   [163, 172],
        "searched": ["mixer", "bedsheet", "sunscreen"],
        "purchases": [164, 173, 153],
    },
    {
        "id": "u5", "username": "vikram_gamer", "password": "vikram123",
        "name": "Vikram Rao", "avatar": "VR",
        "interests": ["Electronics", "Sports & Fitness"],
        "viewed": [61, 62, 21, 51, 181],
        "cart":   [63, 22],
        "searched": ["gaming laptop", "earbuds", "protein"],
        "purchases": [64, 23, 182],
    },
    {
        "id": "u6", "username": "ananya_books", "password": "ananya123",
        "name": "Ananya Verma", "avatar": "AV",
        "interests": ["Books", "Fashion"],
        "viewed": [141, 142, 143, 101, 121],
        "cart":   [144, 102],
        "searched": ["self help", "novel", "kurta"],
        "purchases": [145, 103, 122],
    },
    {
        "id": "u7", "username": "rohit_budget", "password": "rohit123",
        "name": "Rohit Gupta", "avatar": "RG",
        "interests": ["Electronics", "Fashion", "Books"],
        "viewed": [10, 20, 30, 110, 140],
        "cart":   [10, 110],
        "searched": ["budget phone", "jeans", "hindi book"],
        "purchases": [140, 130],
    },
    {
        "id": "u8", "username": "Navya_beauty", "password": "navya123",
        "name": "Navya Sharma", "avatar": "NS",
        "interests": ["Beauty & Personal Care", "Fashion"],
        "viewed": [151, 152, 153, 154, 101, 111],
        "cart":   [155, 156],
        "searched": ["niacinamide", "vitamin c", "hair oil"],
        "purchases": [157, 158, 112],
    },
]

# Save both files
with open("/home/claude/ecommerce/data/products.json", "w") as f:
    json.dump(products, f, indent=2, ensure_ascii=False)

with open("/home/claude/ecommerce/data/users.json", "w") as f:
    json.dump(users, f, indent=2, ensure_ascii=False)

print(f"Products saved: {len(products)}")
print(f"Users saved:    {len(users)}")
print(f"Categories:     {list(PRODUCTS_RAW.keys())}")
