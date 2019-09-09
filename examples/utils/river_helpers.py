import os, sys, re
from pathlib import Path
import numpy as np, pandas as pd

import pdb
from inspect import getmro
from typing import Union, Iterable, Collection

from shapely.geometry import Polygon, Point

# if sys.version_info <= (3,5):
try:
    import geopandas as gpd
    import apls_tools # dependent on geopandas inside itself
except ImportError: # will be 3.x series
    pass

###############################################################################
### Add this file's path ###
###############################################################################
file_dir =  os.path.dirname(os.path.realpath(__file__))
# file_dir =  os.path.dirname(os.path.realpath('.'))
print("Importing: ", file_dir)

if file_dir not in sys.path:
    sys.path.insert(0, file_dir)
    print(f"Added {str(file_dir)} to sys.path")

SP_UTILS = Path.home()/'Playground/Spacenet_Preprocess/scripts'
assert SP_UTILS.exists()
if str(SP_UTILS) not in sys.path:
    sys.path.insert(0, str(SP_UTILS))
    print(f"Added {SP_UTILS} to sys.path")
    
###############################################################################
### Import my modules ###
###############################################################################
from output_helpers import nprint
from geo_helpers import bounds2poly, crop_gdf_to_bounds, get_polys_at_lonlat


###############################################################################
### Helpers ###
###############################################################################
def load_river_csvs(csv_dir):
    """
    Given a directory containing csv files with the same header,
    returns a pd.DataFrame of concatenated csvs with a single header
    """
    if isinstance(csv_dir, str):
        csv_dir = Path(csv_dir).absolute()
    fns = [p for p in csv_dir.iterdir() if p.suffix == '.csv']
    dfs = []
    for fn in fns:
        dfs.append(pd.read_csv(fn))
    data = pd.concat(dfs)
    data.reset_index(inplace=True)
    data.drop('index', axis=1, inplace=True)
    data['Time'] = data.Time.astype('datetime64[ns]')
    return data
    
    
def select_gdf_at_lonlat(gdf, lon, lat):
    """
    Returns a new GeoDataFrame that intersects with the point at lon, lat
    """
    p = Point(lon,lat)
    gdf_selected =  gdf[gdf.intersects(p)]
    return gdf_selected

    

def get_basin_id(basin_data: gpd.GeoDataFrame, 
                 lon: float, 
                 lat: float):
    
    gdf_selected = select_gdf_at_lonlat(basin_data,lon,lat)
    if len(gdf_selected) > 0:
        return gdf_selected['HYBAS_ID'].item()
    else:
        return None
    
def select_gdf_in_basin(gdf: gpd.GeoDataFrame, 
                        basin_data: gpd.GeoDataFrame,
                        basin_id:str, 
                        basin_id_col='HYBAS_ID',
                       verbose=False):
    
    gdf_basin = basin_data[basin_data[basin_id_col] == basin_id]
    bounds = gdf_basin.total_bounds
    gdf_selected = crop_gdf_to_bounds(gdf, bounds, remove_empty=True)
    
    if verbose:
        print(len(gdf_selected), len(gdf_selected.groupby(['Longitude', 'Latitude'])))
        
    return gdf_selected