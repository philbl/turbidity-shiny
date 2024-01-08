from satellite_image_handler.utils.normalize_index import create_ndti_raster


def create_turbidity_index_raster(
    red_band, green_band, nir_band, type_of_turbidity_index
):
    if type_of_turbidity_index == "NDTI":
        return create_ndti_raster(red_band, green_band)
    elif type_of_turbidity_index == "Bande Rouge (665nm)":
        return create_red_band_turbidity_raster(red_band)
    elif type_of_turbidity_index == "Bande Infra Rouge (833nm)":
        return create_nir_band_turbidity_raster(nir_band)


def create_red_band_turbidity_raster(red_band):
    """
    Calculates the Turbidity Index  raster from the input red bands.

    Args:
        red_band (numpy.ndarray): Array representing the red band.

    Returns:
        numpy.ndarray: Array representing the turbidity raster.

    Raises:
        ValueError: If the input bands have different shapes.

    Notes:
        - The input bands are expected to be in the same spatial extent and coordinate system.
        - The input bands should be provided as numpy arrays.
        - The turbidity index is calculated using the formula: red_band
        - Higher turbidity values indicate higher turbidity or presence of suspended particles.
    """
    return red_band.astype(float)


def create_nir_band_turbidity_raster(nir_band):
    """
    Calculates the Turbidity Index  raster from the input nir bands.

    Args:
        nir_band (numpy.ndarray): Array representing the nir band.

    Returns:
        numpy.ndarray: Array representing the turbidity raster.

    Raises:
        ValueError: If the input bands have different shapes.

    Notes:
        - The input bands are expected to be in the same spatial extent and coordinate system.
        - The input bands should be provided as numpy arrays.
        - The turbidity index is calculated using the formula: nir_band
        - Higher turbidity values indicate higher turbidity or presence of suspended particles.
    """
    return nir_band.astype(float)
