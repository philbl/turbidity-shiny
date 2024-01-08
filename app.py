from shiny import ui, App, Session
import matplotlib

from ui_turbidity import ui_turbidity
from ui_water import ui_water
from server_water import server_water
from server_turbidity import server_turbidity


matplotlib.use("agg")


ui_info = ui.page_fluid(ui.output_text_verbatim("general_informations"))

app_ui = ui.page_fluid(
    ui.h1("Exploration: Images Satellite et Turbidité"),
    ui.navset_pill_card(
        ui.nav("Information", ui_info),
        ui.nav("Détection de l'eau", ui_water),
        ui.nav("Turbidité", ui_turbidity),
        selected="Turbidité",
    ),
)


def server(input, output, session: Session):
    server_water(input, output, session)
    server_turbidity(input, output, session)


# This is a shiny.App object. It must be named `app`.
app = App(app_ui, server)
