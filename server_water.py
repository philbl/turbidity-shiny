import matplotlib.pyplot as plt
from shiny import ui, render, reactive, Session
from skimage import filters
from scipy import ndimage
from satellite_image_handler.utils.normalize_index import create_ndwi_raster

from turbidity_shiny.utils import load_pickle_data
from information import (
    SCENE_CLF_WATER_MASK_INFO_HTML,
    NDWI_WATER_MASK_INFO_HTML,
    INFORMATION_STRING,
)


def server_water(input, output, session: Session):
    @reactive.Calc
    def load_water_data():
        estuary_name = input.water_estuary_name().lower()
        data = load_pickle_data(f"data/{estuary_name}_2022.lzma.pkl")
        return data

    @reactive.Calc
    def get_number_of_water_image():
        return len(load_water_data())

    @reactive.Effect
    @reactive.event(input.info_scene_clf)
    def info_scene_clf():
        modal = ui.modal(
            SCENE_CLF_WATER_MASK_INFO_HTML,
            title="Masque d'eau Scene CLF",
            easy_close=True,
            footer=None,
        )
        ui.modal_show(modal)

    @reactive.Effect
    @reactive.event(input.info_ndwi)
    def info_ndwi():
        modal = ui.modal(
            NDWI_WATER_MASK_INFO_HTML,
            title="Masque d'eau NDWI",
            easy_close=True,
            footer=None,
        )
        ui.modal_show(modal)

    @reactive.Effect
    def update_water_slider_idx():
        number_of_image = get_number_of_water_image()
        ui.update_slider(
            "water_image_idx", min=0, max=number_of_image - 1, value=0, step=1
        ),

    @reactive.Effect
    @reactive.event(input.switch_scene_clf_water_mask)
    def apply_switch_scene_clf_water_mask():
        if input.switch_scene_clf_water_mask() is True:
            sigma_input = ui.input_numeric(
                "scene_clf_water_sigma",
                "Scene Clf Masque d'eau Sigma",
                value=2,
                min=1,
                max=14,
                step=1,
            )
            threshold_input = ui.input_numeric(
                "scene_clf_water_threshold",
                "Scene Clf Masque d'eau Threshold",
                value=0.75,
                min=0,
                max=1,
                step=0.05,
            )
            ui.insert_ui(
                ui.div({"id": "scene-clf-water-threshold"}, threshold_input),
                selector="#scene-clf-switch",
                where="afterEnd",
            )
            ui.insert_ui(
                ui.div({"id": "scene-clf-water-sigma"}, sigma_input),
                selector="#scene-clf-switch",
                where="afterEnd",
            )
        elif input.switch_scene_clf_water_mask() is False:
            ui.remove_ui("#scene-clf-water-sigma")
            ui.remove_ui("#scene-clf-water-threshold")

    @reactive.Effect
    @reactive.event(input.switch_ndwi_water_mask)
    def apply_switch_ndwi_water_mask():
        if input.switch_ndwi_water_mask() is True:
            ndwi_threshold = (
                ui.input_numeric(
                    "ndwi_water_1st_threshold",
                    "NDWI Masque d'eau 1er Threshold",
                    value=-0.05,
                    min=-0.1,
                    max=0.1,
                    step=0.01,
                ),
            )
            sigma_input = (
                ui.input_numeric(
                    "ndwi_water_sigma",
                    "NDWI Masque d'eau Sigma",
                    value=2,
                    min=1,
                    max=14,
                    step=1,
                ),
            )
            gaussian_threshold_input = (
                ui.input_numeric(
                    "ndwi_water_2nd_threshold",
                    "NDWI Masque d'eau 2e Threshold",
                    value=0.75,
                    min=0,
                    max=1,
                    step=0.05,
                ),
            )
            ui.insert_ui(
                ui.div({"id": "ndwi-water-2nd-threshold"}, gaussian_threshold_input),
                selector="#ndwi-switch",
                where="afterEnd",
            )
            ui.insert_ui(
                ui.div({"id": "ndwi-water-sigma"}, sigma_input),
                selector="#ndwi-switch",
                where="afterEnd",
            )
            ui.insert_ui(
                ui.div({"id": "ndwi-water-1st-threshold"}, ndwi_threshold),
                selector="#ndwi-switch",
                where="afterEnd",
            )
        elif input.switch_ndwi_water_mask() is False:
            ui.remove_ui("#ndwi-water-sigma")
            ui.remove_ui("#ndwi-water-1st-threshold")
            ui.remove_ui("#ndwi-water-2nd-threshold")

    @output
    @render.text
    def general_informations():
        return INFORMATION_STRING

    @output
    @render.text
    def turbidity_info():
        return "Travaux en cours."

    @reactive.Calc
    def get_water_image_handler():
        return load_water_data()[input.water_image_idx()]

    @reactive.Effect
    @reactive.event(input.water_previous_button)
    def apply_water_previous_buttion():
        current_image_index = input.water_image_idx()
        new_image_index = max(0, current_image_index - 1)
        ui.update_slider("water_image_idx", value=new_image_index)

    @reactive.Effect
    @reactive.event(input.water_next_button)
    def apply_water_next_buttion():
        current_image_index = input.water_image_idx()
        number_of_image = get_number_of_water_image()
        new_image_index = min(number_of_image - 1, current_image_index + 1)
        ui.update_slider("water_image_idx", value=new_image_index)

    @reactive.Calc
    def get_water_mask_dict():
        water_mask_dict = {}
        if input.switch_scene_clf_water_mask() is True:
            sigma = input.scene_clf_water_sigma()
            threshold = input.scene_clf_water_threshold()
            image_handler = get_water_image_handler()
            water_mask = image_handler.get_smoothed_water_mask(
                sigma=sigma, threshold=threshold
            )
            edge_sobel = filters.sobel(water_mask)
            edge_sobel_mask = edge_sobel >= 0.25
            water_mask_dict["scene_clf_water_mask"] = {
                "label": "Scene Clf",
                "mask": edge_sobel_mask,
                "cmap": "Reds",
            }

        if input.switch_ndwi_water_mask() is True:
            sigma = input.ndwi_water_sigma()
            threshold_1 = input.ndwi_water_1st_threshold()
            threshold_2 = input.ndwi_water_2nd_threshold()
            image_handler = get_water_image_handler()
            ndwi_water_mask = (
                create_ndwi_raster(image_handler.green_band, image_handler.nir_band)
                > threshold_1
            )
            ndwi_water_mask = (
                ndimage.gaussian_filter(ndwi_water_mask.astype(float), sigma=sigma)
                > threshold_2
            )
            ndwi_edge_sobel = filters.sobel(ndwi_water_mask)
            ndwi_edge_sobel_mask = ndwi_edge_sobel >= 0.25
            water_mask_dict["ndwi_water_mask"] = {
                "label": "NDWI",
                "mask": ndwi_edge_sobel_mask,
                "cmap": "Blues",
            }

        return water_mask_dict

    xmin = reactive.Value(None)
    xmax = reactive.Value(None)
    ymin = reactive.Value(None)
    ymax = reactive.Value(None)

    def from_y_brush_to_y_plot(y_brush, h, w):
        ratio = 1.5
        new_h = w / ratio
        pixel_value = h / new_h
        number_of_pixel_in_h = pixel_value * h
        buffer = (h - number_of_pixel_in_h) / 2

        return (y_brush - buffer) / pixel_value

    @reactive.Effect
    @reactive.event(input.generate_water_image_dblclick)
    def change_coords():
        image_handler = get_water_image_handler()
        rgb_im = image_handler.true_color_image
        h = rgb_im.shape[0]
        w = rgb_im.shape[1]
        if input.generate_water_image_brush() is not None:
            input_brush = input.generate_water_image_brush()
            xmin.set(int(input_brush["xmin"]))
            xmax.set(int(input_brush["xmax"]))
            ymin.set(int(from_y_brush_to_y_plot(input_brush["ymin"], h, w)))
            ymax.set(int(from_y_brush_to_y_plot(input_brush["ymax"], h, w)))

        else:
            xmin.set(None)
            xmax.set(None)
            ymin.set(None)
            ymax.set(None)

    @output
    @render.plot
    def generate_water_image():
        image_handler = get_water_image_handler()
        rgb_im = image_handler.true_color_image
        fig, ax = plt.subplots(1, 1, frameon=False)
        ax.imshow(rgb_im)
        for water_mask_name, water_mask_dict in get_water_mask_dict().items():
            label = water_mask_dict["label"]
            mask = water_mask_dict["mask"]
            cmap = water_mask_dict["cmap"]
            ax.imshow(mask, interpolation="nearest", cmap=cmap, alpha=mask * 1.0)
            ax.plot(0, 0, c=cmap[0].lower(), label=label)
            plt.legend()
        # plt.axis("off")
        plt.title(image_handler.date[:10])
        fig.patch.set_visible(False)
        # plt.title(f"xmin: {xmin.get()} xmax: {xmax.get()} ymin: {ymin.get()} ymax: {ymax.get()} shape: {rgb_im.shape}")
        plt.tight_layout()
        plt.xlim((xmin.get(), xmax.get()))
        plt.ylim((ymax.get(), ymin.get()))
        return fig
