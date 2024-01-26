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
from satellite_image_handler.utils.bridge_points_handler import BridgePointsHandler

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
        bridge_points_path = f"../data/points_ponts/{estuary_name}"
        bridge_points_handler = BridgePointsHandler(bridge_points_path)
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
            image_handler_class(str(image_path), bridge_points_handler)
            for image_path in tqdm(image_list_2023)
        ]
        image_handler_2023_list = sorted(
            image_handler_2023_list, key=lambda image_handler: image_handler.date
        )

        with open(f"data/turbidity/{estuary_name}_2023.pkl", "wb") as f:
            pickle.dump(image_handler_2023_list, f)
