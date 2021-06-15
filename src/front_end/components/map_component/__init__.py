import os
import streamlit.components.v1 as components
import pydeck as pdk
from typing import List

_RELEASE = True
_COMPONENT_NAME = "map_component"

if not _RELEASE:
    _component_func = components.declare_component(
        _COMPONENT_NAME,
        url="http://localhost:3001",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component(_COMPONENT_NAME, path=build_dir)


def _convert_layer(layer: pdk.Layer) -> dict:
    layer_dict = layer.__dict__
    layer_dict["data"] = layer_dict["_data"]
    layer_dict["getFillColor"] = layer_dict["get_fill_color"]
    layer_dict["getLineColor"] = layer_dict["get_line_color"]
    layer_dict["lineWidthMinPixels"] = layer_dict["line_width_min_pixels"]
    layer_dict["autoHighlight"] = layer_dict["auto_highlight"]
    return layer_dict

def map_component(initialViewState: pdk.ViewState, layers: List[pdk.Layer], key=None):
    layers_dict = list(map(lambda layer: _convert_layer(layer), layers))
    component_value = _component_func(initialViewState=initialViewState.__dict__, layers=layers_dict, key=key, default=None)
    return component_value
