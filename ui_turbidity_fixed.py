from shiny import ui


ui_turbidity_fixed = ui.page_fluid(
    ui.layout_sidebar(
        ui.panel_sidebar(
            ui.input_select(
                "turbidity_fixed_year",
                "Année",
                ["2022", "2023", "2022/2023"],
                selected="2023",
            ),
            ui.input_select(
                "turbidity_fixed_estuary_name",
                "Estuaire",
                ["Bouctouche", "Cocagne", "Dunk", "Morell", "West"],
            ),
            ui.input_select(
                "turbidity_fixed_atmoshperic_correction",
                "Correction Atmosphérique",
                ["Sen2Cor", "Acolite"],
                selected="Sen2Cor",
            ),
            ui.input_switch(
                "turbidity_fixed_exclude_outlier",
                "Exclure les points abérants Grubbs-Beck",
                False,
            ),
            ui.input_switch(
                "turbidity_fixed_use_log_measure",
                "Utiliser le log des mesures de turbidité",
                False,
            ),
            ui.div(
                {"id": "turbidity-fixed-precise-location"},
                ui.input_select(
                    "turbidity_fixed_precise_location",
                    "Endroit de prise de mesure",
                    ["Aucune", "Mesure de Turbidité"],
                ),
            ),
            ui.input_select(
                "turbidity_fixed_type_of_turbidity_index",
                "Index de Turbidité Satellitaire",
                [
                    "NDTI",
                    "Bande Rouge (665nm)",
                    "Bande Infra Rouge (833nm)",
                    "(665nm)/(833nm)",
                ],
                selected="Bande Infra Rouge (833nm)",
            ),
            ui.div(
                {"id": "turbidity-fixed-visualisation"},
                ui.input_select(
                    "turbidity_fixed_visualisation",
                    "Visualisation",
                    [
                        "Image couleur",
                        "water_index",
                        "water_index_mask",
                        "Index Turbidité",
                        "NIR",
                    ],
                    selected="Index Turbidité",
                ),
            ),
            ui.input_select(
                "turbidity_fixed_selection_box_size",
                "Taille de la boite de sélection",
                ["1x1", "3x3", "5x5", "7x7"],
                selected="3x3",
            ),
            ui.input_numeric(
                "turbidity_fixed_turdibidty_df_window",
                "Time Windown for Turbidity Measurement",
                value=2,
                min=0,
                max=12,
                step=1,
            ),
            ui.input_numeric(
                "turbidity_fixed_water_index_mask_threshold",
                "Water Index Masque Threshold",
                value=-0.05,
                min=-0.1,
                max=0.1,
                step=0.01,
            ),
            ui.input_numeric(
                "turbidity_fixed_ndti_smoothed_sigma",
                "NDTI Filtre Gaussien Sigma",
                value=0,
                min=0,
                max=10,
                step=1,
            ),
            ui.input_action_button(
                "turbidity_fixed_previous_button", "Image Précédente"
            ),
            ui.input_action_button("turbidity_fixed_next_button", "Image Suivante"),
            ui.input_slider(
                "turbidity_fixed_image_idx",
                "Image Indice",
                0,
                1,
                0,
                animate=ui.AnimationOptions(interval=2000),
            ),
            ui.input_action_button("turbididty_fixed_save", "Save"),
            class_="mb-3",
        ),
        ui.panel_main(
            ui.output_plot(
                "generate_turbidity_fixed_image",
                width="900px",
                height="600px",
            ),
            ui.output_plot(
                "generate_estuary_turbidity_fixed_plot",
                click=True,
                # width="900px",
                # height="600px",
            ),
        ),
    )
)
