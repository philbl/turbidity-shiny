import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy
from shiny import ui, render, reactive, Session
from shiny.types import SilentException

from satellite_image_handler.utils.normalize_index import create_ndwi_raster
from shiny.plotutils import near_points


from turbidity_shiny.utils import (
    load_json_data,
    save_json_data,
)
from turbidity_shiny.turbidity.turbidity_df import (
    create_turbidity_df,
    get_smoothed_turbidity_index_ndwi_mask,
)
from turbidity_shiny.turbidity.load_data import load_turbidity_data


def server_turbidity(input, output, session: Session):
    @reactive.Calc
    def get_turbidity_data():
        (
            image_handler_list,
            turbidity_measures_data,
            turbidity_location_data,
        ) = load_turbidity_data(
            input.turbidity_estuary_name(), input.modified_turbidity_location_switch()
        )
        return image_handler_list, turbidity_measures_data, turbidity_location_data

    @reactive.Calc
    def get_all_specific_locations():
        turbidity_location_data = get_turbidity_data()[2]
        location_name_list = list(turbidity_location_data.keys())
        location_name_list = ["Aucune"] + sorted(location_name_list)

        return location_name_list

    @reactive.Calc
    def get_number_of_turbidity_image():
        return len(get_turbidity_data()[0])

    @reactive.Calc()
    def generate_turbidity_df():
        (
            image_handler_list,
            turbidity_measures_data,
            turbidity_location_data,
        ) = get_turbidity_data()
        box_size_string = input.turbidity_selection_box_size()
        box_size = int(box_size_string[0])
        ndwi_mask_threshold = input.ndwi_mask_threshold()
        ndti_smoothed_sigma = input.ndti_smoothed_sigma()
        turbidity_df = create_turbidity_df(
            image_handler_list,
            turbidity_measures_data,
            turbidity_location_data,
            ndwi_mask_threshold,
            box_size,
            ndti_smoothed_sigma,
            input.type_of_turbidity_index(),
        )
        turbidity_data_subset = input.turbidity_data_subset()
        if turbidity_data_subset == "Centre Seulement":
            turbidity_df = turbidity_df[
                turbidity_df["location"].apply(
                    lambda location: "bottom" in location or "surface" in location
                )
            ]
        elif turbidity_data_subset == "South (ou West) Seulement":
            turbidity_df = turbidity_df[
                turbidity_df["location"].apply(
                    lambda location: "South" in location or "West" in location
                )
            ]
        elif turbidity_data_subset == "North (ou East) Seulement":
            turbidity_df = turbidity_df[
                turbidity_df["location"].apply(
                    lambda location: "North" in location or "East" in location
                )
            ]
        elif turbidity_data_subset == "Shore Seulement":
            turbidity_df = turbidity_df[
                turbidity_df["location"].apply(lambda location: "shore" in location)
            ]
        return turbidity_df

    @reactive.Effect
    def update_locations_list():
        locations_list = get_all_specific_locations()
        ui.update_select(
            "turbidity_precise_location", choices=locations_list, selected="Aucune"
        )

    @reactive.Effect
    def update_turbidity_slider_idx():
        number_of_image = get_number_of_turbidity_image()
        ui.update_slider(
            "turbidity_image_idx", min=0, max=number_of_image - 1, value=0, step=1
        ),

    @reactive.Effect
    @reactive.event(input.generate_estuary_turbidity_plot_click)
    def _():
        turbidity_df = generate_turbidity_df()
        res = near_points(
            turbidity_df,
            input.generate_estuary_turbidity_plot_click(),
            xvar="turbidity_index_value",
            yvar="measure",
            max_points=1,
        )
        if len(res) == 1:
            location = res["location"].values[0]
            date = res["date"].values[0]
            ui.update_select("turbidity_precise_location", selected=location)
            image_handler_list = get_turbidity_data()[0]
            to_select_idx = -1
            for idx, image_handler in enumerate(image_handler_list):
                if image_handler.date[:10] == date:
                    to_select_idx = idx
                    break
            if to_select_idx == -1:
                raise ValueError
            else:
                ui.update_slider("turbidity_image_idx", value=to_select_idx)

    @reactive.Effect
    @reactive.event(input.turbidity_precise_location)
    def create_turbidity_ui_visualisation_input():
        if input.turbidity_precise_location() != "Aucune":
            try:
                selected_box_size = input.turbidity_visualisation_box_size()
            except SilentException:
                selected_box_size = 100
            visualisation_box_size = ui.input_numeric(
                "turbidity_visualisation_box_size",
                "Taille de la boite de visualisation",
                value=selected_box_size,
                min=10,
                max=400,
                step=10,
            )
            moving_arrow_list = [
                ui.row(
                    ui.column(
                        2, ui.input_action_button("arrow_down", "\u2193"), offset=3
                    ),
                ),
                ui.row(
                    ui.column(2, ui.input_action_button("arrow_left", "\u2190")),
                    ui.column(
                        3, ui.input_action_button("arrow_save", "Save"), offset=1
                    ),
                    ui.column(2, ui.input_action_button("arrow_right", "\u2192")),
                ),
                ui.row(
                    ui.column(
                        2, ui.input_action_button("arrow_up", "\u2191"), offset=3
                    ),
                ),
            ]
            ui.remove_ui("#turbidity-precise-location-visualisation-box")
            for i in range(len(moving_arrow_list)):
                ui.remove_ui(f"#turbidity-precise-location-arrow{i}")
            for i, moving_arrow in enumerate(moving_arrow_list):
                ui.insert_ui(
                    ui.div(
                        {"id": f"turbidity-precise-location-arrow{i}"}, moving_arrow
                    ),
                    selector="#turbidity-precise-location",
                    where="afterEnd",
                )
            ui.insert_ui(
                ui.div(
                    {"id": "turbidity-precise-location-visualisation-box"},
                    visualisation_box_size,
                ),
                selector="#turbidity-precise-location",
                where="afterEnd",
            )
        elif input.turbidity_precise_location() == "Aucune":
            ui.remove_ui("#turbidity-precise-location-visualisation-box")
            for i in range(3):
                ui.remove_ui(f"#turbidity-precise-location-arrow{i}")

    @reactive.Calc
    def get_turbidity_image_handler():
        return get_turbidity_data()[0][input.turbidity_image_idx()]

    @reactive.Effect
    @reactive.event(input.turbidity_previous_button)
    def apply_turbidity_previous_buttion():
        current_image_index = input.turbidity_image_idx()
        new_image_index = max(0, current_image_index - 1)
        ui.update_slider("turbidity_image_idx", value=new_image_index)

    @reactive.Effect
    @reactive.event(input.turbidity_next_button)
    def apply_turbidity_next_buttion():
        current_image_index = input.turbidity_image_idx()
        number_of_image = get_number_of_turbidity_image()
        new_image_index = min(number_of_image - 1, current_image_index + 1)
        ui.update_slider("turbidity_image_idx", value=new_image_index)

    row_spot = reactive.Value(None)
    col_spot = reactive.Value(None)

    @reactive.Effect
    @reactive.event(input.arrow_down)
    def apply_arrow_down():
        row = row_spot.get()
        row_spot.set(row + 1)

    @reactive.Effect
    @reactive.event(input.arrow_up)
    def apply_arrow_up():
        row = row_spot.get()
        row_spot.set(row - 1)

    @reactive.Effect
    @reactive.event(input.arrow_left)
    def apply_arrow_left():
        col = col_spot.get()
        col_spot.set(col - 1)

    @reactive.Effect
    @reactive.event(input.arrow_right)
    def apply_arrow_right():
        col = col_spot.get()
        col_spot.set(col + 1)

    @reactive.Effect
    @reactive.event(input.arrow_save)
    def apply_arrow_save():
        row = row_spot.get()
        col = col_spot.get()
        image_handler = get_turbidity_image_handler()
        longitude, latitude = image_handler.get_longitude_latitude_from_row_col_index(
            row, col
        )
        estuary_name = input.turbidity_estuary_name().lower()
        modified_turbidity_location_data_path = f"../data/field_work/json/summer_2023/modified_location/{estuary_name}_location.json"
        turbidity_precise_location = input.turbidity_precise_location()
        modified_turbidity_location_data = load_json_data(
            modified_turbidity_location_data_path
        )
        modified_turbidity_location_data[turbidity_precise_location] = {
            "geo_coordinates": {"lat": latitude, "lon": longitude}
        }
        save_json_data(
            modified_turbidity_location_data, modified_turbidity_location_data_path
        )

    @reactive.Calc
    def get_row_col_of_specific_location():
        image_handler = get_turbidity_image_handler()
        turbidity_precise_location = input.turbidity_precise_location()
        row_col = None
        if turbidity_precise_location != "Aucune":
            _, _, turbidity_location_data = get_turbidity_data()
            geo_coordinates = turbidity_location_data.get(
                turbidity_precise_location
            ).get("geo_coordinates")
            row_col = numpy.round(
                image_handler.get_row_col_index_from_longitide_latitude(
                    geo_coordinates["lon"], geo_coordinates["lat"]
                )
            ).astype(int)
            if row_col is None:
                raise ValueError("Le spot n'existe pas")
            row, col = row_col
        else:
            row, col = None, None
        row_spot.set(row)
        col_spot.set(col)

    @output
    @render.plot
    def generate_turbidity_image():
        image_handler = get_turbidity_image_handler()
        fig, ax = plt.subplots(1, 1, frameon=False)
        alpha = None
        visualisation_mode = input.turbidity_visualisation()
        visualisation = None
        cmap = None
        vmin, vmax = None, None
        if visualisation_mode in ["Image couleur", "NDWI_mask", "Index Turbidité"]:
            im = image_handler.true_color_image
        elif visualisation_mode == "NDWI":
            im = create_ndwi_raster(image_handler.green_band, image_handler.nir_band)
        if visualisation_mode in ["NDWI_mask", "Index Turbidité"]:
            ndwi_mask = (
                create_ndwi_raster(image_handler.green_band, image_handler.nir_band)
                > input.ndwi_mask_threshold()
            )
            alpha = ndwi_mask.astype(float)
            if visualisation_mode == "Index Turbidité":
                smoothed_ndti_ndwi_mask = get_smoothed_turbidity_index_ndwi_mask(
                    image_handler,
                    input.ndwi_mask_threshold(),
                    input.ndti_smoothed_sigma(),
                    input.type_of_turbidity_index(),
                )
                if input.type_of_turbidity_index() == "NDTI":
                    vmin, vmax = -0.05, 0.05
                else:
                    vmin, vmax = 1_000, 2_000
            visualisation = (
                smoothed_ndti_ndwi_mask
                if visualisation_mode == "Index Turbidité"
                else ndwi_mask
            )
            cmap = "Reds" if visualisation_mode == "Index Turbidité" else "Blues"

        get_row_col_of_specific_location()
        if row_spot.get() is not None and col_spot.get() is not None:
            offset = int(input.turbidity_visualisation_box_size() / 2)
            box_size_string = input.turbidity_selection_box_size()
            box_size = int(box_size_string[0])
            row, col = row_spot.get(), col_spot.get()
            # row, col = row_col
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
            ax.scatter(col_point, row_point, s=5)
            rect = patches.Rectangle(
                (col_box_start, row_box_start),
                box_size,
                box_size,
                linewidth=1,
                edgecolor="g",
                facecolor="none",
            )
            ax.add_patch(rect)
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
            if visualisation_mode == "Index Turbidité":
                fig.colorbar(vis_ax, ax=ax, orientation="horizontal")
        plt.title(image_handler.date[:10])
        fig.patch.set_visible(False)
        plt.tight_layout()
        return fig

    @output
    @render.plot
    def generate_estuary_turbidity_plot():
        turbidity_df = generate_turbidity_df()
        image_spot = input.turbidity_precise_location()
        fig, ax = plt.subplots(1, 1, frameon=False)
        color_mapping_estuaries = {
            "bouctouche": {
                "2023-07-20": "blue",
                "2023-07-25": "orange",
                "2023-08-04": "green",
            },
            "cocagne": {
                "2023-07-20": "blue",
                "2023-07-25": "orange",
                "2023-08-04": "green",
            },
            "dunk": {"2023-06-12": "blue", "2023-08-01": "orange"},
            "west": {"2023-08-01": "blue"},
            "morell": {"2023-07-24": "blue"},
        }
        estuary_name = input.turbidity_estuary_name().lower()
        color_estuary_mapping = color_mapping_estuaries[estuary_name]
        for date, color in color_estuary_mapping.items():
            date_turbidity_df = turbidity_df.loc[turbidity_df["date"] == date]
            spot_date_turbidity_df = date_turbidity_df.loc[
                date_turbidity_df["location"] == image_spot
            ]
            non_spot_date_turbidity_df = date_turbidity_df.loc[
                date_turbidity_df["location"] != image_spot
            ]
            alpha = 1 if image_spot == "Aucune" else 0.5
            ax.scatter(
                non_spot_date_turbidity_df["turbidity_index_value"].astype(float),
                non_spot_date_turbidity_df["measure"].astype(float),
                s=10,
                c=color,
                label=date,
                alpha=alpha,
                marker=".",
            )
            if image_spot != "Aucune":
                ax.scatter(
                    spot_date_turbidity_df["turbidity_index_value"].astype(float),
                    spot_date_turbidity_df["measure"].astype(float),
                    s=10,
                    c=f"dark{color}",
                    marker="x",
                )
            ax.set_xlabel(input.type_of_turbidity_index())
            ax.set_ylabel("Turbidité (FNU)")
            ax.set_title(
                f"Mesure de la turbidity In Situ en fonction d'un indice de {input.type_of_turbidity_index()}"
            )
        plt.legend()
        fig.patch.set_visible(False)
        plt.tight_layout()
        return fig
