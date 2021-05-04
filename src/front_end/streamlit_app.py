from typing import Tuple

import streamlit as st

from geopy import Nominatim

import pydeck as pdk

st.set_page_config(page_title="Region recommendation system", layout="wide")

geolocator = Nominatim(user_agent='region_recommendation')


def get_lat_and_lon_by_name(name: str) -> Tuple[float, float]:
    location = geolocator.geocode(name)
    lat = float(location.raw['lat'])
    lon = float(location.raw['lon'])
    return lat, lon




st.title("Recommendation system for regions in a city")

source_col, dest_col = st.beta_columns(2)

with source_col:
    st.title("Pick a source region from the map")

    source_city = st.text_input("Enter a name of source city:", value="Wrocław")

    source_min, source_max = st.slider("Filter regions in source city by minimal and maximal mean price of apartments",
                                       value=[0, 100000])

    source_lat, source_lon = get_lat_and_lon_by_name(source_city)

    view_state = pdk.ViewState(
        longitude=source_lon, latitude=source_lat, zoom=13, min_zoom=5, max_zoom=20, pitch=40.5, bearing=-27.36
    )

    r = pdk.Deck(
        map_style=pdk.map_styles.MAPBOX_LIGHT,
        initial_view_state=view_state,
        tooltip={"html": "<b>Elevation Value:</b> {elevationValue}", "style": {"color": "white"}},
    )
    st.pydeck_chart(r)


with dest_col:
    st.title("Similar regions in target city")
    target_city = st.text_input("Enter a name of target city:", value="Wrocław")

    target_min, target_max = st.slider("Filter regions in target city by minimal and maximal mean price of apartments",
                                       value=[0, 100000])

    target_lat, target_lon = get_lat_and_lon_by_name(target_city)

    view_state = pdk.ViewState(
        longitude=target_lon, latitude=target_lat, zoom=13, min_zoom=5, max_zoom=20, pitch=40.5, bearing=-27.36
    )

    r = pdk.Deck(
        map_style=pdk.map_styles.MAPBOX_LIGHT,
        initial_view_state=view_state,
        tooltip={"html": "<b>Elevation Value:</b> {elevationValue}", "style": {"color": "white"}},
    )
    st.pydeck_chart(r)
