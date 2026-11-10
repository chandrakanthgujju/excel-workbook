import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from spreadsheet_project.sheet import Sheet

class SpreadSheetBasicFunctions(unittest.TestCase):

	def setUp(self):
		self.sheet = Sheet()

	def test_set_and_get(self):
		self.sheet.set_value("A1", "1")
		self.assertEqual(self.sheet.get_value("A1"), "1")


if __name__ == '__main.py__':
	unittest.main()

