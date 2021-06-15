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

VIEW_STATE_ZOOM = 10
LINE_WIDTH = 0.3
LINE_COLOR = [0, 0, 0]
OPACITY = 0.5

color_mapping = {
    "aeroway": "#F280BF",
    "amenity": "#FF8000",
    "building": "#908b86",
    "healthcare": "#CC0000",
    "historic": "#A6A64D",
    "landuse": "#808000",
    "leisure": "#80E600",
    "military": "#4B5320",
    "natural": "#33CC33",
    "office": "#b3aca7",
    "shop": "#804DFF",
    "sport": "#D94D4D",
    "tourism": "#E6BF80",
    "water": "#0080FF",
    "waterway": "#80BFFF"
}

