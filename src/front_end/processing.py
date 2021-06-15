import streamlit as st

from typing import Tuple
from geopy import Nominatim
from settings import PROCESSED_DATA_DIR
import pandas as pd
import os
import geopandas as gpd

geolocator = Nominatim(user_agent='region_recommendation')

path_to_embeddings = PROCESSED_DATA_DIR.joinpath("aggregate_embeddings.pkl.gz")
path_to_embeddings_distances = PROCESSED_DATA_DIR.joinpath("aggregate_embeddings_distances.pkl.gz")
embeddings = pd.read_pickle(path_to_embeddings)
embeddings_distances = pd.read_pickle(path_to_embeddings_distances)


def get_filtered_df(df, min, max, column_name, filter_out_empty=True):
    filtered_df = df[df[column_name] >= min]
    filtered_df = filtered_df[filtered_df[column_name] <= max]
    return filtered_df


def add_similaries_to_df(df, hex_id):
    sims = embeddings_distances.loc[[hex_id]].T
    sims = sims.rename(columns={hex_id: "similarity"}, index={"h3_id": "h3"})
    sims_df = pd.DataFrame(sims['similarity'])
    sims_df.index.names = ['h3']
    stats_with_sims = df.join(sims_df, how='left')
    stats_with_sims['similarity'] = 1 - stats_with_sims['similarity'] / max(stats_with_sims['similarity'])
    stats_with_sims = stats_with_sims.dropna()
    return stats_with_sims


@st.cache()
def get_geodataframe_for_city(city_name: str):
    if os.path.exists(os.path.join("data", "raw", f"{city_name}_otodom_prices.geojson")) and os.path.exists(
            os.path.join("data", "hexes", f"{city_name}_9.geojson")):

        hex_df = gpd.read_file(os.path.join("data", "hexes", f"{city_name}_9.geojson"))
        hex_df.set_crs(epsg=4326)
        hex_df.set_index("h3", inplace=True)

        otodom_prices = gpd.read_file(os.path.join("data", "raw", f"{city_name}_otodom_prices.geojson"))
        otodom_prices.set_crs(epsg=4326)

        gdf = gpd.sjoin(hex_df, otodom_prices, op="intersects", how="inner").drop(columns=["index_right"]).rename(
            columns={"id": "count"})

        agg_function_columns = {"count": "count", "price": "mean", "price_per_m": "mean", "area": "mean"}
        stats_df = gdf.groupby(by="h3").agg(func=agg_function_columns)

        gdf_grouped = stats_df.join(hex_df, how="right", on='h3').fillna(0)
        gdf_grouped = gpd.GeoDataFrame(gdf_grouped).set_crs(epsg=4326)
        gdf_grouped.set_index("h3", inplace=True)
        return gdf_grouped
    else:
        st.error(f"Not implemented yet for {city_name}")
        return None


def get_lat_and_lon_by_name(name: str) -> Tuple[float, float]:
    location = geolocator.geocode(name)
    lat = float(location.raw['lat'])
    lon = float(location.raw['lon'])
    return lat, lon
