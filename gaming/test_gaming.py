import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from app import stick
import unittest
class StickTests(unittest.TestCase):
    def test_neutral(self):
        for value in (-5000,0,5000):self.assertEqual(stick(value),0)
    def test_range(self):
        self.assertEqual(stick(32767),32767)
        self.assertEqual(stick(-32768),-32768)
        self.assertGreater(stick(16000),0)
        self.assertLess(stick(-16000),0)
