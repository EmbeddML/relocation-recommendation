from typing import Dict, Union
from keplergl import KeplerGl
from pathlib import Path
import pickle as pkl
import json
from src.settings import KEPLER_CONFIG_DIR
from pathlib import Path
from geopandas.geodataframe import GeoDataFrame
from ipywidgets.widgets import widget
from keplergl import KeplerGl
import pandas as pd
import geopandas as gpd
from typing import Union
from .config import load_config
import contextily as ctx
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram
import numpy as np
from src.data.make_dataset import h3_to_polygon
from src.settings import FIGURES_DIR
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from src.data.download import ensure_geometry_type
 
def save_config(kepler: KeplerGl, config_name: str) -> Path:
    path = KEPLER_CONFIG_DIR.joinpath(f"{config_name}.json")
    with open(path, "wt") as f:
        json.dump(kepler.config, f)
    return path
 
def load_config(config_name: str) -> Union[Dict, None]:
    try:
        with open(KEPLER_CONFIG_DIR.joinpath(f"{config_name}.json"), "rt") as f:
            return json.load(f)
    except FileNotFoundError:
        return None
 
def save_kepler_map(kepler_map: KeplerGl, figure_subpath: Path, remove_html=False):
    result_path = FIGURES_DIR.joinpath(figure_subpath)
    result_path.parent.mkdir(parents=True, exist_ok=True)
    html_file = result_path.with_suffix(".html")
    
    for gdf in kepler_map.data.values():
        ensure_geometry_type(gdf)
    kepler_map.save_to_html(file_name=html_file)
 
    options = Options()
    height = kepler_map.height
    width = 1300
    options.add_argument("--headless")
    options.add_argument(f"--window-size={width},{height}")
 
    driver = webdriver.Chrome(options=options)
    driver.get(str(html_file.resolve()))
    time.sleep(3)
    driver.save_screenshot(str(result_path))
    if remove_html:
        html_file.unlink()
 
def visualize_kepler(data: Union[pd.DataFrame, gpd.GeoDataFrame], name="data", config_name: str=None) -> KeplerGl:
    if config_name is not None:
        config = load_config(config_name)
        if config is not None:
            return KeplerGl(data={name: data}, config=config, height=900)
    return KeplerGl(data={name: data})