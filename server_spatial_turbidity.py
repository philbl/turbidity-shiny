from itertools import product
import matplotlib.pyplot as plt
import numpy
import pandas
from shiny import render, reactive, Session

from turbidity_shiny.utils import (
    load_json_data,
)


def server_spatial_turbidity(input, output, session: Session):
    @reactive.Calc
    def load_measures_data_json():
        estuary_name = input.spatial_turbidity_estuary_name()
        path = (
            f"../data/field_work/json/summer_2023/{estuary_name.lower()}_measures.json"
        )
        data_json = load_json_data(path)
        return data_json

    @reactive.Calc
    def create_data_df():
        estuary_name = input.spatial_turbidity_estuary_name()
        data_json = load_measures_data_json()
        data_df = pandas.DataFrame(
            columns=[
                "date",
                "time",
                "notes",
                "global_location",
                "precise_location",
                "measures_list",
            ]
        )
        i = 0
        for field_work in data_json:
            notes = field_work["notes"]
            date = field_work["date"]
            for measure in field_work["spatial_turbidity_measurement"][
                "measurements_list"
            ]:
                time = measure["time"]
                precise_location = (
                    measure["notes"]
                    .replace(f"{estuary_name} ", "")
                    .replace("Bridge Bridge", "Bridge Center")
                )
                global_location = measure["global_location"].replace(
                    f" {estuary_name}", ""
                )
                measures = measure["measures"]
                if date == "2023-07-25" and time == "15:55":
                    continue
                data_df.loc[i, "date"] = date
                data_df.loc[i, "time"] = time
                data_df.loc[i, "notes"] = notes
                data_df.loc[i, "precise_location"] = precise_location
                data_df.loc[i, "global_location"] = global_location
                data_df.loc[i, "measures_list"] = measures
                i += 1

        data_df["year"] = data_df["date"].apply(lambda x: x[:4])
        data_df["month_day"] = data_df["date"].apply(lambda x: x[5:])
        data_df["measure_median"] = data_df["measures_list"].apply(numpy.median)
        data_df["measure_max"] = data_df["measures_list"].apply(numpy.max)
        data_df["measure_min"] = data_df["measures_list"].apply(numpy.min)
        data_df["measure_error"] = data_df["measure_max"] - data_df["measure_min"]
        data_df["measure_error_pct"] = (
            data_df["measure_error"] / data_df["measure_median"]
        )
        data_df["meteo_condition"] = data_df["notes"].apply(lambda x: x.split(",")[0])
        return data_df

    @output
    @render.plot
    def generate_plot():
        if input.spatial_turbidity_plot() == "Toutes les observations":
            return generate_global_plot()
        if input.spatial_turbidity_plot() == "Séparée par emplacement global":
            return generate_global_location_plot()
        if input.spatial_turbidity_plot() == "Séparée par emplacement global et précis":
            return generate_precise_location_plot()
        if input.spatial_turbidity_plot() == "BoxPlot de toutes les emplacements":
            return generate_global_boxplot()
        if input.spatial_turbidity_plot() == "BoxPlot des emplacements globals":
            return generate_precise_location_boxplot()

    def generate_global_plot():
        data_df = create_data_df()
        fig, ax = plt.subplots(1, 1, figsize=(10, 7))
        for unique_location in numpy.unique(data_df["precise_location"]):
            data_for_location = data_df[
                data_df["precise_location"] == unique_location
            ].sort_values(by="date")
            ax.scatter(
                data_for_location["date"],
                data_for_location["measure_median"],
                label=unique_location,
            )
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        return fig

    def generate_global_location_plot():
        data_df = create_data_df()
        global_location_group = [
            tuple(
                filter(
                    lambda precise_location: global_location in precise_location,
                    numpy.unique(data_df["precise_location"]),
                )
            )
            for global_location in numpy.unique(data_df["global_location"])
        ]
        fig, axs = plt.subplots(
            len(global_location_group), 1, figsize=(8, 6), sharex=True
        )
        for location_group, ax in zip(
            global_location_group, numpy.array(axs).flatten()
        ):
            nb_first_word = 2 if "Pedestrian" in location_group[0] else 3
            fig_title = " ".join(location_group[0].split(" ")[:nb_first_word])
            for unique_location in location_group:
                label = " ".join(
                    sorted(
                        list(
                            set(unique_location.split(" ")) - set(fig_title.split(" "))
                        )
                    )
                )
                data_for_location = data_df[
                    data_df["precise_location"] == unique_location
                ].sort_values(by="month_day")
                ax.scatter(
                    data_for_location["month_day"],
                    data_for_location["measure_median"],
                    label=label,
                )
            ax.set_title(fig_title)
            ax.legend()
        plt.tight_layout()
        plt.show()
        return fig

    def generate_precise_location_plot():
        data_df = create_data_df()
        precise_location_group = [
            tuple(
                filter(
                    lambda precise_location: (global_location in precise_location)
                    and (center_shore_location in precise_location),
                    numpy.unique(data_df["precise_location"]),
                )
            )
            for global_location, center_shore_location in product(
                list(numpy.unique(data_df["global_location"])), ["Center", "shore"]
            )
        ]
        fig, axs = plt.subplots(
            int(len(precise_location_group) / 2), 2, figsize=(10, 7), sharex=True
        )
        axs = numpy.atleast_2d(axs)
        for location_group, ax in zip(precise_location_group, axs.flatten()):
            if len(location_group) == 0:
                continue
            fig_title = " ".join(
                [
                    x
                    for x, y in zip(
                        location_group[0].split(" "), location_group[1].split(" ")
                    )
                    if x == y
                ]
            )
            for unique_location in location_group:
                label = list(
                    set(unique_location.split(" ")) - set(fig_title.split(" "))
                )[0]
                data_for_location = data_df[
                    data_df["precise_location"] == unique_location
                ].sort_values(by="month_day")
                ax.scatter(
                    data_for_location["month_day"],
                    data_for_location["measure_median"],
                    label=label,
                    alpha=0.85,
                )
            ax.set_title(fig_title)
            ax.tick_params(axis="x", rotation=45)
            ax.legend(loc="upper left")
        for h_axs in axs:
            max_ylim = max(h_axs[0].get_ylim()[1], h_axs[1].get_ylim()[1])
            for ax in h_axs:
                ax.set_ylim(0, max_ylim)
        plt.tight_layout()
        plt.show()
        return fig

    def generate_global_boxplot():
        data_df = create_data_df()
        fig, ax = plt.subplots(1, 1)
        data_df.boxplot(column="measure_median", by="global_location", rot=90, ax=ax)
        return fig

    def generate_precise_location_boxplot():
        data_df = create_data_df()
        fig, ax = plt.subplots(1, 1)
        data_df.boxplot(column="measure_median", by="precise_location", rot=90, ax=ax)
        return fig
