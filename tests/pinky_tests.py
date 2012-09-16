import sys
sys.path.append('..')
sys.path.append('/usr/local/Cellar/google-app-engine/1.7.1/share/google-app-engine/')

import unittest
from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.ext import testbed

from model import Tile

def pinky_test():
    assert 1 == 1

class TileTest(unittest.TestCase):

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

    def tearDown(self):
        self.testbed.deactivate()

    def testInsertEntity(self):
        t = Tile(x=0, y=1, shape=0, view_blob='blob')
        t.put()
        self.assertEqual(1, len(Tile.all().fetch(2)))
