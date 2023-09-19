from shiny import ui

INFORMATION_STRING = (
    ""
    "Visualisation  des images satellites. \n"
    "Il est possible de visualiser la performance de la détection automatique de l'eau. \n"
    "Il sera aussi possible de visualiser la turbidité détecté par imagerie en comparaison avec les données In-Situ. (Travaux en cours)"
)


SCENE_CLF_WATER_MASK_INFO_HTML = ui.HTML(
    "Ce masque est obtenu à l'aide de la classification de scène calculé par le Level2A de traitement de Sentinel2. La résolution est de 20m. <br> <br>"  # noqa E501
    "Un filtre Gaussien est appliqué sur le masque obtenu pour lisser le résultat. <br>"
    "Le Sigma fait référence à l'amplitude des pixels voisins considérés. <br>"
    "Le Threshold sert à décider si un pixel est considéré comme de l'eau. <br> <br>"
    "Une valeur de Sigma plus élevée va donner une frontière plus lisse. <br>"
    "Une valeur plus basse va épouser davantage les formes. <br> <br>"
    "Une valeur de thresholds basse va avoir tendance à avoir plus de faux positif. (De terrain considéré comme de l'eau) <br>"
    "Et une valeur plus élevée va donner plus de faux négatif <br>"
)


NDWI_WATER_MASK_INFO_HTML = ui.HTML(
    "Ce masque est obtenu à l'aide de le l'indice NDWI. (green - NIR) / (NIR + grenn). La résolution est de 10m. <br> <br>"
    "Un premier threshold est appliqué sur l'indice NDWI. Une valeur élevée va donner plus de faux négatif. <br> <br>"
    "Un filtre Gaussien est appliqué sur le masque obtenu pour lisser le résultat. <br>"
    "Le Sigma fait référence à l'amplitude des pixels voisins considérés. <br>"
    "Le Threshold sert à décider si un pixel est considéré comme de l'eau. <br> <br>"
    "Une valeur de Sigma plus élevée va donner une frontière plus lisse. <br>"
    "Une valeur plus basse va épouser davantage les formes. <br> <br>"
    "Une valeur de thresholds basse va avoir tendance à avoir plus de faux positif. (De terrain considéré comme de l'eau) <br>"
    "Et une valeur plus élevée va donner plus de faux négatif <br>"
)
