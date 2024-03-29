from shiny import ui


ui_turbidity = ui.page_fluid(
    ui.layout_sidebar(
        ui.panel_sidebar(
            ui.input_select(
                "turbidity_estuary_name",
                "Estuaire",
                ["Bouctouche", "Cocagne", "Dunk", "Morell", "West"],
            ),
            ui.input_select(
                "turbidity_atmoshperic_correction",
                "Correction Atmosphérique",
                ["Sen2Cor", "Acolite"],
                selected="Acolite",
            ),
            ui.input_select(
                "modified_turbidity_location_switch",
                "Utiliser les locations manuellement Modifiée",
                ["Original", "Modifiée manuellement"],
                selected="Modifiée manuellement",
            ),
            ui.input_switch(
                "turbidity_exclude_outlier",
                "Exclure les points abérants (>70 FNU)",
                True,
            ),
            ui.input_switch(
                "turbidity_use_log_measure",
                "Utiliser le log des mesures de turbidité",
                False,
            ),
            ui.div(
                {"id": "turbidity-precise-location"},
                ui.input_select(
                    "turbidity_precise_location",
                    "Endroit de prise de mesure",
                    ["Aucune"],
                ),
            ),
            ui.input_select(
                "type_of_turbidity_index",
                "Index de Turbidité Satellitaire",
                ["NDTI", "Bande Rouge (665nm)", "Bande Infra Rouge (833nm)"],
                selected="Bande Infra Rouge (833nm)",
            ),
            ui.div(
                {"id": "turbidity-visualisation"},
                ui.input_select(
                    "turbidity_visualisation",
                    "Visualisation",
                    [
                        "Image couleur",
                        "water_index",
                        "water_index_mask",
                        "Index Turbidité",
                    ],
                    selected="Index Turbidité",
                ),
            ),
            ui.input_select(
                "turbidity_selection_box_size",
                "Taille de la boite de sélection",
                ["1x1", "3x3", "5x5"],
                selected="3x3",
            ),
            ui.input_numeric(
                "water_index_mask_threshold",
                "Water Index Masque Threshold",
                value=-0.05,
                min=-0.1,
                max=0.1,
                step=0.01,
            ),
            ui.input_numeric(
                "ndti_smoothed_sigma",
                "NDTI Filtre Gaussien Sigma",
                value=0,
                min=0,
                max=10,
                step=1,
            ),
            ui.input_select(
                "turbidity_data_subset",
                "Sous Ensemble de prise de mesure",
                [
                    "Tous",
                    "Sans les bottoms",
                    "Centre Seulement",
                    "South (ou West) Seulement",
                    "North (ou East) Seulement",
                    "Shore Seulement",
                ],
                selected="Sans les bottoms",
            ),
            ui.input_action_button("turbidity_previous_button", "Image Précédente"),
            ui.input_action_button("turbidity_next_button", "Image Suivante"),
            ui.input_slider(
                "turbidity_image_idx",
                "Image Indice",
                0,
                1,
                0,
                animate=ui.AnimationOptions(interval=2000),
            ),
            class_="mb-3",
        ),
        ui.panel_main(
            ui.output_plot(
                "generate_turbidity_image",
                width="900px",
                height="600px",
            ),
            ui.output_plot(
                "generate_estuary_turbidity_plot",
                click=True,
                # width="900px",
                # height="600px",
            ),
        ),
    )
)
