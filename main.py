import flet as ft
import logic
import scraper
import datetime

def main(page: ft.Page):
    # --- Configuration de la fenêtre ---
    page.title = "Autohero Scraper Pro"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 450
    page.window_height = 850
    page.scroll = "adaptive"
    page.padding = 15

    # --- Gestion de la Navigation (Pages) ---
    # On va utiliser un système de "Vues" pour changer de page sans perdre les données
    
    # 1. Variables pour stocker les résultats
    # Format : {"Suzuki": [liste_des_annonces], "Toyota": [...]}
    scan_results = {} 

    # --- En-tête ---
    header = ft.Text("Autohero Multi-Scan", size=24, weight="bold", color="blue")
    
    # =================================================================
    # 1. GESTION MULTI-MARQUES
    # =================================================================
    selected_brands = set()
    selected_brands_text = ft.Text("Aucune marque sélectionnée", italic=True, size=12, color="grey")

    def close_dlg(e):
        if not selected_brands:
            selected_brands_text.value = "Aucune marque sélectionnée"
            selected_brands_text.color = "red"
        else:
            noms = [logic.BRAND_CONFIGS[k]['brand_name'] for k in selected_brands]
            txt = ", ".join(noms[:3])
            if len(noms) > 3: txt += f" (+{len(noms)-3} autres)"
            selected_brands_text.value = txt
            selected_brands_text.color = "black"
        page.close(dlg_modal)
        page.update()

    def checkbox_changed(e):
        brand_key = e.control.data
        if e.control.value:
            selected_brands.add(brand_key)
        else:
            if brand_key in selected_brands:
                selected_brands.remove(brand_key)

    checkboxes_col = ft.Column(scroll="auto")
    for key in sorted(logic.BRAND_CONFIGS.keys()):
        brand_name = logic.BRAND_CONFIGS[key]['brand_name']
        cb = ft.Checkbox(label=brand_name, value=False, data=key, on_change=checkbox_changed)
        checkboxes_col.controls.append(cb)

    dlg_modal = ft.AlertDialog(
        modal=True,
        title=ft.Text("Choisir les marques"),
        content=ft.Container(width=300, height=400, content=checkboxes_col),
        actions=[ft.TextButton("VALIDER", on_click=close_dlg)],
    )

    def open_brand_selector(e):
        page.open(dlg_modal)
        page.update()

    btn_select_brands = ft.ElevatedButton(
        "Sélectionner les marques", 
        icon=ft.Icons.LIST, 
        on_click=open_brand_selector,
        width=380
    )

    # =================================================================
    # 2. TOUS LES FILTRES
    # =================================================================
    
    price_min = ft.TextField(label="Prix Min (€)", width=130, keyboard_type=ft.KeyboardType.NUMBER, text_size=12)
    price_max = ft.TextField(label="Prix Max (€)", width=130, keyboard_type=ft.KeyboardType.NUMBER, text_size=12)
    km_min = ft.TextField(label="KM Min", width=130, keyboard_type=ft.KeyboardType.NUMBER, text_size=12)
    km_max = ft.TextField(label="KM Max", width=130, keyboard_type=ft.KeyboardType.NUMBER, text_size=12)

    years_list = [ft.dropdown.Option(str(y)) for y in range(datetime.datetime.now().year, 2004, -1)]
    year_min = ft.Dropdown(label="Année Min", width=130, options=years_list, text_size=12)
    year_max = ft.Dropdown(label="Année Max", width=130, options=years_list, text_size=12)

    dd_trans = ft.Dropdown(label="Transmission", width=300, options=[
        ft.dropdown.Option("manuelle", "Manuelle"),
        ft.dropdown.Option("automatique", "Automatique")
    ], text_size=12)

    dd_fuel = ft.Dropdown(label="Carburant", width=300, options=[
        ft.dropdown.Option("essence", "Essence"),
        ft.dropdown.Option("diesel", "Diesel"),
        ft.dropdown.Option("hybride", "Hybride"),
        ft.dropdown.Option("electrique", "Électrique"),
        ft.dropdown.Option("gaz", "Gaz (GPL/GNV)"),
        ft.dropdown.Option("ethanol", "Ethanol")
    ], text_size=12)

    cb_remise = ft.Checkbox(label="Voitures remisées uniquement")
    cb_dispo = ft.Checkbox(label="Annonces 'Disponibles' uniquement")
    cb_bientot = ft.Checkbox(label="Annonces 'Bientôt disponible' uniquement")

    def reset_filters(e):
        price_min.value = ""
        price_max.value = ""
        km_min.value = ""
        km_max.value = ""
        year_min.value = None
        year_max.value = None
        dd_trans.value = None
        dd_fuel.value = None
        cb_remise.value = False
        cb_dispo.value = False
        cb_bientot.value = False
        page.update()

    btn_reset = ft.ElevatedButton("Réinitialiser les filtres", bgcolor="grey", color="white", on_click=reset_filters)

    filters_content = ft.Column([
        ft.Text("Critères Numériques", weight="bold", size=14),
        ft.Row([price_min, price_max], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Row([year_min, year_max], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Row([km_min, km_max], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Divider(),
        ft.Text("Critères Techniques", weight="bold", size=14),
        dd_trans,
        dd_fuel,
        ft.Divider(),
        ft.Text("Statut", weight="bold", size=14),
        cb_remise,
        cb_dispo,
        cb_bientot,
        ft.Divider(),
        btn_reset
    ])

    filters_tile = ft.ExpansionTile(
        title=ft.Text("Filtres Complets", weight="bold", color="blue"),
        subtitle=ft.Text("Prix, Année, KM, Statut..."),
        controls=[ft.Container(padding=10, content=filters_content)]
    )

    # Zone où s'afficheront les boutons des marques (après le scan)
    results_list_container = ft.Column(spacing=10)
    status_text = ft.Text("Prêt à scanner.", italic=True, color="grey")

    # =================================================================
    # 3. FONCTION POUR ALLER VERS LA PAGE DE DÉTAIL
    # =================================================================
    def go_to_detail_page(brand_name, ads_list):
        # Création de la liste des cartes pour la nouvelle page
        detail_list = ft.ListView(expand=True, spacing=10, padding=10)
        
        for ad in ads_list:
            badges = []
            if ad.get('transmission'): badges.append(ad['transmission'])
            if ad.get('fuel'): badges.append(ad['fuel'])
            
            card = ft.Card(
                elevation=3,
                content=ft.Container(
                    padding=10,
                    content=ft.Column([
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.DIRECTIONS_CAR, color="blue"),
                            title=ft.Text(ad['title'], weight="bold", size=15),
                            subtitle=ft.Text(f"{ad['year']} | {ad['km']} km", size=13)
                        ),
                        ft.Row([
                            ft.Container(content=ft.Text(b, size=10, color="white"), bgcolor="grey", padding=3, border_radius=3) 
                            for b in badges
                        ]),
                        ft.Divider(),
                        ft.Row([
                            ft.Text(f"{ad['price_eur']} €", size=18, weight="bold", color="blue"),
                            ft.ElevatedButton("Voir", url=ad['url'], bgcolor="blue", color="white")
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                    ])
                )
            )
            detail_list.controls.append(card)

        # Définition de la vue (Page)
        page.views.append(
            ft.View(
                f"/detail/{brand_name}",
                [
                    ft.AppBar(title=ft.Text(f"{brand_name} ({len(ads_list)})"), bgcolor="blue", color="white"),
                    detail_list
                ]
            )
        )
        page.go(f"/detail/{brand_name}")

    def route_change(route):
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop


    # =================================================================
    # 4. LOGIQUE DE RECHERCHE
    # =================================================================
    def on_search_click(e):
        if not selected_brands:
            status_text.value = "Erreur: Sélectionnez au moins une marque !"
            status_text.color = "red"
            page.update()
            return

        results_list_container.controls.clear()
        scan_results.clear()
        btn_search.disabled = True
        page.update()

        # Filtres
        user_filters = {}
        def get_int(field):
            try: return int(field.value) if field.value else None
            except: return None

        if get_int(price_min): user_filters['prix_min'] = get_int(price_min)
        if get_int(price_max): user_filters['prix_max'] = get_int(price_max)
        if get_int(km_min): user_filters['km_min'] = get_int(km_min)
        if get_int(km_max): user_filters['km_max'] = get_int(km_max)
        if year_min.value: user_filters['annee_min'] = int(year_min.value)
        if year_max.value: user_filters['annee_max'] = int(year_max.value)
        if dd_trans.value: user_filters['transmission'] = dd_trans.value
        if dd_fuel.value: user_filters['carburant'] = [dd_fuel.value]
        if cb_remise.value: user_filters['remise'] = 'oui'
        if cb_dispo.value: user_filters['statut_disponible'] = True
        if cb_bientot.value: user_filters['statut_bientot'] = True

        total_found_global = 0

        for brand_key in selected_brands:
            brand_name = logic.BRAND_CONFIGS[brand_key]['brand_name']
            
            status_text.value = f"Scan en cours : {brand_name}..."
            status_text.color = "orange"
            page.update()

            try:
                raw_ads = scraper.get_ads(brand_key, max_pages=4)
                final_ads = logic.apply_filters(raw_ads, user_filters)
                
                if final_ads:
                    total_found_global += len(final_ads)
                    # On sauvegarde les résultats en mémoire
                    scan_results[brand_name] = final_ads
                    
                    # On crée un BOUTON "CARTE" pour la marque (au lieu d'une liste déroulante)
                    # C'est ce bouton qui changera de page
                    brand_card = ft.Card(
                        content=ft.ListTile(
                            leading=ft.Icon(ft.Icons.FOLDER_OPEN, size=30, color="blue"),
                            title=ft.Text(f"{brand_name}", weight="bold", size=16),
                            subtitle=ft.Text(f"{len(final_ads)} annonce(s) trouvée(s)", color="green"),
                            trailing=ft.Icon(ft.Icons.ARROW_FORWARD_IOS, size=16),
                            on_click=lambda e, bn=brand_name, ads=final_ads: go_to_detail_page(bn, ads)
                        )
                    )
                    results_list_container.controls.append(brand_card)

            except Exception as ex:
                print(f"Erreur sur {brand_name}: {ex}")
                continue
        
        status_text.value = f"Terminé : {total_found_global} annonces au total."
        status_text.color = "green" if total_found_global > 0 else "red"
        
        if total_found_global == 0:
            results_list_container.controls.append(ft.Text("Aucun résultat pour ces critères."))

        btn_search.disabled = False
        page.update()

    # --- Assemblage Page Principale ---
    btn_search = ft.ElevatedButton(
        text="Lancer le Scan Multi-Marques",
        icon=ft.Icons.ROCKET_LAUNCH,
        style=ft.ButtonStyle(padding=15, shape=ft.RoundedRectangleBorder(radius=10)),
        bgcolor="blue",
        color="white",
        width=380,
        on_click=on_search_click
    )

    # Contenu de la vue principale
    main_column = ft.Column(
        [
            header,
            btn_select_brands,
            selected_brands_text,
            ft.Divider(),
            filters_tile, 
            ft.Divider(),
            btn_search,
            status_text,
            results_list_container 
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        scroll="auto", # Permet de scroller la page principale
        expand=True
    )

    page.add(main_column)

ft.app(target=main)