import httpx
from bs4 import BeautifulSoup
import logic
import time
import random

# On imite un navigateur mobile Android RÉCENT pour éviter les blocages
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://www.google.com/"
}

def get_ads(brand_key, max_pages=4):
    """
    Récupère les annonces pour une marque donnée.
    max_pages : Limite le nombre de pages à scanner.
    """
    if brand_key not in logic.BRAND_CONFIGS:
        print(f"Erreur : La marque '{brand_key}' n'est pas dans la config.")
        return []

    config = logic.BRAND_CONFIGS[brand_key]
    base_url = config["search_url"]
    all_ads = []
    
    print(f"Scraping de {config['brand_name']}...")

    # On active 'follow_redirects=True' pour gérer le code 302
    with httpx.Client(timeout=30.0, headers=HEADERS, follow_redirects=True) as client:
        for page_num in range(1, max_pages + 1):
            
            # Construction de l'URL
            # Si c'est la page 1, on utilise l'URL de base brute pour éviter des erreurs de pagination
            if page_num == 1:
                url = base_url
            else:
                url = f"{base_url}&page={page_num}"
            
            print(f" - Chargement page {page_num} ({url})...")

            try:
                response = client.get(url)
                
                # Vérification du succès
                if response.status_code != 200:
                    print(f"Stop: Erreur code {response.status_code} sur {url}")
                    # Si c'est une erreur 404, ça veut dire qu'il n'y a plus de pages
                    if response.status_code == 404:
                        break
                    continue

                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Sélecteur mis à jour pour être plus robuste
                cards = soup.select('a[data-qa-selector="ad-card-link"]')

                if not cards:
                    print("Info: Pas d'annonces trouvées sur cette page (Fin de liste ?)")
                    # Debug : Si page 1 et vide, c'est suspect
                    if page_num == 1:
                        print("DEBUG: Le site a renvoyé une page vide d'annonces.")
                    break

                print(f"   -> {len(cards)} annonces détectées.")

                for card in cards:
                    try:
                        # 1. Extraction brute
                        href = card.get('href')
                        full_url = "https://www.autohero.com" + href if href else ""
                        
                        title_elem = card.select_one('[data-qa-selector="title"]')
                        title = logic.ws(title_elem.text) if title_elem else ""

                        subtitle_elem = card.select_one('[data-qa-selector="subtitle"]')
                        subtitle = logic.ws(subtitle_elem.text) if subtitle_elem else ""

                        price_elem = card.select_one('[data-qa-selector="price"]')
                        price_raw = price_elem.text if price_elem else ""
                        price = logic.to_int(price_raw)

                        year_elem = card.select_one('[data-qa-selector="spec-year"]')
                        year = logic.to_int(year_elem.text) if year_elem else None

                        km_elem = card.select_one('[data-qa-selector="spec-mileage"]')
                        km = logic.to_int(km_elem.text) if km_elem else None

                        fuel_elem = card.select_one('[data-qa-selector="spec-fuel"]')
                        fuel = logic.ws(fuel_elem.text) if fuel_elem else ""

                        gear_elem = card.select_one('[data-qa-selector="spec-gear"]')
                        gear = logic.ws(gear_elem.text) if gear_elem else ""
                        
                        # --- Normalisation via ta logique complexe (logic.py) ---
                        transmission = logic.transmission_from(f"{subtitle} {gear}")
                        model = logic.extract_model(title, config['brand_name'], config['model_order'])

                        ad_data = {
                            "title": title,
                            "model": model,
                            "price_eur": price,
                            "year": year,
                            "km": km,
                            "fuel": fuel,
                            "transmission": transmission,
                            "url": full_url
                        }
                        all_ads.append(ad_data)
                        
                    except Exception as e:
                        # On ignore les erreurs sur une seule carte pour ne pas bloquer le reste
                        continue
                
                # Pause aléatoire pour ne pas ressembler à un robot
                time.sleep(random.uniform(0.5, 1.5))

            except Exception as e:
                print(f"Erreur de réseau critique : {e}")
                break
    
    return all_ads