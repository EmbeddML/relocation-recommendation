import streamlit as st

from typing import Tuple
from geopy import Nominatim
from src.settings import PROCESSED_DATA_DIR
import pandas as pd
import os
import geopandas as gpd
from sklearn.metrics import pairwise_distances

geolocator = Nominatim(user_agent='region_recommendation')

path_to_embeddings = PROCESSED_DATA_DIR.joinpath("aggregate_embeddings.pkl.gz")
embeddings = pd.read_pickle(path_to_embeddings)


def get_filtered_df(df, min, max, column_name, filter_out_empty=True):
    filtered_df = df[df[column_name] >= min]
    filtered_df = filtered_df[filtered_df[column_name] <= max]
    return filtered_df


def add_similaries_to_df(df, hex_id, modalities):
    cols = [col for t in modalities for col in embeddings.columns if col.startswith(t)]
    filtered_embeddings = embeddings[cols]
    sims = pd.DataFrame(data={"hex_id":filtered_embeddings.index,
                             "similarity":pairwise_distances(filtered_embeddings.loc[[hex_id]], filtered_embeddings, metric='euclidean')[0]})
    sims.set_index("hex_id",inplace=True)
    df.set_index("hex_id",inplace=True)
    stats_with_sims = df.join(sims, how='left')
    stats_with_sims['similarity'] = 1 - stats_with_sims['similarity'] / max(stats_with_sims['similarity'])
    stats_with_sims = stats_with_sims.dropna()
    return stats_with_sims


@st.cache()
def get_geodataframe_for_city(city_name: str):
    if os.path.exists(os.path.join("data", "processed", f"{city_name}_grouped.pkl.gz")):
        gdf_grouped = pd.read_pickle(os.path.join("data", "processed", f"{city_name}_grouped.pkl.gz"))
        return gdf_grouped
    else:
        st.error(f"Not implemented yet for {city_name}")
        return None

def get_nonzero_features(h3_id: str, feature: str):
    if feature == "transport":
        df = pd.read_pickle(os.path.join("data", "processed", "transport.pkl.gz"))
        df = df.loc[h3_id]
        df_directions = df[df.index.str.startswith("directions")]
        df_trips = df[df.index.str.startswith("trips")]
        return df_directions, df_trips
    elif feature == "functional":
        df = pd.read_pickle(os.path.join("data", "processed", "functional.pkl.gz"))
        df = df.loc[h3_id]
        df = df[df != 0].sort_values(ascending=False)
        return df
    elif feature == "roads":
        df = pd.read_pickle(os.path.join("data", "processed", "road.pkl.gz"))
        df = df.loc[h3_id]
        df = df[df != 0].sort_values(ascending=False)
        return df


def get_lat_and_lon_by_name(name: str) -> Tuple[float, float]:
    location = geolocator.geocode(name)
    lat = float(location.raw['lat'])
    lon = float(location.raw['lon'])
    return lat, lon
