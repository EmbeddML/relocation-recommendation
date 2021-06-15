import pydeck as pdk

selectbox_options = {
    "price": "Mean price of offers",
    "price_per_m": "Mean price per m2 of offers",
    "area": "Mean area of offers",
    "count": "Number of offers"
}

cities_selectbox_options = {
    "wroclaw": "Wrocław",
    "gdansk": "Gdańsk",
    "warszawa": "Warszawa",
    "krakow": "Kraków",
    "poznan": "Poznań"
}

radio_buttons_options = [
    (("x", "y", "z"), "Road Network + GTFS data + Functional data"),
    (("y", "z"), "Functional data + GTFS data"),
    (("x", "z"), "GTFS data + Road Network"),
    (("x", "y"), "Functional data + Road Network"),
    (("x",), "Only Road Network"),
    (("y",), "Only GTFS data"),
    (("z",), "Only Functional data")
]

VIEW_STATE_ZOOM = 11
LINE_WIDTH = 0.3
LINE_COLOR = [0, 0, 0]
OPACITY = 0.5
MAP_STYLE = pdk.map_styles.MAPBOX_ROAD
