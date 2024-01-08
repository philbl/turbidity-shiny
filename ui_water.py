from shiny import ui


ui_water = ui.page_fluid(
    ui.layout_sidebar(
        ui.panel_sidebar(
            ui.input_select(
                "water_estuary_name",
                "Estuaire",
                ["Bouctouche", "Cocagne", "Dunk", "Morell", "West"],
            ),
            ui.input_action_button("water_previous_button", "Image Précédente"),
            ui.input_action_button("water_next_button", "Image Suivante"),
            ui.input_slider(
                "water_image_idx",
                "Image Indice",
                0,
                1,
                0,
                animate=ui.AnimationOptions(interval=2000),
            ),
            # TODO use panel conditional https://shinylive.io/py/editor/#orbit-simulation
            ui.row(
                ui.column(
                    7,
                    ui.div(
                        {"id": "scene-clf-switch"},
                        ui.input_switch(
                            "switch_scene_clf_water_mask", "Masque d'eau Scene Clf 20m "
                        ),
                    ),
                ),
                ui.column(
                    1,
                    ui.input_action_button(
                        "info_scene_clf",
                        "?",
                        style="padding:10px; font-size:60%; border-radius: 50%; border: 1px solid black;background-color:lightgrey",
                    ),
                ),
            ),
            ui.row(
                ui.column(
                    7,
                    ui.div(
                        {"id": "ndwi-switch"},
                        ui.input_switch(
                            "switch_ndwi_water_mask", "Masque d'eau NDWI 10m"
                        ),
                    ),
                ),
                ui.column(
                    1,
                    ui.input_action_button(
                        "info_ndwi",
                        "?",
                        style="padding:10px; font-size:60%; border-radius: 50%; border: 1px solid black;background-color:lightgrey",
                    ),
                ),
            ),
            class_="mb-3",
        ),
        ui.panel_main(
            ui.output_plot(
                "generate_water_image",
                width="900px",
                height="600px",
                dblclick=True,
                brush=ui.brush_opts(reset_on_new=True),
            ),
        ),
    )
)
