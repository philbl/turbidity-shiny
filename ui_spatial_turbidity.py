from shiny import ui


ui_spatial_turbidity = ui.page_fluid(
    ui.layout_sidebar(
        ui.panel_sidebar(
            ui.input_select(
                "spatial_turbidity_estuary_name",
                "Estuaire",
                ["Bouctouche", "Cocagne", "Dunk", "Morell", "West"],
            ),
            ui.input_select(
                "spatial_turbidity_plot",
                "Figure",
                [
                    "Toutes les observations",
                    "Séparée par emplacement global",
                    "Séparée par emplacement global et précis",
                    "BoxPlot de toutes les emplacements",
                    "BoxPlot des emplacements globals",
                ],
            ),
            class_="mb-3",
        ),
        ui.panel_main(
            ui.output_plot(
                "generate_plot",
                width="900px",
                height="600px",
            ),
        ),
    )
)
