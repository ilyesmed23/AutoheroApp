import re
import datetime

# --- CONFIGURATION DES MARQUES ---
BASE_SEARCH_URL = "https://www.autohero.com/fr/v1/search/?brand0="

BRAND_CONFIGS = {
    "abarth": {"search_url": BASE_SEARCH_URL + "Abarth", "brand_name": "Abarth", "model_order": ["595", "695", "500"]},
    "alfaromeo": {"search_url": BASE_SEARCH_URL + "Alfa%20Romeo", "brand_name": "Alfa Romeo", "model_order": ["Giulia", "Stelvio", "Tonale", "Giulietta"]},
    "audi": {
        "search_url": BASE_SEARCH_URL + "Audi",
        "brand_name": "Audi",
        "model_order": ["A1", "A3", "A4", "A5", "A6", "A7", "Q2", "Q3", "Q4", "Q5", "Q7", "Q8", "e-tron"]
    },
    "bmw": {
        "search_url": BASE_SEARCH_URL + "BMW",
        "brand_name": "BMW",
        "model_order": ["Série 1", "Série 2", "Série 3", "Série 4", "Série 5", "Série 6", "Série 7", "X1", "X2", "X3", "X4", "X5", "X6", "X7", "iX1", "iX3", "iX", "i4", "i5", "i7"]
    },
    "citroen": {"search_url": BASE_SEARCH_URL + "Citroen", "brand_name": "Citroen", "model_order": ["C1", "C3", "C3 Aircross", "C4", "C4 Cactus", "C4 X", "C5", "C5 Aircross", "C5 X", "Berlingo", "Spacetourer"]},
    "cupra": {"search_url": BASE_SEARCH_URL + "Cupra", "brand_name": "Cupra", "model_order": ["Formentor", "Leon", "Ateca", "Born"]},
    "dsautomobiles": {"search_url": BASE_SEARCH_URL + "ds_automobiles", "brand_name": "DS Automobiles", "model_order": ["DS 3", "DS 4", "DS 7", "DS 9"]},
    "dacia": {
        "search_url": BASE_SEARCH_URL + "Dacia",
        "brand_name": "Dacia",
        "model_order": ["Spring", "Sandero", "Logan", "Logan MCV", "Jogger", "Dokker", "Duster"]
    },
    "fiat": {"search_url": BASE_SEARCH_URL + "Fiat", "brand_name": "Fiat", "model_order": ["500", "500X", "500L", "Panda", "Tipo", "Punto"]},
    "ford": {"search_url": BASE_SEARCH_URL + "Ford", "brand_name": "Ford", "model_order": ["Fiesta", "Focus", "Puma", "Kuga", "Mustang", "Mustang Mach-E", "Explorer"]},
    "honda": {"search_url": BASE_SEARCH_URL + "Honda", "brand_name": "Honda", "model_order": ["Civic", "CR-V", "HR-V", "Jazz"]},
    "hyundai": {"search_url": BASE_SEARCH_URL + "Hyundai", "brand_name": "Hyundai", "model_order": ["i10", "i20", "i30", "Tucson", "Kona", "Santa Fe", "Ioniq"]},
    "jaguar": {"search_url": BASE_SEARCH_URL + "Jaguar", "brand_name": "Jaguar", "model_order": ["XE", "XF", "E-Pace", "F-Pace", "I-Pace"]},
    "jeep": {"search_url": BASE_SEARCH_URL + "Jeep", "brand_name": "Jeep", "model_order": ["Renegade", "Compass", "Wrangler", "Avenger", "Gladiator"]},
    "kia": {"search_url": BASE_SEARCH_URL + "Kia", "brand_name": "Kia", "model_order": ["Picanto", "Rio", "Ceed", "Stonic", "Niro", "Sportage", "EV6"]},
    "landrover": {"search_url": BASE_SEARCH_URL + "land_rover", "brand_name": "Land Rover", "model_order": ["Defender", "Discovery", "Range Rover", "Range Rover Evoque", "Range Rover Sport", "Range Rover Velar"]},
    "lexus": {"search_url": BASE_SEARCH_URL + "Lexus", "brand_name": "Lexus", "model_order": ["CT", "IS", "NX", "RX", "UX"]},
    "lynkco": {"search_url": BASE_SEARCH_URL + "lynk_co", "brand_name": "Lynk & Co", "model_order": ["01"]},
    "mg": {"search_url": BASE_SEARCH_URL + "MG", "brand_name": "MG", "model_order": ["MG 4", "MG 5", "ZS", "EHS", "Marvel R"]},
    "mini": {"search_url": BASE_SEARCH_URL + "MINI", "brand_name": "MINI", "model_order": ["Cooper", "Countryman", "Clubman"]},
    "mazda": {"search_url": BASE_SEARCH_URL + "Mazda", "brand_name": "Mazda", "model_order": ["Mazda2", "Mazda3", "CX-3", "CX-30", "CX-5", "CX-60", "MX-5"]},
    "mercedesbenz": {
        "search_url": BASE_SEARCH_URL + "Mercedes_Benz",
        "brand_name": "Mercedes_Benz",
        "model_order": ["Classe A", "Classe B", "Classe C", "Classe E", "Classe S", "Classe V", "CLA", "CLS", "GLA", "GLB", "GLC", "GLE", "GLS", "EQA", "EQB", "EQC", "EQE", "EQS"]
    },
    "mitsubishi": {"search_url": BASE_SEARCH_URL + "Mitsubishi", "brand_name": "Mitsubishi", "model_order": ["Space Star", "Eclipse Cross"]},
    "nissan": {"search_url": BASE_SEARCH_URL + "Nissan", "brand_name": "Nissan", "model_order": ["Micra", "Juke", "Qashqai", "X-Trail", "Leaf", "Ariya"]},
    "opel": {"search_url": BASE_SEARCH_URL + "Opel", "brand_name": "Opel", "model_order": ["Corsa", "Astra", "Mokka", "Crossland", "Crossland X", "Grandland", "Grandland X"]},
    "peugeot": {
        "search_url": BASE_SEARCH_URL + "Peugeot",
        "brand_name": "Peugeot",
        "model_order": ["108", "208", "308", "408", "508", "2008", "3008", "5008", "Rifter", "Partner"]
    },
    "renault": {
        "search_url": BASE_SEARCH_URL + "Renault",
        "brand_name": "Renault",
        "model_order": ["Twingo", "Zoe", "Clio", "MéganE", "Captur", "Arkana", "Kadjar", "Koleos", "Austral", "Talisman", "Scenic", "Grand Scenic", "Espace", "Trafic", "Kangoo", "Master"]
    },
    "seat": {"search_url": BASE_SEARCH_URL + "Seat", "brand_name": "Seat", "model_order": ["Ibiza", "Leon", "Arona", "Ateca", "Tarraco"]},
    "skoda": {"search_url": BASE_SEARCH_URL + "Skoda", "brand_name": "Skoda", "model_order": ["Fabia", "Scala", "Octavia", "Superb", "Kamiq", "Karoq", "Kodiaq", "Enyaq"]},
    "smart": {"search_url": BASE_SEARCH_URL + "Smart", "brand_name": "Smart", "model_order": ["Fortwo", "Forfour"]},
    "suzuki": {"search_url": BASE_SEARCH_URL + "Suzuki", "brand_name": "Suzuki", "model_order": ["Ignis", "Swift", "Vitara", "S-Cross"]},
    "toyota": {"search_url": BASE_SEARCH_URL + "Toyota", "brand_name": "Toyota", "model_order": ["Aygo", "Yaris", "Corolla", "C-HR", "RAV4", "Hilux", "Land Cruiser"]},
    "volkswagen": {
        "search_url": BASE_SEARCH_URL + "Volkswagen",
        "brand_name": "Volkswagen",
        "model_order": ["up!", "Polo", "Golf VIII", "Golf VII", "Golf", "T-Cross", "T-Roc", "Tiguan", "Touran", "Passat", "Arteon", "CC", "Beetle", "Caddy", "Sharan", "Caravelle", "Taigo", "Amarok", "Touareg", "ID.3", "ID.4", "ID.5", "ID.7", "ID. Buzz"]
    },
    "volvo": {"search_url": BASE_SEARCH_URL + "Volvo", "brand_name": "Volvo", "model_order": ["XC40", "XC60", "XC90", "S60", "S90", "V60", "V90"]},
}

