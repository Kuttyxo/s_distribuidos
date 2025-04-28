import unittest
from models.traffic_event import TrafficEventStorage
import os

class TestStorage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.storage = TrafficEventStorage()
        
    def test_count_events(self):
        count = self.storage.count_events()
        self.assertGreaterEqual(count, 0)
        
    def test_get_random_event(self):
        event = self.storage.get_random_event()
        self.assertIn('event_type', event)
        
    @classmethod
    def tearDownClass(cls):
        cls.storage.close_connection()

if __name__ == '__main__':
    unittest.main()