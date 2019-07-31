import os, sys, time
import numpy as np
import scipy as sp
import pandas as pd
import geopandas as gpd
    
from pathlib import Path
from pprint import pprint

import holoviews as hv
import xarray as xr

from holoviews import opts
from holoviews.operation.datashader import datashade, shade, dynspread, rasterize
from holoviews.streams import Stream, param
from holoviews import streams

import geoviews as gv
import geoviews.feature as gf
from geoviews import tile_sources as gvts

import cartopy.crs as ccrs
import cartopy.feature as cf


def get_element_plot_mapping(backend='bokeh'):
    """
    shows the mapping of holoviews element and plot 
    for the backend
    - backend (str): eg: 'bokeh','matplotlib'
    """
    pd.set_option('max_colwidth', 100)
    regi = hv.Store.registry[backend]
    df = pd.DataFrame({
            'element': list(map(str, regi.keys())),
            'plot': list(map(str, regi.values()))})
    return hv.Table(df).opts(width=700)

def relabel_elements(ndoverlay, labels):
    """
    ndOverlay is indexed by integer
    labels (str or iterable of strs)
    length of hv elements in the overlay must equal to the length of labels
    """
    import holoviews as hv
    from itertools import cycle
    if isinstance(labels, str):
        labels = [labels]
    if isinstance(labels, list) and len(labels) != len(ndoverlay):
        raise ValueError('Length of the labels and ndoverlay must be the same')
        
        
    it = cycle(labels) 
    relabeled = hv.NdOverlay({i: ndoverlay[i].relabel(next(it)) for i in range(len(ndoverlay))})
    return relabeled