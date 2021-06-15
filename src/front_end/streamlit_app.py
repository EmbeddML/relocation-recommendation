import pydeck as pdk
import streamlit as st
from src.front_end.components.map_component import map_component
from geopy import Nominatim
from shapely.geometry import Polygon
from SessionState import get_state

state = get_state()

from front_end.processing import get_geodataframe_for_city, get_lat_and_lon_by_name, get_filtered_df, \
    add_similaries_to_df
from front_end.streamlit_helpers import cities_selectbox_options, selectbox_options, OPACITY, LINE_COLOR, LINE_WIDTH, \
    VIEW_STATE_ZOOM, radio_buttons_options

st.set_page_config(page_title="Region recommendation system", layout="wide")
st.title("Recommendation system for regions in a city")
st.sidebar.title("How the similarity is to be calculated?")
chosen_modalities = \
st.sidebar.radio("", radio_buttons_options, 0, format_func=lambda o: o[1])[0]
source_col, dest_col = st.beta_columns(2)

with source_col:
    st.title("Pick a source region from the map")

    source_city = \
        st.selectbox("Choose a source city", list(cities_selectbox_options.items()), 0, format_func=lambda o: o[1])[0]
    source_option = st.selectbox("Choose by which feature to filter regions in source city",
                                 list(selectbox_options.items()), 0,
                                 format_func=lambda o: o[1])

    source_city_df = get_geodataframe_for_city(source_city).reset_index()
    source_lat, source_lon = get_lat_and_lon_by_name(source_city)

    source_column = source_city_df[source_option[0]]
    source_min_column = round(min(source_column))
    source_max_column = round(max(source_column))

    source_min, source_max = st.slider(f"Filter regions in source city by minimal and maximal {source_option[1]}",
                                       value=[source_min_column, source_max_column])

    source_layer = pdk.Layer(
        "GeoJsonLayer",
        data=get_filtered_df(source_city_df, source_min, source_max, source_option[0]),
        opacity=OPACITY,
        get_fill_color=[174, 213, 129],
        get_line_color=LINE_COLOR,
        line_width_min_pixels=LINE_WIDTH,
        pickable=True,
        auto_highlight=True
    )

    view_state = pdk.ViewState(
        longitude=source_lon,
        latitude=source_lat,
        zoom=VIEW_STATE_ZOOM)

    source_hex_id = map_component(initialViewState=view_state, layers=[source_layer], key="source_map")
    state.source_hex_id = source_hex_id

    # source_deck = pdk.Deck(
    #     map_style=MAP_STYLE,
    #     tooltip={
    #         "text": "Average price: {price}\nAverage price per m2: {price_per_m}\nAverage area: {area}\nNumber of offers: {count}"})

with dest_col:
    st.title("Similar regions in target city")
    target_city = \
        st.selectbox("Choose a target city", list(cities_selectbox_options.items()), 0, format_func=lambda o: o[1])[0]

    target_option = st.selectbox("Choose by which feature to filter regions in target city", list(selectbox_options.items()), 0,
                                 format_func=lambda o: o[1])

    target_city_df = get_geodataframe_for_city(target_city).reset_index()
    target_lat, target_lon = get_lat_and_lon_by_name(target_city)

    target_column = target_city_df[target_option[0]]
    target_min_column = round(min(target_column))
    target_max_column = round(max(target_column))

    target_min, target_max = st.slider(f"Filter regions in target city by minimal and maximal {target_option[1]}",
                                       value=[target_min_column, target_max_column])

    target_df = get_filtered_df(target_city_df, target_min, target_max, target_option[0])
    if state.source_hex_id is None or state.source_hex_id == "":
        target_layer = pdk.Layer(
            "GeoJsonLayer",
            data=target_df,
            opacity=OPACITY,
            get_fill_color=[154, 3, 3],
            get_line_color=LINE_COLOR,
            line_width_min_pixels=LINE_WIDTH,
            pickable=True,
            auto_highlight=True
        )
    else:
        target_df = add_similaries_to_df(target_df, state.source_hex_id, chosen_modalities)
        target_layer = pdk.Layer(
            "GeoJsonLayer",
            data=target_df,
            opacity=OPACITY,
            get_fill_color='[similarity*252, 3, 3]',
            get_line_color=LINE_COLOR,
            line_width_min_pixels=LINE_WIDTH,
            pickable=True,
            auto_highlight=True
        )
    view_state = pdk.ViewState(
        longitude=target_lon,
        latitude=target_lat,
        zoom=VIEW_STATE_ZOOM)

    target_hex_id = map_component(initialViewState=view_state, layers=[target_layer], key="target_map")
    state.target_hex_id = target_hex_id
    # target_deck = pdk.Deck(
    #     map_style=MAP_STYLE,
    #     layers=[target_layer], initial_view_state=view_state,
    #     tooltip={
    #         "text": "Average price: {price}\nAverage price per m2: {price_per_m}\nAverage area: {area}\nNumber of offers: {count}\n Similarity: {similarity}\n H3 ID: {h3}"})


state.sync()