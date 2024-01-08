from turbidity_shiny.utils import load_json_data, load_pickle_data


def load_turbidity_data(estuary_name, modified_turbidity_location):
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
    image_handler_list = load_pickle_data(f"data/turbidity/{estuary_name}_2023.pkl")
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
