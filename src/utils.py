import lzma
import pickle

from src.satellite_image_processing.image_handler.abstract_image_handler import (
    AbstractImageHandler,
)


def load_pickle_data(path):
    with lzma.open(path, "rb") as f:
        data = pickle.load(f)
    return data


def get_all_sorted_date_from_pickle_list_of_image_handler(
    image_handler_list: AbstractImageHandler,
):
    return [image_handler.date[:10] for image_handler in image_handler_list]
