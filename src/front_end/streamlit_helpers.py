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

VIEW_STATE_ZOOM = 11
LINE_WIDTH = 0.3
LINE_COLOR = [0, 0, 0]
OPACITY = 0.5
MAP_STYLE = pdk.map_styles.MAPBOX_ROAD
