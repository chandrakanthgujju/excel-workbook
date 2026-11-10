import unittest

from spreadsheet_project.sheet import Sheet
from spreadsheet_project.utils.custom_errors import CircularFormulaError


class SheetCacheTest(unittest.TestCase):

	def setUp(self):
		self.sheet = Sheet()

	def test_cached_value_reused(self):
		self.sheet.set_value("A1", "1")
		self.sheet.set_value("B1", "2")
		self.sheet.set_value("C1", "=A1+B1")
		first = self.sheet.get_value("C1")
		self.assertEqual(first, 3)
		self.assertIn("C1", self.sheet._cache)
		second = self.sheet.get_value("C1")
		self.assertEqual(second, first)
		self.assertIs(self.sheet._cache["C1"], first)

	def test_changing_left_operand_invalidates(self):
		self.sheet.set_value("A1", "1")
		self.sheet.set_value("B1", "2")
		self.sheet.set_value("C1", "=A1+B1")
		self.assertEqual(self.sheet.get_value("C1"), 3)
		self.sheet.set_value("A1", "10")
		self.assertNotIn("C1", self.sheet._cache)
		self.assertEqual(self.sheet.get_value("C1"), 12)

	def test_changing_right_operand_invalidates(self):
		self.sheet.set_value("A1", "1")
		self.sheet.set_value("B1", "2")
		self.sheet.set_value("C1", "=A1+B1")
		self.assertEqual(self.sheet.get_value("C1"), 3)
		self.sheet.set_value("B1", "5")
		self.assertNotIn("C1", self.sheet._cache)
		self.assertEqual(self.sheet.get_value("C1"), 6)

	def test_chain_invalidates_transitively(self):
		self.sheet.set_value("A1", "1")
		self.sheet.set_value("C1", "=A1+1")
		self.sheet.set_value("D1", "=C1+1")
		self.assertEqual(self.sheet.get_value("D1"), 3)
		self.assertIn("D1", self.sheet._cache)
		self.sheet.set_value("A1", "10")
		self.assertNotIn("C1", self.sheet._cache)
		self.assertNotIn("D1", self.sheet._cache)
		self.assertEqual(self.sheet.get_value("C1"), 11)
		self.assertEqual(self.sheet.get_value("D1"), 12)

	def test_resetting_formula_drops_old_dependant(self):
		self.sheet.set_value("A1", "1")
		self.sheet.set_value("B1", "2")
		self.sheet.set_value("C1", "=A1+B1")
		self.assertIn("C1", self.sheet._dependants["B1"])
		self.sheet.set_value("C1", "=A1+1")
		self.assertNotIn("C1", self.sheet._dependants.get("B1", set()))
		self.assertFalse(self.sheet._dependants.get("B1"))
		self.assertEqual(self.sheet.get_value("C1"), 2)
		self.sheet.set_value("B1", "9")
		self.assertEqual(self.sheet.get_value("C1"), 2)

	def test_referenced_unset_cell_returns_none(self):
		self.sheet.set_value("B1", "=A1+2")
		self.assertNotIn("A1", self.sheet._cells)
		self.assertIsNone(self.sheet.get_value("A1"))
		self.assertEqual(self.sheet.get_value("B1"), 2)

	def test_circular_pair_raises_without_hanging_on_set(self):
		self.sheet.set_value("A1", "=B1+1")
		self.sheet.set_value("B1", "=A1+1")
		with self.assertRaises(CircularFormulaError):
			self.sheet.get_value("A1")
		with self.assertRaises(CircularFormulaError):
			self.sheet.get_value("B1")
