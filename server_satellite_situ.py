import matplotlib.pyplot as plt

import numpy
import pandas
from shiny import render, reactive, Session


ESTUARY_NAME_LIST = ["Bouctouche", "Cocagne", "Dunk", "Morell", "West"]
ORDER_COLS = [
    "location",
    "exclude_points_from_bridge",
    "ndwi_threshold",
    "box_size",
    "ndti_smoothed_sigma",
    "type_of_turbidity_index",
    "y_name",
    "r2",
    "pvalue",
    "pct_of_obs_use",
    "slope",
    "number_of_obs",
    "number_of_valid_obs",
]


def load_result_df(estuary_name):
    result_df = pandas.read_feather(
        f"data/result_bridge_pvalue/{estuary_name}_estuary_result_no_outlier_with_data.feather"
    )
    result_df["pct_of_obs_use"] = (
        result_df["number_of_valid_obs"] / result_df["number_of_obs"]
    ).apply(lambda x: numpy.round(x, 2))
    result_df["r2"] = result_df["r2"].apply(lambda x: numpy.round(x, 4))
    result_df["slope"] = result_df["slope"].apply(lambda x: numpy.round(x, 4))
    result_df["pvalue"] = result_df["pvalue"].apply(lambda x: numpy.round(x, 4))
    return result_df


def server_satellite_situ(input, output, session: Session):
    @reactive.Calc
    def load_result_dict():
        result_dict = {}
        for estuary_name in ESTUARY_NAME_LIST:
            estuary_name = estuary_name.lower()
            result_df = load_result_df(estuary_name)
            if input.satellite_situ_all_obs_switch() is True:
                result_df = result_df[result_df["pct_of_obs_use"] == 1].reset_index(
                    drop=True
                )
            if input.satellite_situ_exclude_points_from_bridge_switch() is True:
                result_df = result_df[
                    result_df["exclude_points_from_bridge"]
                ].reset_index(drop=True)
            result_dict[estuary_name] = result_df
        return result_dict

    @reactive.Calc
    def load_corresponding_result_df():
        result_dict = load_result_dict()
        estuary_name = input.satellite_situ_estuary_name()
        result_df = result_dict[estuary_name.lower()]
        return result_df

    @output
    @render.data_frame
    def output_result_df():
        result_df = load_corresponding_result_df()
        result_df = result_df[ORDER_COLS]
        return render.DataGrid(result_df, row_selection_mode="single")

    @reactive.Calc
    def load_all_estuary_corresponding_df():
        selected_idx = input.output_result_df_selected_rows()
        if len(selected_idx) == 0:
            return None
        else:
            selected_idx = selected_idx[0]
            result_df = load_corresponding_result_df()
            result_dict = load_result_dict()
            selected_row = result_df.iloc[selected_idx]
            corresponding_df_list = []
            for estuary_name in ESTUARY_NAME_LIST:
                estuary_df = result_dict[estuary_name.lower()]
                max_r2 = estuary_df["r2"].max()
                estuary_df = estuary_df[
                    (estuary_df["ndwi_threshold"] == selected_row["ndwi_threshold"])
                    & (estuary_df["box_size"] == selected_row["box_size"])
                    & (
                        estuary_df["ndti_smoothed_sigma"]
                        == selected_row["ndti_smoothed_sigma"]
                    )
                    & (
                        estuary_df["type_of_turbidity_index"]
                        == selected_row["type_of_turbidity_index"]
                    )
                    & (estuary_df["y_name"] == selected_row["y_name"])
                ]
                if len(estuary_df) == 0:
                    continue
                estuary_df["estuary"] = estuary_name
                estuary_df["max_r2"] = max_r2
                corresponding_df_list.append(estuary_df)
            return pandas.concat(corresponding_df_list, ignore_index=True)

    @output
    @render.data_frame
    def output_correspond_selected_row_result_df():
        corresponding_df = load_all_estuary_corresponding_df()
        if corresponding_df is not None:
            new_order_cols = ORDER_COLS.copy()
            new_order_cols.insert(8, "max_r2")
            return render.DataGrid(
                corresponding_df[["estuary"] + new_order_cols],
                row_selection_mode="single",
            )

    @output
    @render.plot
    def output_correspond_selected_row_plot():
        selected_idx = input.output_correspond_selected_row_result_df_selected_rows()
        if len(selected_idx) == 0:
            pass
        else:
            selected_idx = selected_idx[0]
            result_df = load_all_estuary_corresponding_df()
            selected_row = result_df.iloc[selected_idx]
            fig, ax = plt.subplots(1, 1, figsize=(10, 7))
            ax.scatter(selected_row["data_dict"]["x"], selected_row["data_dict"]["y"])
            x_min, x_max = (
                selected_row["data_dict"]["x"].min(),
                selected_row["data_dict"]["x"].max(),
            )
            y_max = selected_row["data_dict"]["y"].max()
            x = numpy.linspace(start=x_min, stop=x_max, num=10)
            # reg = linregress(selected_row["data_dict"]["x"], selected_row["data_dict"]["y"])
            ax.plot(x, selected_row["intercept"] + selected_row["slope"] * x)
            ylabel = (
                "Turbidité (FNU)"
                if selected_row["y_name"] == "measure"
                else "Log(Turbidité (FNU))"
            )
            ax.set_ylabel(ylabel)
            ax.set_xlabel(selected_row["type_of_turbidity_index"])
            ax.set_title(
                "Mesure de la turbidity In Situ en fonction d'un indice d'imagerie satellite"
            )
            ax.set_ylim((0, y_max * 1.2))
            return fig

    @output
    @render.plot
    def output_hyperparameters_diagnostics():
        result_df = load_corresponding_result_df().copy()
        result_df["ndwi_threshold"] = result_df["ndwi_threshold"].apply(
            lambda x: numpy.round(x, 2)
        )
        result_df["location"] = result_df["location"].apply(
            lambda x: x.replace(" ", "\n")
        )
        result_df["type_of_turbidity_index"] = result_df[
            "type_of_turbidity_index"
        ].apply(lambda x: x.replace(" R", "\nR"))
        result_df["type_of_turbidity_index"] = result_df[
            "type_of_turbidity_index"
        ].apply(lambda x: x.replace(" (", "\n("))
        fig, axs = plt.subplots(4, 2, figsize=(6, 12))
        for col, ax in zip(
            [
                "location",
                "ndwi_threshold",
                "box_size",
                "ndti_smoothed_sigma",
                "type_of_turbidity_index",
                "y_name",
                "exclude_points_from_bridge",
            ],
            axs.flatten(),
        ):
            result_df.boxplot(column="r2", by=col, ax=ax)
        plt.tight_layout()
        return fig