# --- FONCTIONS UTILITAIRES ---
NBSP = "\u00A0\u202F\u2007"

def ws(s): 
    return re.sub(rf"[{NBSP}]", " ", (s or "")).strip()

def to_int(s): 
    return int(re.sub(r"[^\d]", "", s)) if s else None

def extract_model(t, brand_name, model_order):
    t = ws(t)
    if not t: return "Autre"
    brand_to_match = "Mercedes" if brand_name == "Mercedes_Benz" else brand_name
    brand_pattern = rf"^\s*{re.escape(brand_to_match)}\s+(.*)$"
    m = re.match(brand_pattern, t, re.I)
    if not m and brand_name == "Mercedes_Benz":
        brand_pattern = rf"^\s*{re.escape(brand_name)}\s+(.*)$"
        m = re.match(brand_pattern, t, re.I)
    core = m.group(1) if m else t
    if not model_order:
        return "Autre" if core else brand_name
    for name in model_order:
        pattern_base = re.escape(name)
        if not name[-1].isalnum():
            pattern = rf"\b{pattern_base}"
        elif " " in name:
            pattern = rf"\b{pattern_base}"
        else:
            pattern = rf"\b{pattern_base}\b"
        if re.search(pattern, core, re.I):
            return name
    return "Autre"

def transmission_from(txt):
    t = ws(txt)
    if re.search(r"(dct|dsg|double)", t, re.I): return "Double embrayage / DCT"
    if re.search(r"(auto|bva)", t, re.I): return "Automatique"
    if re.search(r"(manu|bvm)", t, re.I): return "Manuelle"
    return None

