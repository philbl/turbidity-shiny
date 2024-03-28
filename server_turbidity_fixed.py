import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy
from shiny import ui, render, reactive, Session
from shiny.types import SilentException

from satellite_image_handler.utils.normalize_index import create_water_index_raster
from shiny.plotutils import near_points


from turbidity_shiny.utils import (
    load_json_data,
    save_json_data,
)
from turbidity_shiny.turbidity.turbidity_df import (
    create_turbidity_fixed_df,
    get_smoothed_turbidity_index_water_index_mask,
)
from turbidity_shiny.turbidity.load_data import load_turbidity_fixed_data


def server_turbidity_fixed(input, output, session: Session):
    @reactive.Calc
    def get_turbidity_data():
        (
            image_handler_list,
            fixed_turbidity_data,
            turbidity_geo_coordinate_dict,
        ) = load_turbidity_fixed_data(
            input.turbidity_fixed_estuary_name(),
            input.turbidity_fixed_atmoshperic_correction(),
            input.turbidity_fixed_year(),
        )
        return image_handler_list, fixed_turbidity_data, turbidity_geo_coordinate_dict

    @reactive.Calc
    def get_number_of_turbidity_image():
        return len(get_turbidity_data()[0])

    @reactive.Calc
    def generate_turbidity_df():
        (
            image_handler_list,
            fixed_turbidity_data,
            turbidity_geo_coordinate_dict,
        ) = get_turbidity_data()
        box_size_string = input.turbidity_fixed_selection_box_size()
        box_size = int(box_size_string[0])
        water_index_mask_threshold = input.turbidity_fixed_water_index_mask_threshold()
        ndti_smoothed_sigma = input.turbidity_fixed_ndti_smoothed_sigma()
        turbidity_df = create_turbidity_fixed_df(
            image_handler_list,
            fixed_turbidity_data,
            turbidity_geo_coordinate_dict,
            water_index_mask_threshold,
            box_size,
            ndti_smoothed_sigma,
            input.turbidity_fixed_type_of_turbidity_index(),
            True,
            input.turbidity_fixed_exclude_outlier(),
            False,
            input.turbidity_fixed_turdibidty_df_window(),
        )
        return turbidity_df

    @reactive.Effect
    @reactive.event(input.turbidity_fixed_estuary_name, input.turbidity_fixed_year)
    def update_turbidity_slider_idx():
        number_of_image = get_number_of_turbidity_image()
        ui.update_slider(
            "turbidity_fixed_image_idx", min=0, max=number_of_image - 1, value=0, step=1
        ),

    @reactive.Effect
    @reactive.event(input.generate_estuary_turbidity_fixed_plot_click)
    def _():
        turbidity_df = generate_turbidity_df()
        res = near_points(
            turbidity_df,
            input.generate_estuary_turbidity_fixed_plot_click(),
            xvar="turbidity_index_value",
            yvar="measure",
            max_points=1,
        )
        if len(res) == 1:
            date = res["date"].values[0]
            image_handler_list = get_turbidity_data()[0]
            to_select_idx = -1
            for idx, image_handler in enumerate(image_handler_list):
                if image_handler.date[:10] == date:
                    to_select_idx = idx
                    break
            if to_select_idx == -1:
                raise ValueError
            else:
                ui.update_slider("turbidity_fixed_image_idx", value=to_select_idx)

    @reactive.Effect
    @reactive.event(input.turbidity_fixed_precise_location)
    def create_turbidity_ui_visualisation_input():
        if input.turbidity_fixed_precise_location() != "Aucune":
            try:
                selected_box_size = input.turbidity_fixed_visualisation_box_size()
            except SilentException:
                selected_box_size = 100
            visualisation_box_size = ui.input_numeric(
                "turbidity_fixed_visualisation_box_size",
                "Taille de la boite de visualisation",
                value=selected_box_size,
                min=10,
                max=400,
                step=10,
            )

            ui.remove_ui("#turbidity-fixed-precise-location-visualisation-box")
            ui.insert_ui(
                ui.div(
                    {"id": "turbidity-fixed-precise-location-visualisation-box"},
                    visualisation_box_size,
                ),
                selector="#turbidity-fixed-precise-location",
                where="afterEnd",
            )
        elif input.turbidity_fixed_precise_location() == "Aucune":
            ui.remove_ui("#turbidity-fixed-precise-location-visualisation-box")

    @reactive.Calc
    def get_turbidity_image_handler():
        return get_turbidity_data()[0][input.turbidity_fixed_image_idx()]

    @reactive.Effect
    @reactive.event(input.turbidity_fixed_previous_button)
    def apply_turbidity_previous_buttion():
        current_image_index = input.turbidity_fixed_image_idx()
        new_image_index = max(0, current_image_index - 1)
        ui.update_slider("turbidity_fixed_image_idx", value=new_image_index)

    @reactive.Effect
    @reactive.event(input.turbidity_fixed_next_button)
    def apply_turbidity_next_buttion():
        current_image_index = input.turbidity_fixed_image_idx()
        number_of_image = get_number_of_turbidity_image()
        new_image_index = min(number_of_image - 1, current_image_index + 1)
        ui.update_slider("turbidity_fixed_image_idx", value=new_image_index)

    @reactive.Calc
    def get_row_col_of_turbidity_probe():
        image_handler = get_turbidity_image_handler()
        row_col = None
        _, _, turbidity_geo_coordinate_dict = get_turbidity_data()
        turbidity_geo_coordinate = turbidity_geo_coordinate_dict[image_handler.date[:4]]
        row_col = numpy.round(
            image_handler.get_row_col_index_from_longitide_latitude(
                turbidity_geo_coordinate["lon"], turbidity_geo_coordinate["lat"]
            )
        ).astype(int)

        return row_col

    @reactive.Effect
    @reactive.event(input.turbididty_fixed_save)
    def apply_arrow_save():
        image_handler = get_turbidity_image_handler()
        date = image_handler.date[:10]
        estuary_name = input.turbidity_fixed_estuary_name().lower()
        good_dates_data_path = "data/turbidity_fixed/good_dates.json"
        good_dates_data = load_json_data(good_dates_data_path)
        good_dates_data[estuary_name].append(date)
        good_dates_data[estuary_name] = list(set(good_dates_data[estuary_name]))
        good_dates_data[estuary_name] = sorted(good_dates_data[estuary_name])
        save_json_data(good_dates_data, good_dates_data_path)
        ui.notification_show(f"{date} is saved", duration=1)

    @output
    @render.plot
    def generate_turbidity_fixed_image():
        image_handler = get_turbidity_image_handler()
        fig, ax = plt.subplots(1, 1, frameon=False)
        alpha = None
        visualisation_mode = input.turbidity_fixed_visualisation()
        visualisation = None
        cmap = None
        vmin, vmax = None, None
        if visualisation_mode in [
            "Image couleur",
            "water_index_mask",
            "Index Turbidité",
        ]:
            im = image_handler.true_color_image
        elif visualisation_mode == "water_index":
            im = create_water_index_raster(image_handler)
        elif visualisation_mode == "NIR":
            im = image_handler.nir_band
            vmin, vmax = 1_000, 10_000
            cmap = "Reds"
            visualisation = im
            alpha = 1
        if visualisation_mode in ["water_index_mask", "Index Turbidité"]:
            water_index_mask = (
                create_water_index_raster(image_handler)
                > input.turbidity_fixed_water_index_mask_threshold()
            )
            if True:
                water_index_mask = (
                    water_index_mask
                    * image_handler.get_mask_from_bridge_points_handler()
                )
            alpha = water_index_mask.astype(float)
            if visualisation_mode == "Index Turbidité":
                smoothed_ndti_water_index_mask = (
                    get_smoothed_turbidity_index_water_index_mask(
                        image_handler,
                        input.turbidity_fixed_water_index_mask_threshold(),
                        input.turbidity_fixed_ndti_smoothed_sigma(),
                        input.turbidity_fixed_type_of_turbidity_index(),
                        True,
                    )
                )
                if input.turbidity_fixed_type_of_turbidity_index() == "NDTI":
                    vmin, vmax = -0.05, 0.05
                elif (
                    input.turbidity_fixed_type_of_turbidity_index() == "(665nm)/(833nm)"
                ):
                    vmin, vmax = 0.8, 1.2
                else:
                    if input.turbidity_fixed_atmoshperic_correction() == "Sen2Cor":
                        vmin, vmax = 1_000, 1_700
                    elif input.turbidity_fixed_atmoshperic_correction() == "Acolite":
                        vmin, vmax = 0.01, 0.08
            visualisation = (
                smoothed_ndti_water_index_mask
                if visualisation_mode == "Index Turbidité"
                else water_index_mask
            )
            cmap = "Reds" if visualisation_mode == "Index Turbidité" else "Blues"

        row, col = get_row_col_of_turbidity_probe()
        if input.turbidity_fixed_precise_location() == "Mesure de Turbidité":
            offset = int(input.turbidity_fixed_visualisation_box_size() / 2)
            box_size_string = input.turbidity_fixed_selection_box_size()
            box_size = int(box_size_string[0])
            min_row = max(0, row - offset)
            max_row = min(row + offset, im.shape[0] - 1)
            min_col = max(0, col - offset)
            max_col = min(col + offset, im.shape[1] - 1)

            im = im[min_row:max_row, min_col:max_col]
            if alpha is not None:
                alpha = alpha[min_row:max_row, min_col:max_col]
                visualisation = visualisation[min_row:max_row, min_col:max_col]
            row_point = row if min_row == 0 or max_row == im.shape[0] - 1 else offset
            col_point = col if min_col == 0 or max_col == im.shape[1] - 1 else offset
            row_box_start = row_point - box_size / 2
            col_box_start = col_point - box_size / 2

            rect = patches.Rectangle(
                (col_box_start, row_box_start),
                box_size,
                box_size,
                linewidth=1,
                edgecolor="g",
                facecolor="none",
            )
            ax.add_patch(rect)
        else:
            row_point, col_point = row, col

        ax.scatter(col_point, row_point, s=5)
        ax.imshow(im)
        if visualisation is not None:
            vis_ax = ax.imshow(
                visualisation,
                interpolation="nearest",
                cmap=cmap,
                alpha=alpha,
                vmin=vmin,
                vmax=vmax,
            )
            if visualisation_mode in ["Index Turbidité", "NIR"]:
                fig.colorbar(vis_ax, ax=ax, orientation="horizontal")
        plt.title(image_handler.date[:10])
        fig.patch.set_visible(False)
        plt.tight_layout()
        return fig

    @output
    @render.plot
    def generate_estuary_turbidity_fixed_plot():
        color_mapping_years = {"2022": "orange", "2023": "blue"}
        turbidity_df = generate_turbidity_df()
        image_handler = get_turbidity_image_handler()
        image_date = image_handler.date[:10]
        fig, ax = plt.subplots(1, 1, frameon=False)

        for year, color in color_mapping_years.items():
            year_turbidity_df = turbidity_df.loc[
                turbidity_df["date"].apply(lambda date_: date_[:4] == year)
            ]
            if len(year_turbidity_df) == 0:
                continue
            date_turbidity_df = year_turbidity_df.loc[
                year_turbidity_df["date"] == image_date
            ]
            non_date_turbidity_df = year_turbidity_df.loc[
                year_turbidity_df["date"] != image_date
            ]
            ax.scatter(
                non_date_turbidity_df["turbidity_index_value"].astype(float),
                non_date_turbidity_df["measure"].astype(float),
                s=10,
                color=color,
                marker=".",
                label=year,
            )
            ax.scatter(
                date_turbidity_df["turbidity_index_value"].astype(float),
                date_turbidity_df["measure"].astype(float),
                s=10,
                c=f"dark{color}",
                marker="x",
            )
        ax.set_xlabel(input.turbidity_fixed_type_of_turbidity_index())
        ylabel = (
            "Turbidité (FNU)"
            if input.turbidity_fixed_use_log_measure() is False
            else "Log(Turbidité (FNU))"
        )
        ax.set_ylabel(ylabel)
        ax.set_title(
            f"Mesure de la turbidity In Situ en fonction d'un indice de {input.turbidity_fixed_type_of_turbidity_index()}"
        )
        plt.legend()
        # ax.set_ylim(0,40)
        fig.patch.set_visible(False)
        plt.tight_layout()
        return fig
