from shiny import ui


ui_satellite_fixed = ui.page_fluid(
    ui.layout_sidebar(
        ui.panel_sidebar(
            ui.input_select(
                "satellite_fixed_year",
                "Année",
                ["2022", "2023", "2022/2023"],
                selected="2023",
            ),
            ui.input_select(
                "satellite_fixed_estuary_name",
                "Estuaire",
                ["Bouctouche", "Cocagne", "Dunk", "Morell", "West"],
            ),
            ui.input_select(
                "satellite_fixed_atmospheric_correctin",
                "Correction Atmosphérique",
                ["Toutes", "Sen2Cor", "Acolite"],
            ),
            ui.input_switch(
                "satellite_fixed_all_obs_switch",
                "Toutes les Observations doivent être utilisées",
                False,
            ),
            ui.input_switch(
                "satellite_fixed_only_positive_slope",
                "Garder Seulement les pentes positives",
                False,
            ),
            class_="mb-3",
        ),
        ui.panel_main(
            ui.output_data_frame(
                "output_fixed_result_df",
                # width="900px",
                # height="600px",
            ),
            ui.panel_conditional(
                "input.output_fixed_result_df_selected_rows.length > 0",
                ui.output_data_frame(
                    "output_correspond_selected_row_fixed_result_df",
                    # width="900px",
                    # height="600px",
                ),
            ),
            ui.panel_conditional(
                "input.output_fixed_result_df_selected_rows.length > 0 && "
                "input.output_correspond_selected_row_fixed_result_df_selected_rows.length > 0",
                ui.output_plot("output_correspond_selected_row_fixed_plot"),
            ),
            ui.output_plot("output_fixed_hyperparameters_diagnostics", height="1000px"),
        ),
    )
)
