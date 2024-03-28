from datetime import datetime, timedelta
import numpy
import pandas
from astropy.convolution import Gaussian2DKernel
from astropy.convolution import convolve
from outliers import smirnov_grubbs as grubbs

from satellite_image_handler.utils.normalize_index import create_water_index_raster

from turbidity_shiny.turbidity_index import create_turbidity_index_raster


def create_image_handler_date_dict(image_handler_list):
    image_handler_dict = {
        image_handler.date[:10]: image_handler for image_handler in image_handler_list
    }
    return image_handler_dict


def create_turbidity_df(
    image_handler_list,
    turbidity_measures_data,
    turbidity_location_data,
    water_index_threshold,
    box_size,
    ndti_smoothed_sigma,
    type_of_turbidity_index,
    exclude_points_from_bridge_points_handler,
    exlude_outlier,
    use_log_measure,
):
    image_handler_dict = create_image_handler_date_dict(image_handler_list)
    turbidity_df = pandas.DataFrame(
        columns=[
            "date",
            "location",
            "measure",
            "turbidity_index_value",
            "turbidity_index_std",
        ]
    )
    i = 0
    for measurement_dicts in turbidity_measures_data:
        date = measurement_dicts["date"]
        image_handler = image_handler_dict.get(date)
        if image_handler is None:
            continue
        measurements_list = measurement_dicts["spatial_turbidity_measurement"][
            "measurements_list"
        ]
        for measures in measurements_list:
            measure = numpy.median(measures["measures"])
            notes = measures["notes"]
            geo_coordinates = turbidity_location_data[notes]["geo_coordinates"]
            row, col = numpy.round(
                image_handler.get_row_col_index_from_longitide_latitude(
                    geo_coordinates["lon"], geo_coordinates["lat"]
                )
            ).astype(int)
            smoothed_turbidity_index_water_index_mask = (
                get_smoothed_turbidity_index_water_index_mask(
                    image_handler,
                    water_index_threshold,
                    ndti_smoothed_sigma,
                    type_of_turbidity_index,
                    exclude_points_from_bridge_points_handler,
                )
            )
            box_size_offset = box_size // 2
            box = smoothed_turbidity_index_water_index_mask[
                row - box_size_offset : row + box_size_offset + 1,
                col - box_size_offset : col + box_size_offset + 1,
            ]
            turbidity_index_value = numpy.nanmean(box)
            turbidity_index_std = numpy.nanstd(box)
            turbidity_df.loc[i, "date"] = date
            turbidity_df.loc[i, "location"] = notes
            turbidity_df.loc[i, "measure"] = measure
            turbidity_df.loc[i, "turbidity_index_value"] = turbidity_index_value
            turbidity_df.loc[i, "turbidity_index_std"] = turbidity_index_std
            i += 1
    turbidity_df["measure"] = turbidity_df["measure"].astype(float)
    if exlude_outlier is True:
        turbidity_df = turbidity_df[turbidity_df["measure"] < 70].reset_index(drop=True)
    if use_log_measure is True:
        turbidity_df["measure"] = turbidity_df["measure"].apply(numpy.log)
    turbidity_df["turbidity_index_value"] = turbidity_df[
        "turbidity_index_value"
    ].astype(float)
    turbidity_df["turbidity_index_std"] = turbidity_df["turbidity_index_std"].astype(
        float
    )
    return turbidity_df


