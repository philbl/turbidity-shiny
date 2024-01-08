from pathlib import Path
import pickle
from tqdm import tqdm

from turbidity_shiny.utils import load_json_data

from satellite_image_handler.sentinel_image_handler import (  # noqa F401
    CocagneSentinelImageHandler,
    BouctoucheSentinelImageHandler,
    WestSentinelImageHandler,
    MorellSentinelImageHandler,
    DunkSentinelImageHandler,
)

ESTUARY_NAME_DICT = {
    "dunk": DunkSentinelImageHandler,
    "cocagne": CocagneSentinelImageHandler,
    "bouctouche": BouctoucheSentinelImageHandler,
    "west": WestSentinelImageHandler,
    "morell": MorellSentinelImageHandler,
}

if __name__ == "__main__":
    good_dates_dict = load_json_data("data/turbidity/good_dates.json")
    for estuary_name, image_handler_class in ESTUARY_NAME_DICT.items():
        good_dates_list = good_dates_dict[estuary_name]
        image_list = list(Path(f"../data/sentinel2_data/{estuary_name}").iterdir())
        image_list_2023 = list(
            filter(
                lambda path: any(
                    good_dates in str(path) for good_dates in good_dates_list
                ),
                image_list,
            )
        )

        image_handler_2023_list = [
            image_handler_class(str(image_path)) for image_path in tqdm(image_list_2023)
        ]
        image_handler_2023_list = sorted(
            image_handler_2023_list, key=lambda image_handler: image_handler.date
        )

        # turbidity_data = load_json_data(f"../data/field_work/json/summer_2023/{estuary_name}.json")

        # dates_list = []
        # for spot_measures in turbidity_data:
        #     dates_list.append(spot_measures["date"])
        # dates_list = list(set(dates_list))

        # images_date_tuple = [
        #     (image_handler, image_handler.date[:10])
        #     for image_handler in image_handler_2023_list
        # ]

        # images_date_tuple = list(
        #     filter(
        #         lambda image_date: image_date[1] in dates_list,
        #         images_date_tuple,
        #     )
        # )

        with open(f"data/turbidity/{estuary_name}_2023.pkl", "wb") as f:
            pickle.dump(image_handler_2023_list, f)
