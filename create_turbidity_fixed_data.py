from pathlib import Path
import pickle
from tqdm import tqdm

from turbidity_shiny.utils import (
    load_json_data,
)

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
    # "cocagne": CocagneSentinelImageHandler,
    # "bouctouche": BouctoucheSentinelImageHandler,
    # "west": WestSentinelImageHandler,
    # "morell": MorellSentinelImageHandler,
}


if __name__ == "__main__":
    good_dates_dict = load_json_data("data/turbidity_fixed/2022/good_dates.json")
    for estuary_name, image_handler_class in ESTUARY_NAME_DICT.items():
        bridge_points_path = f"../data/points_ponts/{estuary_name}"
        bridge_points_handler = BridgePointsHandler(bridge_points_path)
        image_list_path = list(Path(f"../data/sentinel2_data/{estuary_name}").iterdir())
        good_dates_list = good_dates_dict[estuary_name]
        image_list_good_dates_path = list(
            filter(
                lambda path: any(
                    good_dates.replace("-", "") in str(path)
                    for good_dates in good_dates_list
                ),
                image_list_path,
            )
        )

        image_list = [
            image_handler_class(path, bridge_points_handler)
            for path in tqdm(image_list_good_dates_path)
        ]
        image_list = [
            image for image in image_list if image.date[:10] in good_dates_list
        ]
        image_list = sorted(image_list, key=lambda image_handler: image_handler.date)
        with open(f"data/turbidity_fixed/2022/{estuary_name}.pkl", "wb") as f:
            pickle.dump(image_list, f)
        del image_list
