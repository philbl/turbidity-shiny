import lzma
import gzip  # noqa F401
import numpy
from pathlib import Path
import pickle
from tqdm import tqdm

from satellite_image_handler.sentinel_image_handler import (  # noqa F401
    CocagneSentinelImageHandler,
    BouctoucheSentinelImageHandler,
    WestSentinelImageHandler,
    MorellSentinelImageHandler,
    DunkSentinelImageHandler,
)

ESTUARY_NAME = "dunk"
IMAGE_HANDLER_CLASS = DunkSentinelImageHandler
NO_CLOUD_IDX_2022_DICT = {
    "bouctouche": 15,
    "cocagne": 15,
    "west": 7,
    "morell": 2,
    "dunk": 1,
}
THRESHOLD_DICT = {
    "bouctouche": 0.65,
    "cocagne": 0.65,
    "west": 0.65,
    "morell": 0.45,
    "dunk": 0.65,
}


if __name__ == "__main__":
    image_list = list(
        Path(f"../turbidity-analysis/data/sentinel2_data/{ESTUARY_NAME}").iterdir()
    )
    image_list_2022 = list(filter(lambda path: "2022" in str(path), image_list))

    image_handler_2022_list = [
        IMAGE_HANDLER_CLASS(str(image_path)) for image_path in tqdm(image_list_2022)
    ]
    image_handler_2022_list = sorted(
        image_handler_2022_list, key=lambda image_handler: image_handler.date
    )

    no_cloud_idx = NO_CLOUD_IDX_2022_DICT[ESTUARY_NAME]
    threshold = THRESHOLD_DICT[ESTUARY_NAME]
    WATER_MASK = (
        image_handler_2022_list[no_cloud_idx]
        .get_smoothed_water_mask(sigma=2, threshold=threshold)
        .astype(float)
    )

    cloud_free_images = list(
        filter(
            lambda ih: numpy.nanmean(
                (WATER_MASK * numpy.isin(ih.scene_clf, [3, 8, 9, 10]).astype(float))
            )
            < 0.01,
            image_handler_2022_list,
        )
    )

    with lzma.open(f"data/{ESTUARY_NAME}_2022.lzma.pkl", "wb") as f:
        pickle.dump(cloud_free_images, f)