def status_normalize(s):
    t = ws(s)
    if re.search(r"bient[oô]t", t, re.I): return "Bientôt disponible"
    if re.search(r"vente\s+en\s+cours", t, re.I): return "Vente en cours"
    if re.search(r"vendu", t, re.I): return "Vendu"
    return "Disponible"

def apply_filters(rows, filters):
    if not filters:
        return rows
    filtered_rows = []
    for row in rows:
        keep = True
        price = row.get('price_eur')
        year = row.get('year')
        km = row.get('km')
        transmission = (row.get('transmission') or "").lower()
        fuel = (row.get('fuel') or "").lower()
        discount = row.get('discount_eur')
        status = row.get('status')
        if filters.get('prix_min') and (not price or price < filters['prix_min']): keep = False
        if keep and filters.get('prix_max') and (not price or price > filters['prix_max']): keep = False
        if keep and filters.get('annee_min') and (not year or year < filters['annee_min']): keep = False
        if keep and filters.get('annee_max') and (not year or year > filters['annee_max']): keep = False
        if keep and filters.get('km_min') and (not km or km < filters['km_min']): keep = False
        if keep and filters.get('km_max') and (not km or km > filters['km_max']): keep = False
        if keep and filters.get('statut_disponible') and status != 'Disponible': keep = False
        if keep and filters.get('statut_bientot') and status != 'Bientôt disponible': keep = False
        if keep and filters.get('remise') == 'oui' and (not discount or discount <= 0): keep = False
        if keep and filters.get('remise') == 'non' and (discount and discount > 0): keep = False
        if keep and filters.get('transmission') == 'manuelle' and 'manuelle' not in transmission: keep = False
        if keep and filters.get('transmission') == 'automatique' and ('automatique' not in transmission and 'double' not in transmission): keep = False
        if keep and 'carburant' in filters:
            match_found = False
            for f in filters['carburant']:
                if f.lower() in fuel:
                    match_found = True
                    break
            if not match_found: keep = False
        if keep:
            filtered_rows.append(row)
    return filtered_rows