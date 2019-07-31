import os
import json
from IPython.display import JSON, display

from pathlib import Path
from pprint import pprint
import pdb

from geopy.geocoders import Nominatim

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
    
def dict2json(d):
    return JSON(d)

def display_dict2json(d):
    display(JSON(d))

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

def is_valid_url(path):
    import requests
    r = requests.head(path)
    return r.status_code == requests.codes.ok

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