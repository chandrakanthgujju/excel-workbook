import unittest

from spreadsheet_project.sheet import Sheet
from spreadsheet_project.utils.cell_utils import get_cell_ids, get_column_name, split_cell_id
from spreadsheet_project.utils.custom_errors import CircularFormulaError, InvalidFormulaError


class AggregateFunctionTest(unittest.TestCase):

	def setUp(self):
		self.sheet = Sheet()

	def test_sum_min_max_avg_over_column(self):
		self.sheet.set_value("A1", "1")
		self.sheet.set_value("A2", "2")
		self.sheet.set_value("A3", "3")
		self.sheet.set_value("B1", "=SUM(A1:A3)")
		self.sheet.set_value("B2", "=MIN(A1:A3)")
		self.sheet.set_value("B3", "=MAX(A1:A3)")
		self.sheet.set_value("B4", "=AVG(A1:A3)")
		self.assertEqual(self.sheet.get_value("B1"), 6)
		self.assertEqual(self.sheet.get_value("B2"), 1)
		self.assertEqual(self.sheet.get_value("B3"), 3)
		self.assertEqual(self.sheet.get_value("B4"), 2.0)

	def test_two_dimensional_range(self):
		self.sheet.set_value("A1", "1")
		self.sheet.set_value("A2", "2")
		self.sheet.set_value("B1", "3")
		self.sheet.set_value("B2", "4")
		self.sheet.set_value("C1", "=SUM(A1:B2)")
		self.sheet.set_value("C2", "=MIN(A1:B2)")
		self.sheet.set_value("C3", "=MAX(A1:B2)")
		self.sheet.set_value("C4", "=AVG(A1:B2)")
		self.assertEqual(self.sheet.get_value("C1"), 10)
		self.assertEqual(self.sheet.get_value("C2"), 1)
		self.assertEqual(self.sheet.get_value("C3"), 4)
		self.assertEqual(self.sheet.get_value("C4"), 2.5)

	def test_reversed_range(self):
		self.sheet.set_value("A1", "1")
		self.sheet.set_value("A2", "2")
		self.sheet.set_value("A3", "3")
		self.sheet.set_value("B1", "=SUM(A3:A1)")
		self.assertEqual(self.sheet.get_value("B1"), 6)

	def test_blanks_and_text_are_skipped(self):
		self.sheet.set_value("A1", "5")
		self.sheet.set_value("A2", "")
		self.sheet.set_value("A3", "hello")
		self.sheet.set_value("B1", "=MIN(A1:A3)")
		self.sheet.set_value("B2", "=SUM(A1:A3)")
		self.assertEqual(self.sheet.get_value("B1"), 5)
		self.assertEqual(self.sheet.get_value("B2"), 5)

	def test_empty_range(self):
		self.sheet.set_value("B1", "=SUM(A1:A3)")
		self.sheet.set_value("B2", "=MIN(A1:A3)")
		self.sheet.set_value("B3", "=AVG(A1:A3)")
		self.assertEqual(self.sheet.get_value("B1"), 0)
		with self.assertRaises(InvalidFormulaError):
			self.sheet.get_value("B2")
		with self.assertRaises(InvalidFormulaError):
			self.sheet.get_value("B3")

	def test_sum_range_including_itself_is_circular(self):
		self.sheet.set_value("A1", "1")
		self.sheet.set_value("A3", "3")
		self.sheet.set_value("A2", "=SUM(A1:A3)")
		with self.assertRaises(CircularFormulaError):
			self.sheet.get_value("A2")

	def test_sum_cache_refreshes_when_input_changes(self):
		self.sheet.set_value("A1", "1")
		self.sheet.set_value("A2", "2")
		self.sheet.set_value("A3", "3")
		self.sheet.set_value("B1", "=SUM(A1:A3)")
		self.assertEqual(self.sheet.get_value("B1"), 6)
		self.assertIn("B1", self.sheet._cache)
		self.sheet.set_value("A2", "10")
		self.assertNotIn("B1", self.sheet._cache)
		self.assertEqual(self.sheet.get_value("B1"), 14)


class CellIdHelperTest(unittest.TestCase):

	def test_column_name_round_trip(self):
		expected = {"A": 1, "Z": 26, "AA": 27, "AZ": 52, "XFD": 16384}
		for name, col in expected.items():
			with self.subTest(name=name):
				self.assertEqual(split_cell_id(name + "1"), (col, 1))
				self.assertEqual(get_column_name(col), name)

	def test_get_cell_ids(self):
		self.assertEqual(get_cell_ids("A1", "A3"), ["A1", "A2", "A3"])
		self.assertEqual(get_cell_ids("A3", "A1"), ["A1", "A2", "A3"])
		self.assertEqual(get_cell_ids("A1", "B2"), ["A1", "A2", "B1", "B2"])
