import pydeck as pdk
import streamlit as st

import plotly.express as px
from src.front_end.components.map_component import map_component
from geopy import Nominatim
from shapely.geometry import Polygon
from front_end.processing import get_geodataframe_for_city, get_lat_and_lon_by_name, get_filtered_df, \
    add_similaries_to_df, get_nonzero_features
from front_end.streamlit_helpers import cities_selectbox_options, selectbox_options, OPACITY, LINE_COLOR, LINE_WIDTH, \
    VIEW_STATE_ZOOM, MAP_STYLE, radio_buttons_options
import numpy as np
from SessionState import get_state
from src.front_end.streamlit_helpers import color_mapping


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

    

state = get_state()

st.set_page_config(page_title="Region recommendation system", layout="wide")
st.title("Recommendation system for regions in a city")
st.sidebar.title("How the similarity is to be calculated?")
chosen_modalities = st.sidebar.radio("", radio_buttons_options, 0, format_func=lambda o: o[1])[0]

source_col, dest_col = st.beta_columns(2)


with source_col:
    st.title("Pick a source region from the map")

    source_city = st.selectbox("Choose a source city", list(cities_selectbox_options.items()), 0, format_func=lambda o: o[1])[0]
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
        target_df = add_similaries_to_df(target_df, state.source_hex_id, chosen_modalities).reset_index()
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


if state.source_hex_id is not None and state.source_hex_id != "":
    with st.beta_expander("Transport features"):
        source_transport_col, dest_transport_col = st.beta_columns(2)
    
        with source_transport_col:
            directions, trips = get_nonzero_features(state.source_hex_id, "transport")
            directions_chart = show_features(directions, title="Source region directions")
            trips_chart = show_features(trips, title="Source region trips")
            st.plotly_chart(directions_chart, width=0, height=0, use_container_width=True)
            st.plotly_chart(trips_chart, width=0, height=0, use_container_width=True)

        with dest_transport_col:
            if state.target_hex_id is not None and state.target_hex_id != "":
                directions, trips = get_nonzero_features(state.target_hex_id, "transport")
                directions_chart = show_features(directions, title="Target region directions")
                trips_chart = show_features(trips, title="Target region trips")
                st.plotly_chart(directions_chart, width=0, height=0, use_container_width=True)
                st.plotly_chart(trips_chart, width=0, height=0, use_container_width=True)

    with st.beta_expander("Functional features"):
        source_functional_col, dest_functional_col = st.beta_columns(2)
    
        with source_functional_col:
            df_functional = get_nonzero_features(state.source_hex_id, "functional")
            if not df_functional.empty:
                functional_chart = show_features(df_functional, title="Source region functional info", log_y=True, color=True)
                st.plotly_chart(functional_chart, width=0, height=0, use_container_width=True)

        with dest_functional_col:
            if state.target_hex_id is not None and state.target_hex_id != "":
                df_functional = get_nonzero_features(state.target_hex_id, "functional")
                if not df_functional.empty:
                    functional_chart = show_features(df_functional, title="Target region functional info", log_y=True, color=True)
                    st.plotly_chart(functional_chart, width=0, height=0, use_container_width=True)


    with st.beta_expander("Road features"):
        source_road_col, dest_road_col = st.beta_columns(2)
    
        with source_road_col:
            df_roads = get_nonzero_features(state.source_hex_id, "roads")
            if not df_roads.empty:
                roads_chart = show_features(df_roads, title="Source region roads")
                st.plotly_chart(roads_chart, width=0, height=0, use_container_width=True)

        with dest_road_col:
            if state.target_hex_id is not None and state.target_hex_id != "":
                df_roads = get_nonzero_features(state.target_hex_id, "roads")
                if not df_roads.empty:
                    roads_chart = show_features(df_roads, title="Target region roads")
                    st.plotly_chart(roads_chart, width=0, height=0, use_container_width=True)

state.sync()