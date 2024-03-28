from shiny import ui, App, Session
import matplotlib

from ui_turbidity import ui_turbidity
from ui_water import ui_water
from ui_spatial_turbidity import ui_spatial_turbidity
from ui_satellite_situ import ui_satellite_situ
from ui_turbidity_fixed import ui_turbidity_fixed
from ui_satellite_fixed import ui_satellite_fixed
from server_water import server_water
from server_turbidity import server_turbidity
from server_spatial_turbidity import server_spatial_turbidity
from server_satellite_situ import server_satellite_situ
from server_turbidity_fixed import server_turbidity_fixed
from server_satellite_fixed import server_satellite_fixed


matplotlib.use("agg")


ui_info = ui.page_fluid(ui.output_text_verbatim("general_informations"))

app_ui = ui.page_fluid(
    ui.h1("Exploration: Images Satellite et Turbidité"),
    ui.navset_pill_card(
        ui.nav("Information", ui_info),
        ui.nav("Détection de l'eau", ui_water),
        ui.nav("Turbidité", ui_turbidity),
        ui.nav("Turbidité Spatiale", ui_spatial_turbidity),
        ui.nav("Relation Satellite/In-Situ Spatiale", ui_satellite_situ),
        ui.nav("Turbidité Fixe", ui_turbidity_fixed),
        ui.nav("Relation Satellite/In-Situ Fixe", ui_satellite_fixed),
        selected="Turbidité",
    ),
)


def server(input, output, session: Session):
    server_water(input, output, session)
    server_turbidity(input, output, session)
    server_spatial_turbidity(input, output, session)
    server_satellite_situ(input, output, session)
    server_turbidity_fixed(input, output, session)
    server_satellite_fixed(input, output, session)


# This is a shiny.App object. It must be named `app`.
app = App(app_ui, server)
