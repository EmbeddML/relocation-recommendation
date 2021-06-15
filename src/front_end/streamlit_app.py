import json
import os
from copy import deepcopy
from typing import List, Tuple

import geopandas as gpd
import h3
import pandas as pd
import pydeck as pdk
import streamlit as st
from src.front_end.components.map_component import map_component
from geopy import Nominatim
from shapely.geometry import Polygon
from SessionState import get_state

state = get_state()

st.set_page_config(page_title="Region recommendation system", layout="wide")

geolocator = Nominatim(user_agent='region_recommendation')

selectbox_options = {
    "price": "Mean price of offers",
    "price_per_m": "Mean price per m2 of offers",
    "area": "Mean area of offers",
    "count": "Number of offers"
}


def get_lat_and_lon_by_name(name: str) -> Tuple[float, float]:
    location = geolocator.geocode(name)
    lat = float(location.raw['lat'])
    lon = float(location.raw['lon'])
    return lat, lon


def get_hex_from_city_geojson(
        city: dict,
        resolution: int = 8
) -> Tuple[gpd.GeoDataFrame, List[str]]:
    """Fills city poolygon with hexagons at a given resolution.

    Args:
        city (dict): Geojson formatted city polygon
        resolution (int, optional): Uber H3 resolution. Defaults to 8.

    Returns:
        Tuple[gpd.GeoDataFrame, List[str]]: geodataframe with hexagons
        in city and list of hexagons ids.

    """
    city = deepcopy(city)
    city['geometry']['coordinates'][0] = [
        [x[1], x[0]] for x in city['geometry']['coordinates'][0]
    ]
    hexagons = h3.polyfill(city['geometry'], resolution)

    df = pd.DataFrame(hexagons, columns=['hex_id'])

    df['geometry_dict'] = df['hex_id'].apply(
        lambda x: {
            "type": "Polygon",
            "coordinates": [h3.h3_to_geo_boundary(h=x, geo_json=True)]
        })

    df['geometry'] = df['hex_id'].apply(
        lambda x: Polygon(h3.h3_to_geo_boundary(h=x, geo_json=True)))

    gdf = gpd.GeoDataFrame(df)

    return gdf, hexagons


@st.cache()
def get_geodataframe_for_city(city_name: str):
    if "Wrocław" in city_name:
        with open(os.path.join("data", 'wroclaw.geojson')) as f:
            wroclaw_geojson = json.load(f)

        wro_df, hex_wro = get_hex_from_city_geojson(wroclaw_geojson, resolution=8)
        wro_df = wro_df.set_crs(epsg=4326)
        wro_df = wro_df.set_index('hex_id')

        otodom = gpd.read_file("data/raw/OtodomPrices.geojson")
        gdf = gpd.sjoin(wro_df, otodom, op="intersects", how="inner").drop(columns=["index_right"]).rename(
            columns={"id": "count"})

        agg_function_columns = {"count": "count", "price": "mean", "price_per_m": "mean", "area": "mean"}
        stats_df = gdf.groupby(by="hex_id").agg(func=agg_function_columns)

        gdf_grouped = stats_df.join(wro_df, how="right").fillna(0)
        gdf_grouped = gpd.GeoDataFrame(gdf_grouped).set_crs(epsg=4326)
        return gdf_grouped
    else:
        st.error("Not implemented yet for other cities")
        return None


def get_filtered_df(df, min, max, column_name, filter_out_empty=True):
    filtered_df = df[df[column_name] >= min]
    filtered_df = filtered_df[filtered_df[column_name] <= max]
    return filtered_df


st.title("Recommendation system for regions in a city")
source_col, dest_col = st.beta_columns(2)

with source_col:
    st.title("Pick a source region from the map")

    source_city = st.text_input("Enter a name of source city:", value="Wrocław")

    source_option = st.selectbox("Choose by which feature to filter regions in source city", list(selectbox_options.items()), 0,
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
        opacity=0.2,
        get_fill_color=[174, 213, 129],
        get_line_color=[0, 0, 0],
        auto_highlight=True,
        line_width_min_pixels=2,
        pickable=True
    )

    view_state = pdk.ViewState(
        longitude=source_lon,
        latitude=source_lat,
        zoom=11)

    source_hex_id = map_component(initialViewState=view_state, layers=[source_layer], key="source_map")
    state.source_hex_id = source_hex_id
    st.write(state.source_hex_id)
    st.write(state.target_hex_id)



with dest_col:
    st.title("Similar regions in target city")
    target_city = st.text_input("Enter a name of target city:", value="Wrocław")

    target_option = st.selectbox("Choose by which feature to filter regions in target city", list(selectbox_options.items()), 0,
                                 format_func=lambda o: o[1])

    target_city_df = get_geodataframe_for_city(target_city).reset_index()
    target_lat, target_lon = get_lat_and_lon_by_name(target_city)

    target_column = target_city_df[target_option[0]]
    target_min_column = round(min(target_column))
    target_max_column = round(max(target_column))

    target_min, target_max = st.slider(f"Filter regions in target city by minimal and maximal {target_option[1]}",
                                       value=[target_min_column, target_max_column])

    target_layer = pdk.Layer(
        "GeoJsonLayer",
        data=get_filtered_df(target_city_df, target_min, target_max, target_option[0]),
        opacity=0.2,
        get_fill_color=[174, 213, 129],
        get_line_color=[0, 0, 0],
        auto_highlight=True,
        line_width_min_pixels=2,
        pickable=True
    )

    view_state = pdk.ViewState(
        longitude=target_lon,
        latitude=target_lat,
        zoom=11)

    target_hex_id = map_component(initialViewState=view_state, layers=[target_layer], key="target_map")
    state.target_hex_id = target_hex_id
    st.write(state.source_hex_id)
    st.write(state.target_hex_id)


    state.sync()