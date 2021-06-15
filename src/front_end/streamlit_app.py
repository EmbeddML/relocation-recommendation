import pydeck as pdk
import streamlit as st
import plotly.express as px
from front_end.processing import get_geodataframe_for_city, get_lat_and_lon_by_name, get_filtered_df, \
    add_similaries_to_df, get_nonzero_features
from front_end.streamlit_helpers import cities_selectbox_options, selectbox_options, OPACITY, LINE_COLOR, LINE_WIDTH, \
    VIEW_STATE_ZOOM, MAP_STYLE
import numpy as np


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


def show_features(data, title, log_y=False, color=False, orientation='v'):
    if color:
        columns = np.array([col.split("_")[0] for col in data.index])
        colors = np.array([color_mapping[col] for col in columns])
        fig = px.bar(data, title=title, color=colors, orientation=orientation, log_y=log_y)
    else:
        fig = px.bar(data, title=title, orientation=orientation)
    fig.update_yaxes(title=None)
    fig.update_xaxes(title=None)
    fig.update_layout(showlegend=False)
    fig.update_xaxes(tickangle=270)
    return fig


st.set_page_config(page_title="Region recommendation system", layout="wide")

st.title("Recommendation system for regions in a city")
selected_hex = st.text_input("Enter hex name:")
source_col, dest_col = st.beta_columns(2)


with source_col:
    st.title("Pick a source region from the map")

    source_city = \
        st.selectbox("Choose a source city", list(cities_selectbox_options.items()), 0, format_func=lambda o: o[1])[0]
    source_option = st.selectbox("Choose by which feature to filter regions in source city",
                                 list(selectbox_options.items()), 0,
                                 format_func=lambda o: o[1])

    source_city_df = get_geodataframe_for_city(source_city)
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

    source_deck = pdk.Deck(
        map_style=MAP_STYLE,
        layers=[source_layer], initial_view_state=view_state,
        tooltip={
            "text": "Average price: {price}\nAverage price per m2: {price_per_m}\nAverage area: {area}\nNumber of offers: {count}"})
    st.pydeck_chart(source_deck)



with dest_col:
    st.title("Similar regions in target city")
    target_city = \
        st.selectbox("Choose a target city", list(cities_selectbox_options.items()), 0, format_func=lambda o: o[1])[0]

    target_option = st.selectbox("Choose by which feature to filter regions in target city",
                                 list(selectbox_options.items()), 0,
                                 format_func=lambda o: o[1])

    target_city_df = get_geodataframe_for_city(target_city)
    target_lat, target_lon = get_lat_and_lon_by_name(target_city)

    target_column = target_city_df[target_option[0]]
    target_min_column = round(min(target_column))
    target_max_column = round(max(target_column))

    target_min, target_max = st.slider(f"Filter regions in target city by minimal and maximal {target_option[1]}",
                                       value=[target_min_column, target_max_column])

    target_df = get_filtered_df(target_city_df, target_min, target_max, target_option[0])
    if selected_hex is None or selected_hex == "":
        target_layer = pdk.Layer(
            "GeoJsonLayer",
            data=target_df,
            opacity=OPACITY,
            get_fill_color=[174, 213, 129],
            get_line_color=LINE_COLOR,
            line_width_min_pixels=LINE_WIDTH,
            pickable=True,
            auto_highlight=True
        )
    else:
        target_df = add_similaries_to_df(target_df, selected_hex)
        target_layer = pdk.Layer(
            "GeoJsonLayer",
            data=target_df,
            opacity=OPACITY,
            get_fill_color='[similarity*255, 0, 0]',
            get_line_color=LINE_COLOR,
            line_width_min_pixels=LINE_WIDTH,
            pickable=True,
            auto_highlight=True
        )

    view_state = pdk.ViewState(
        longitude=target_lon,
        latitude=target_lat,
        zoom=VIEW_STATE_ZOOM)

    target_deck = pdk.Deck(
        map_style=MAP_STYLE,
        layers=[target_layer], initial_view_state=view_state,
        tooltip={
            "text": "Average price: {price}\nAverage price per m2: {price_per_m}\nAverage area: {area}\nNumber of offers: {count}\n Similarity: {similarity}\n H3 ID: {index}"})

    st.pydeck_chart(target_deck)

if selected_hex is not None and selected_hex != "":
    with st.beta_expander("Transport features"):
        source_transport_col, dest_transport_col = st.beta_columns(2)
    
        with source_transport_col:
                directions, trips = get_nonzero_features(selected_hex, "transport")
                directions_chart = show_features(directions, title="Source region directions")
                trips_chart = show_features(trips, title="Source region trips")
                st.plotly_chart(directions_chart, width=0, height=0, use_container_width=True)
                st.plotly_chart(trips_chart, width=0, height=0, use_container_width=True)
        with dest_transport_col:
            #TODO: target region transport features
            pass

    with st.beta_expander("Functional features"):
        source_functional_col, dest_functional_col = st.beta_columns(2)
    
        with source_functional_col:
            df_functional = get_nonzero_features(selected_hex, "functional")
            functional_chart = show_features(df_functional, title="Source region functional info", log_y=True, color=True)
            st.plotly_chart(functional_chart, width=0, height=0, use_container_width=True)
        with dest_functional_col:
            #TODO: target region transport features
            pass

    with st.beta_expander("Road features"):
        source_road_col, dest_road_col = st.beta_columns(2)
    
        with source_road_col:
            df_roads = get_nonzero_features(selected_hex, "roads")
            roads_chart = show_features(df_roads, title="Source region roads")
            st.plotly_chart(roads_chart, width=0, height=0, use_container_width=True)
        with dest_road_col:
            #TODO: target region transport features
            pass