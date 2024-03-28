from shiny import ui


ui_satellite_situ = ui.page_fluid(
    ui.layout_sidebar(
        ui.panel_sidebar(
            ui.input_select(
                "satellite_situ_estuary_name",
                "Estuaire",
                ["Bouctouche", "Cocagne", "Dunk", "Morell", "West"],
            ),
            ui.input_select(
                "satellite_situ_atmospheric_correctin",
                "Correction Atmosphérique",
                ["Toutes", "Sen2Cor", "Acolite"],
            ),
            ui.input_switch(
                "satellite_situ_all_obs_switch",
                "Toutes les Observations doivent être utilisées",
                False,
            ),
            # ui.input_switch(
            #     "satellite_situ_exclude_points_from_bridge_switch",
            #     "Exclure les points identifiés manuellement comme un pont",
            #     False,
            # ),
            class_="mb-3",
        ),
        ui.panel_main(
            ui.output_data_frame(
                "output_result_df",
                # width="900px",
                # height="600px",
            ),
            ui.panel_conditional(
                "input.output_result_df_selected_rows.length > 0",
                ui.output_data_frame(
                    "output_correspond_selected_row_result_df",
                    # width="900px",
                    # height="600px",
                ),
            ),
            ui.panel_conditional(
                "input.output_result_df_selected_rows.length > 0 && "
                "input.output_correspond_selected_row_result_df_selected_rows.length > 0",
                ui.output_plot("output_correspond_selected_row_plot"),
            ),
            ui.output_plot("output_hyperparameters_diagnostics", height="1000px"),
        ),
    )
)