def get_smoothed_turbidity_index_water_index_mask(
    image_handler,
    water_index_threshold,
    ndti_smoothed_sigma,
    type_of_turbidity_index,
    exclude_points_from_bridge_points_handler,
):
    turbidity_index = create_turbidity_index_raster(
        image_handler.red_band,
        image_handler.green_band,
        image_handler.nir_band,
        type_of_turbidity_index,
        image_handler,
    )
    water_index = create_water_index_raster(image_handler)
    water_index_mask = water_index > water_index_threshold
    if exclude_points_from_bridge_points_handler is True:
        water_index_mask = (
            water_index_mask * image_handler.get_mask_from_bridge_points_handler()
        )
    turbidity_index_water_mask = water_index_mask * turbidity_index
    turbidity_index_water_mask[water_index_mask == 0.0] = numpy.nan
    if ndti_smoothed_sigma == 0:
        return turbidity_index_water_mask
    else:
        gaussian_kernel = Gaussian2DKernel(
            x_stddev=ndti_smoothed_sigma,
            y_stddev=ndti_smoothed_sigma,
            x_size=7,
            y_size=7,
        )
        convole_ndti_water_mask = convolve(turbidity_index_water_mask, gaussian_kernel)
        convole_ndti_water_mask[water_index_mask == 0.0] = numpy.nan
        return convole_ndti_water_mask


def get_turbidity_from_image_handle_class_and_turbidity_df(
    image_handle_class, turbidity_df, window=0
):
    image_date = datetime.strptime(image_handle_class.date[:19], "%Y-%m-%dT%H:%M:%S")
    image_date = image_date - timedelta(hours=4)
    argmin_idx_location = (turbidity_df["date"] - image_date).abs().argmin()
    turbidity = turbidity_df.loc[
        argmin_idx_location - window : argmin_idx_location + window
    ]["filtered_interpolated_turbidity"].mean()
    time_diff = turbidity_df.loc[argmin_idx_location]["date"] - image_date
    return turbidity, time_diff


def create_turbidity_fixed_df(
    image_handler_list,
    fixed_turbidity_data,
    turbidity_geo_coordinate_dict,
    water_index_threshold,
    box_size,
    ndti_smoothed_sigma,
    type_of_turbidity_index,
    exclude_points_from_bridge_points_handler,
    exlude_outlier=False,
    use_log_measure=False,
    turdibidty_df_window=0,
):
    turbidity_df = pandas.DataFrame(
        columns=[
            "date",
            "measure",
            "turbidity_index_value",
        ]
    )
    for i, image_handler in enumerate(image_handler_list):
        turbidity, time_diff = get_turbidity_from_image_handle_class_and_turbidity_df(
            image_handler, fixed_turbidity_data, turdibidty_df_window
        )
        image_date = datetime.strptime(image_handler.date[:19], "%Y-%m-%dT%H:%M:%S")
        if numpy.abs(time_diff).days == 0 and image_date < datetime(2023, 11, 19):
            smoothed_turbidity_index_water_index_mask = (
                get_smoothed_turbidity_index_water_index_mask(
                    image_handler,
                    water_index_threshold,
                    ndti_smoothed_sigma,
                    type_of_turbidity_index,
                    exclude_points_from_bridge_points_handler,
                )
            )
            turbidity_geo_coordinate = turbidity_geo_coordinate_dict[
                image_handler.date[:4]
            ]
            row, col = numpy.round(
                image_handler.get_row_col_index_from_longitide_latitude(
                    turbidity_geo_coordinate["lon"], turbidity_geo_coordinate["lat"]
                )
            ).astype(int)
            box_size_offset = box_size // 2
            box = smoothed_turbidity_index_water_index_mask[
                row - box_size_offset : row + box_size_offset + 1,
                col - box_size_offset : col + box_size_offset + 1,
            ]
            turbidity_index_value = numpy.nanmean(box)

            turbidity_df.loc[i, "date"] = image_handler.date[:10]
            turbidity_df.loc[i, "measure"] = turbidity
            turbidity_df.loc[i, "turbidity_index_value"] = turbidity_index_value
    turbidity_df["measure"] = turbidity_df["measure"].astype(float)
    turbidity_df = turbidity_df[~turbidity_df["measure"].isna()].reset_index(drop=True)
    turbidity_df["turbidity_index_value"] = turbidity_df[
        "turbidity_index_value"
    ].astype(float)
    if exlude_outlier:
        non_outlier_index = ~numpy.isin(
            turbidity_df["measure"],
            grubbs.max_test_outliers(turbidity_df["measure"].values, alpha=0.05),
        )
        turbidity_df = turbidity_df[non_outlier_index].reset_index(drop=True)

    return turbidity_df
