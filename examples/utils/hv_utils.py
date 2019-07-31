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

import pdb

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


################################################################################
## Conversion helpers
################################################################################
def ranges2lbrt(x_range, y_range):
    """
    Convert x_range and y_range to a tuple of 4 floats indicating
    l,b,r,t 
    Args:
    - x_range, y_range (tuple)
    Returns
    - lbrt (tuple of 4 floats)
    """
    minx, maxx = x_range
    miny, maxy = y_range
    return (minx, miny, maxx, maxy)

def lbrt2ranges(lbrt):
    """
    Converts a tuple of 4 floats indicating l,b,r,t coordinate
    to x_range and y_range
    """
    minx, miny, maxx, maxy = lbrt
    return ( (minx, maxx), (miny, maxy) )


################################################################################
## Statistics helpers
################################################################################
def extract_item(xarr):
    """Extract item from a zero-dimensional xarray"""
    if xarr.ndim != 0: 
        raise ValueError(f'Input array must be zero-dim: {xarr.ndim}')
    return xarr.values.item()


def get_stats(arr, show_as_timestamp, decimals=3):
    """
    Computes statistics of a 1Dim xr.array type data
    Args:
    - arr (np.array or xarray.DataArray in dask)
    - show_as_timestamp (bool): 
        If True, return the argmin and argmax as datetime64 
        If False, return as index to arr's coordinate
    - decimals (int): number of decimal places to round to
    
    Returns:
    - stats: a dictionary with the following keys:
        - mean, std, min, argmin, max, argmax,

    """
    if isinstance(arr, (xr.DataArray, xr.Dataset)):
        arr.load()
        
    if arr.ndim != 1:
        raise ValueError(f'Input array must be 1-dim: {arr.ndim}')
        
    for i,val in enumerate(arr):
        if np.isnan(val):
            arr[i] = 0.0
            
    from collections import OrderedDict 
    def to_float(x):
        return np.around(extract_item(x), decimals=decimals)
    

    vals = list(map(to_float, 
                    [arr.mean(), arr.std(), arr.min(), 
                     arr.argmin(), arr.max(), arr.argmax()]))
    
    stats = OrderedDict(
        {'mean': vals[0],
        'std':vals[1],
        'min': vals[2],
        'argmin': vals[3],# time index, not datetime obj
        'max': vals[4],
        'argmax': vals[5],
        })
    if show_as_timestamp:
        min_idx = stats['argmin']
        max_idx = stats['argmax']
        stats.update(argmin=arr.get_index('time')[min_idx],
                     argmax=arr.get_index('time')[max_idx]
                    )
#     print(type(stats['argmin']))
#     pdb.set_trace()

    df = pd.DataFrame.from_records([stats], columns=stats.keys())
#     pdb.set_trace()
    return df
        
def get_img(xrd, varname, t, crs=ccrs.PlateCarree()):
    """
    Returns a hv.Image of xarray dataset's variable named `varname` at `tidx`th time
    Args:
    - xrd (xarray dataset)
    - varname (str)
    - t (int or dt.datetime64)
    Returns:
    - img (hv.Image)
    """
    if isinstance(t, int):
        return gv.Image(xrd[varname].isel(time=t), ['X','Y'], varname, crs=crs)
    else: #todo: better way to check if xarray's acceptable time indexing type
        return gv.Image(xrd[varname].sel(time=t), ['X','Y'], varname, crs=crs)

def append_to_div(hvDiv, new_str):
    """Modifies the hvDiv element inplace
    by adding a new paragraph that contains the input `new_str`
    Args:
    - hvDiv (hv.Div)
    - new_str (str)
    
    Modifies the hvDiv inplace, returns None
    """
    new_str = f'<p>{new_str}</p>'
    hvDiv.data += new_str
    
################################################################################
## Debug helpers
################################################################################    
def get_debug_div(*args, **kwargs):
    print('get_debug_div called')
#     import inspect
#     pdb.set_trace()
    content = f'<p> args: {str(args)} </p>'
    content += """
    <p> kwargs:  </p>
    <ul>
    """
    for k,v in kwargs.items():
        content += f'<li>{k}: {v}</li>'
    content += '</ul>'
    return hv.Div(content)

    
################################################################################
## Tests
################################################################################
def test_ranges2lbrt():
    x_range = (-1,1); y_range=(-10,10)
    lbtc = ranges2lbrt(x_range, y_range)
    assert lbtc == (-1,-10,1,10)
def test_lbrt2ranges():
    lbrt = (-1,-10,1,10)
    assert lbrt2ranges(lbrt) == ((-1, 1), (-10, 10))
def test_get_img():
    pass
    # get_img(xrd_ea, varname, 0)
def test_append_to_div():
    div = hv.Div("""
        <h1 style='color:blue;border:1px solid blue'>Debug Box</h1>
        <p></p>
        """)
    print('Original div')
    display(div)
    append_to_div(div, 'new paragraph')
    print('After adding a new str')
    display(div)
    
    