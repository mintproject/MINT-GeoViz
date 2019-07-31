################################################################################
## VectorTile class
## autho: hayley song
## Modified: Jun 8, 2019
################################################################################

import math
import requests, json
from pathlib import Path

from itertools import cycle

import pandas as pd
import geopandas as gpd

import holoviews as hv
import geoviews as gv

# from .utils import relabel_elements

class VectorTile():
    """
    Assumes tiles are 256x256 pixel
    Also refer to
    https://svn.openstreetmap.org/applications/routing/pyroute/tilenames.py
    """
    
    SIZE = 256
    LAYER= 'all'
    FFORMAT = 'json'
    CACHE_DIR = '../data/vectile_cache/'
    
    #check if VEC_CACHE object exists in global namespace
    global VECTILE_CACHE
    try:
        VECTILE_CACHE
    except NameError:
        VECTILE_CACHE = {}
    
    @staticmethod
    def deg2xy(lat_deg, lon_deg, zoom):
        """
        Lat,Lon to tile numbers
        - src: https://is.gd/mjvdR7
        """
        lat_rad = math.radians(lat_deg)
        n = 2.0 ** zoom
        xtile = int((lon_deg + 180.0) / 360.0 * n)
        ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
        return (xtile, ytile)

    @staticmethod
    def xyz2deg(xtile, ytile, zoom):
        """
        Tile numbers to lat/lon in degree
        This returns the NW-corner of the square. 
        Use the function with xtile+1 and/or ytile+1 to get the other corners. 
        With xtile+0.5 & ytile+0.5 it will return the center of the tile.
        - src: https://is.gd/mjvdR7
        """
        n = 2.0 ** zoom
        lon_deg = xtile / n * 360.0 - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
        lat_deg = math.degrees(lat_rad)
        return (lat_deg, lon_deg)
    
    def __init__(self, xtile, ytile, z, size=None, layer=None, fformat=None):
        """
        Args:
        - xtile, ytile, z (int)
        - size (int) : currently only supports 256 because of the latlon->tile
            conversion calculation is constrained to that size
        - fformat (str): currently it must be json because I don't know
            how to read mvt or topojson formats to geopandas.DataFrame
        """
        self.xtile = xtile
        self.ytile = ytile
        self.z = z
        self.lat, self.lon = VectorTile.xyz2deg(self.xtile, self.ytile, z)
        self.size = size or VectorTile.SIZE
        self.layer = layer or VectorTile.LAYER
        self.fformat = fformat or VectorTile.FFORMAT
        self.tile_url = f'https://tile.nextzen.org/tilezen/vector/v1/{self.size}/{self.layer}/{self.z}/{self.xtile}/{self.ytile}.{self.fformat}?api_key=GpjLSbvrQsa98MgMMuodzw'
        
    @classmethod
    def from_xyz(cls, xtile, ytile, z):
        return cls(xtile, ytile, z)
    
    @classmethod
    def from_latlon(cls, lat, lon, z):
        xtile, ytile = cls.deg2xy(lat, lon, z)
        return cls(xtile, ytile, z)
    
    def info(self):
        print(f"x, y, z: , {self.xtile}, {self.ytile}, {self.z}")
        print(f"lat, lon: {self.lat}, {self.lon}")
        print(f"size: {self.size}")
        print(f"layer: {self.layer}")
    
    def to_gdf(self):
        """
        Given xtile, ytile and z(oom level), 
        request the vector tile from nextzen vector tile endpoint

        If the tile was requested before and is saved, 
        it will check the current python session's cache, then the local
        disk to read the tile from memory.

        If not cached, it will send a request to the vector tile server,
        save the tile data both in python memory and local disk.

        Returns geopandas.DataFrame that contains some meta data like osm_id 
        and most importantly) geometries

        """
        cache_key = (self.size,self.layer,self.z,self.xtile,self.ytile)
        
        # Check if this tile is in python session memory
        # If so, read from the memory, otherwise read from the disk
        if VECTILE_CACHE.get( cache_key ):
            if VECTILE_CACHE[cache_key].get('loaded'):
                "Reading from python session memory"
                return VECTILE_CACHE[cache_key].get('dframe') #geopandas.gdf
            else:
                "Reading from disk cache"
                return gpd.GeoDataFrame.read_file(VECTILE_CACHE[cache_key].get('fpath'))

        # Request a new tile
        r = requests.get(url=self.tile_url)
        if not r.ok:
            raise ValueError('reponse not ok: ', r.status_code)
        data = r.json()

        # Write to disk
        fdir = (Path(VectorTile.CACHE_DIR) / f'{self.size}/{self.layer}/{self.z}/{self.xtile}/').resolve()
        if not fdir.exists():
            fdir.mkdir(parents=True)
            print(f'{fdir} created')
        fpath = fdir/ f'{self.ytile}.{self.fformat}'
        print('Saving to: ', fpath)
        with open(fpath, 'w') as f:
            json.dump(data,f)

        while not fpath.exists():
            time.sleep(0.3)
        if fpath.exists():
            gdf = gpd.read_file(fpath)
        else:
            raise IOError('File was not correctly written to disk: ', fpath)

        # Write to cache
        VECTILE_CACHE[cache_key] = {
            'loaded': True,
            'dframe': gdf,
            'fpath': fpath
        }
        return gdf
    
    def to_ndoverlay(self, colors=None, labels=None):
        """
        Fetches the vector tile (from python cache or from the local disk or from the web service <- search order)
        and returns a NdOverlay of Shape Elements with a numeric index

        kwargs:    
        - colors (iterable of color values, or str indicating a colormap definted in holoviews)
            : Used to generate a itertools.cycle to cycle through color values. 
            : Default is 'Category20'
            eg: color=bokeh.palettes.Category20_10

        For hv.Cycle('colomap_name')'s usage, refer to: 
        http://holoviews.org/user_guide/Style_Mapping.html
        """

        gdf = self.to_gdf()
        colors = colors or 'Category20'

        # return ndoverlay of each shape
        ndoverlay = hv.NdOverlay({i: gv.Shape(geom).opts(fill_color=hv.Cycle(colors))
                          for (i,geom) in enumerate(gdf.geometry)})
#         if labels is not None:
#             ndoverlay = relabel_children(ndoverlay, labels)
    
        return ndoverlay
        
        
        
        
        
        