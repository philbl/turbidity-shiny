import numpy
import pandas
from astropy.convolution import Gaussian2DKernel
from astropy.convolution import convolve


from satellite_image_handler.utils.normalize_index import create_ndwi_raster

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
    ndwi_threshold,
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
            smoothed_turbidity_index_ndwi_mask = get_smoothed_turbidity_index_ndwi_mask(
                image_handler,
                ndwi_threshold,
                ndti_smoothed_sigma,
                type_of_turbidity_index,
                exclude_points_from_bridge_points_handler,
            )
            box_size_offset = box_size // 2
            box = smoothed_turbidity_index_ndwi_mask[
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


def get_smoothed_turbidity_index_ndwi_mask(
    image_handler,
    ndwi_threshold,
    ndti_smoothed_sigma,
    type_of_turbidity_index,
    exclude_points_from_bridge_points_handler,
):
    turbidity_index = create_turbidity_index_raster(
        image_handler.red_band,
        image_handler.green_band,
        image_handler.nir_band,
        type_of_turbidity_index,
    )
    ndwi = create_ndwi_raster(image_handler.green_band, image_handler.nir_band)
    ndwi_mask = ndwi > ndwi_threshold
    if exclude_points_from_bridge_points_handler is True:
        ndwi_mask = ndwi_mask * image_handler.get_mask_from_bridge_points_handler()
    turbidity_index_water_mask = ndwi_mask * turbidity_index
    turbidity_index_water_mask[ndwi_mask == 0.0] = numpy.nan
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
        convole_ndti_water_mask[ndwi_mask == 0.0] = numpy.nan
        return convole_ndti_water_mask
