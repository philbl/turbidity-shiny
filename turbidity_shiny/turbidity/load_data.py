import pandas

from turbidity_shiny.utils import (
    load_json_data,
    load_pickle_data,
    convert_string_date_to_datetime_2022,
    convert_string_date_to_datetime_2023,
    get_turbidity_geo_coordinates_from_path,
)


GEO_COORDINATE_PATH_DICT = {
    "dunk": "field_may_10_dunk.json",
    "cocagne": "field_may_11_cocagne.json",
    "bouctouche": "field_may_11_bouctouche.json",
    "west": "field_may_9_west.json",
    "morell": "field_may_10_morell.json",
}


def load_turbidity_data(
    estuary_name, modified_turbidity_location, atmoshperic_correction
):
    """
    Load turbidity data for a specific estuary.

    Parameters:
    - estuary_name (str): The name of the estuary. It is case-insensitive.
    - modified_turbidity_location (str): The location type for turbidity data, either "Original" or "Modifiée manuellement".

    Returns:
    tuple: A tuple containing three elements:
        1. list: Image handler list loaded from the pickled data file.
        2. dict: Turbidity measures data loaded from the JSON file.
        3. dict: Turbidity location data loaded from the appropriate JSON file based on the location type.

    Example:
    >>> image_handler_list, turbidity_measures_data, turbidity_location_data = load_turbidity_data("estuary_1", "Original")
    """
    estuary_name = estuary_name.lower()
    if atmoshperic_correction == "Sen2Cor":
        image_handler_list = load_pickle_data(f"data/turbidity/{estuary_name}_2023.pkl")
    elif atmoshperic_correction == "Acolite":
        image_handler_list = load_pickle_data(
            f"data/turbidity/acolite/{estuary_name}_2023.pkl"
        )
    turbidity_measures_data = load_json_data(
        f"../data/field_work/json/summer_2023/{estuary_name}_measures.json"
    )
    if modified_turbidity_location == "Original":
        turbidity_location_data = load_json_data(
            f"../data/field_work/json/summer_2023/{estuary_name}_location.json"
        )
    elif modified_turbidity_location == "Modifiée manuellement":
        turbidity_location_data = load_json_data(
            f"../data/field_work/json/summer_2023/modified_location/{estuary_name}_location.json"
        )
    return image_handler_list, turbidity_measures_data, turbidity_location_data


def load_and_clean_turbidity_fixed_data(csv_path: str, year) -> pandas.DataFrame:
    """
    Load csv data with ";" delimeter. Rename coloumns with lower caracters.
    Date is also converted
    """
    data = pandas.read_csv(csv_path)
    data.columns = [col.lower() for col in data.columns]
    if year == "2023":
        data["date"] = data["date and time"].apply(convert_string_date_to_datetime_2023)
    if year == "2022":
        data["date"] = data["date"].apply(convert_string_date_to_datetime_2022)
    return data


def load_turbidity_fixed_data(estuary_name, atmoshperic_correction, years):
    """
    Load turbidity fixed data for a specific estuary.

    Parameters:
    - estuary_name (str): The name of the estuary. It is case-insensitive.

    Returns:
    tuple: A tuple containing three elements:
        1. list: Image handler list loaded from the pickled data file.
        2. pandas.DataFrane: Turbidity measures data loaded from the csv file.
        3. dict: Turbidity location data loaded from the appropriate JSON file.

    Example:
    >>> image_handler_list, turbidity_measures_data, turbidity_location_data = load_turbidity_fixed_data("estuary_1")
    """
    atmoshperic_correction = atmoshperic_correction.lower()
    years_list = years.split("/")
    estuary_name = estuary_name.lower()
    image_handler_list = []
    fixed_turbidity_data_list = []
    turbidity_geo_coordinate_dict = {}
    for year in years_list:
        image_handler_list.extend(
            load_pickle_data(
                f"data/turbidity_fixed/{year}/{atmoshperic_correction}/{estuary_name}.pkl"
            )
        )
        fixed_turbidity_data_list.append(
            load_and_clean_turbidity_fixed_data(
                f"../data/{year}_data/outlier_removal/{estuary_name}.csv", year
            )
        )
        turbidity_geo_coordinate_dict[year] = get_turbidity_geo_coordinates_from_path(
            f"../data/field_work/json/probe/{estuary_name}_{year}.json"
        )

    fixed_turbidity_data = pandas.concat(fixed_turbidity_data_list).reset_index(
        drop=True
    )
    return image_handler_list, fixed_turbidity_data, turbidity_geo_coordinate_dict
