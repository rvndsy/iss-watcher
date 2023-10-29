import sys, os
import unittest
from unittest.mock import patch
import logging

# Changed the directory to the parent of the current tests folder.

parent_directory_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(1, parent_directory_path)

import main
from main import *

# Using unittest instead of provided example because I wanted to experiment with unittests and I ran into issues with 'logger' from main.
# This test creates mock object for the logger so that 'logger.info(xyz)' lines can be ignored.

class TestGetOsmSearchCoords(unittest.TestCase):

    def test_empty_response(self):
        # Testing an empty json into get_osm_search_coords
        with patch('main.logger', create=True):
            response_json = []
            result = get_osm_search_coords(response_json)
            expected_result = (-200, -200, 'null')
            self.assertEqual(result, expected_result)

    def test_minimal_response(self):
        # Testing as minimal as possible json into get_osm_search_coords
        with patch('main.logger', create=True):
            # Testing 
            response_json = [{'lat': '56.646', 'lon': '24.804', 'display_name': 'Valmiera, Latvia'}]
            result = get_osm_search_coords(response_json)
            expected_result = (56.646, 24.804, 'Valmiera, Latvia')
            self.assertEqual(result, expected_result)

    def test_valid_response(self):
        # Testing a real response json into get_osm_search_coords
        with patch('main.logger', create=True):
            response_json = [{"place_id":182904349,"licence":"Data © OpenStreetMap contributors, ODbL 1.0. http://osm.org/copyright","osm_type":"relation","osm_id":13048680,"lat":"57.5389148","lon":"25.4261688","category":"boundary","type":"administrative","place_rank":14,"importance":0.5170003199625869,"addresstype":"city","name":"Valmiera","display_name":"Valmiera, Valmieras novads, Vidzeme, Latvia","boundingbox":["57.4974929","57.5551153","25.3746416","25.4677580"]}]
            result = get_osm_search_coords(response_json)
            expected_result = (57.5389148, 25.4261688, 'Valmiera, Valmieras novads, Vidzeme, Latvia')
            self.assertEqual(result, expected_result)

if __name__ == '__main__':
    print("Testing function: \"get_osm_search_coords\"")

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestGetOsmSearchCoords)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)