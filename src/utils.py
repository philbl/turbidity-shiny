import lzma
import pickle

from satellite_image_handler.abstract_satellite_image_handler.abstract_sentinel_image_handler import (
    AbstractSentinelImageHandler,
)


def load_pickle_data(path):
    with lzma.open(path, "rb") as f:
        data = pickle.load(f)
    return data


def get_all_sorted_date_from_pickle_list_of_image_handler(
    image_handler_list: AbstractSentinelImageHandler,
):
    return [image_handler.date[:10] for image_handler in image_handler_list]
