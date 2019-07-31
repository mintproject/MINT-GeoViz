import os, sys
from pathlib import Path
from pprint import pprint

# Set path to the utils directory
CURR_DIR = Path(__file__).resolve().parent
print('Current file loc: ', CURR_DIR)
UTILS_DIR = (CURR_DIR.parent/'utils').resolve()
assert UTILS_DIR.exists()
if str(UTILS_DIR) not in sys.path:
    sys.path.insert(0, str(UTILS_DIR))
    print(f"Added {str(UTILS_DIR)} to sys.path")

# pprint(sys.path)

# Unit test starts here
import unittest
import utils

class TestCalc(unittest.TestCase):
    
    def test_get_mro(self):
        print( utils.get_mro('somestring') )

    def test_nprint(self):
        utils.nprint(10, 100)
        utils.nprint("line1", "line2")
        utils.nprint(['ele1', 'ele2','ele3'])
        utils.nprint('line1', 'line2', 'line3')

    def test_dict2json(self):
        d = {'user': ['hayley', 'wanting', 'bob', 'yijun'],
             'age': [10,12,11, 9]
            }
        pprint(d)
        pprint(utils.dict2json(d))

    def test_cols_with_null(self):
        pass

    def test_check_url(self):
        url = 'http://workflow.isi.edu/MINT/FLDAS/FLDAS_NOAH01_A_EA_D.001/2019/04/FLDAS_NOAH01_A_EA_D.A20190401.001.nc'
        print('url: ', url)

        result = utils.check_url(url)
        self.assertTrue(result)

    
if __name__ == '__main__':
    unittest.main()