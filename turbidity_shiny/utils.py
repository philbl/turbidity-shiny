import lzma
import pickle
import re
import json

from satellite_image_handler.abstract_satellite_image_handler.abstract_sentinel_image_handler import (
    AbstractSentinelImageHandler,
)


def load_pickle_data(path):
    if "lzma" in path:
        with lzma.open(path, "rb") as f:
            data = pickle.load(f)
    else:
        with open(path, "rb") as f:
            data = pickle.load(f)
    return data


def load_json_data(path):
    with open(path, "r") as f:
        json_data = json.load(f)
    return json_data


def save_json_data(data, path):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def get_all_sorted_date_from_pickle_list_of_image_handler(
    image_handler_list: AbstractSentinelImageHandler,
):
    return [image_handler.date[:10] for image_handler in image_handler_list]


def get_measurement_for_single_date(date, measurement_list):
    """
    date is YYYY-MM-DD
    """
    measurement_single_date_list = []
    for measurement in measurement_list:
        if measurement["date"] == date:
            measurement_single_date_list.append(measurement)
    return measurement_single_date_list


def delete_bridge_precise_depth_string(string):
    bridge_suffix_pattern = r"( surface| bottom)$"
    result = re.sub(bridge_suffix_pattern, "", string)
    return result
