import os
import json
from IPython.display import JSON, display

import datetime as dt
from pathlib import Path
from pprint import pprint
import pdb

from geopy.geocoders import Nominatim

    
################################################################################
# Python Object Inspection Helpers
################################################################################
def get_mro(myObj):
    return myObj.__class__.mro()

def show_attrs(myObj):
    import holoviews as hv
    atts = [str(att) for att in dir(myObj) if not att.startswith('_')]
    n_atts = len(atts)
    return hv.Table(pd.DataFrame(atts, columns=['att']))

def nprint(*args, header=True):
    if header:
        print("="*80)
    for arg in args:
        pprint(arg)

def attr_print(myObj):
    attrs = [att for att in dir(dimx) if not att.startswith('_')]
    pprint(attrs)
    
################################################################################
# Geocoding Conversion Helpers
################################################################################
## geocoders: addr string -> lat, lon & vice versa
def get_latlon(addr_str):
    """
    Given a string address, resolve its location in (lat, lon) degrees
    """
    geolocator = Nominatim(user_agent="myawesomeproj")
    loc = geolocator.geocode(addr_str)
    return loc.latitude, loc.longitude

def get_addr(lat, lon):
    """
    Given lat, lon in degrees, return a resolved address as a string.
    Eg: get_addr_str(52.509669, 13.376294) -> "Potsdamer Platz, Mitte, Berlin, 10117..."
    """
    geolocator = Nominatim(user_agent="specify_your_app_name_here")
    loc= geolocator.reverse(f'{lat}, {lon}')
    return loc.address

################################################################################
# Time Type Conversion Helpers
################################################################################
def to_datetime(tlist):
    """
    Operation to convert any non-python datetime object in a list of time objects
    to (python) dt.datetime object. 
    This is useful for making the xaxis of any time-series plots human-readable, 
    possibly due to a bug in bokeh.
    """
    mro = get_mro
    
    # check if the topmost mro is datetime.datetime object
    if all( (mro(t)[0] == dt.datetime) for t in tlist):
        return tlist

    print('Converting timevalues to python datetime object')
    dt_list= list(map(lambda t: t.to_pydatetime(), tlist))
    return dt_list
        
################################################################################
# URL helpers
################################################################################
def dict2json(d):
    return JSON(d)

def display_dict2json(d):
    display(JSON(d))

def is_valid_url(path):
    import requests
    r = requests.head(path)
    return r.status_code == requests.codes.ok
    
    
################################################################################
# Pandas helpers
################################################################################
def cols_with_null(df):
    """
    Returns any columnnames with any null value
    Args:
    - df(pandas.DataFrame)
    Returns:
    - cols (list): list of strings, each of which correseponds to the column name
    with any null values
    """
           
    cols = [c for c in df.columns if df[c].isnull().values.any()]
    return cols

def select(df, selection, axis):
    """
    Returns a new dataframe with its axis reduced to the elements in `selection`
    
    Args: 
    - selection (list): a list of column names (if axis=1) or row indices (if axis=0)
    - axis: 0 for row selection, 1 for column selection
    
    Example:
    ```python
    df = pd.DataFrame({'a': [1,2,3], 'b': [10,20,30]})
    
    # select certain columns, in a certain order
    new_cols = ['b']
    print(select(df, new_cols, axis=1))
    
    # Reorder columns
    new_cols = ['b','a']
    print(select(df, new_cols, axis=1)
    
    # Select a subset of rows
    r_sels = [0]
    print(select(df, r_sels, axis=0)
    
    ```
    """
    if axis not in [0,1]:
        raise ValueError(f'axis must be either 0 or 1:  {axis}')
    if axis == 0:
        return df.loc[df.index.isin(selection)]
    if axis == 1:
        return df[selection]
    
    
def reorder_cols(df, new_cols):
    """
    Returns a new dataframe with column orders switched to the new_cols
    Args:
    - df (pd.DataFrame)
    - new_cols (list): a list of new column names. Can be a subset of df.columns
        in which case, only specified columns will be selected in the given order
    Returns:
    - pd.DataFrame: a new dataframe object with the columns selected
    """
    if not set(new_cols).issubset(set(df.columns)):
        raise ValueError('Input column list must be a subset of the original df')
    return df[new_cols]
    

################################################################################
# Xarray helpers
################################################################################


################################################################################
# holoviews helpers
# todo: move to hv_utils.py
################################################################################
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
# Tests
################################################################################
def test_get_mro():
    print( get_mro('somestring') )

def test_nprint():
    nprint(10, 100)
    nprint("line1", "line2")
    nprint(['ele1', 'ele2','ele3'])
    nprint('line1', 'line2', 'line3')

def test_dict2json():
    d = {'user': ['hayley', 'wanting', 'bob', 'yijun'],
         'age': [10,12,11, 9]
        }
    print(d)
    print(dict2json(d))

def test_cols_with_null():
    pass

def test_is_valid_url():
    url = 'http://workflow.isi.edu/MINT/FLDAS/FLDAS_NOAH01_A_EA_D.001/2019/04/FLDAS_NOAH01_A_EA_D.A20190401.001.nc'
    print('url: ', url)
    print('url exists? :', is_valid_url(url))
    
def test_get_latlon():
    addr = '424 West Pico Blvd, Los Angeles, 90015'
    print(addr)
    print(get_latlon(addr))

def test_get_addr():
    lat, lon = -5, 37 # somewhere in africa
    print('lat, lon: ', lat, lon)
    print(get_addr(lat, lon))
    
def test_reorder_cols():
    df = pd.DataFrame({'a': [1,2,3], 'b': [10,20,30]})
    reordered = reorder_cols(df, ['b','a'])
    print('original: ')
    display(df)
    print('reordered: ')
    display(reordered)
                             
def test_all():
    test_get_mro()
    test_nprint()
    test_dict2json()
    test_cols_with_null()
    test_is_valid_url()
    test_get_latlon()
    test_get_addr()
    
    
if __name__ == '__main__':
    test_all()