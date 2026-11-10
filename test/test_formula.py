import unittest

from spreadsheet_project.sheet import Sheet
from spreadsheet_project.utils.cell_utils import parse_formula
from spreadsheet_project.utils.custom_errors import (
	CircularFormulaError,
	DivisionByZeroError,
	InvalidFormulaError,
	NonNumericCellError,
)


class ParseFormulaTest(unittest.TestCase):

	def test_one_operation(self):
		self.assertEqual(parse_formula("A1+2"), ("A1", "+", "2"))
		self.assertEqual(parse_formula("A1 * 2.3"), ("A1", "*", "2.3"))
		self.assertEqual(parse_formula("-3+B2"), ("-3", "+", "B2"))

	def test_rejects_anything_else(self):
		for text in ("A1+B1*2", "A1+", "+2", "A1", "abc", "5", "=1+2"):
			with self.subTest(text=text):
				self.assertIsNone(parse_formula(text))


class SheetFormulaTest(unittest.TestCase):

	def setUp(self):
		self.sheet = Sheet()

	def test_formula_with_spaces_around_expression(self):
		self.sheet.set_value("A1", "= 1+2")
		self.assertEqual(self.sheet.get_value("A1"), 3)

	def test_addition_and_division(self):
		self.sheet.set_value("A1", "=1+2")
		result = self.sheet.get_value("A1")
		self.assertEqual(result, 3)
		self.assertIs(type(result), int)

		self.sheet.set_value("A1", "=10/4")
		result = self.sheet.get_value("A1")
		self.assertEqual(result, 2.5)
		self.assertIs(type(result), float)

	def test_cell_times_float(self):
		self.sheet.set_value("A1", "2")
		self.sheet.set_value("B1", "=A1*2.3")
		self.assertEqual(self.sheet.get_value("B1"), 2 * 2.3)

	def test_two_cell_addition(self):
		self.sheet.set_value("A1", "1")
		self.sheet.set_value("A34", "5")
		self.sheet.set_value("C1", "=A1+A34")
		self.assertEqual(self.sheet.get_value("C1"), 6)

	def test_subtraction_example(self):
		self.sheet.set_value("B2", "1")
		self.sheet.set_value("A1", "=3-B2")
		self.assertEqual(self.sheet.get_value("A1"), 2)

	def test_update_propagation(self):
		self.sheet.set_value("A1", "1")
		self.sheet.set_value("B1", "2")
		self.sheet.set_value("C1", "=A1+B1")
		self.assertEqual(self.sheet.get_value("C1"), 3)
		self.sheet.set_value("A1", "10")
		self.assertEqual(self.sheet.get_value("C1"), 12)

	def test_unset_reference_is_zero(self):
		self.sheet.set_value("B1", "=A1+2")
		self.assertIsNone(self.sheet.get_value("A1"))
		self.assertEqual(self.sheet.get_value("B1"), 2)
		self.sheet.set_value("A1", "")
		self.assertEqual(self.sheet.get_value("A1"), "")
		self.assertEqual(self.sheet.get_value("B1"), 2)

	def test_non_numeric_reference_raises(self):
		self.sheet.set_value("A1", "hello")
		self.sheet.set_value("B1", "=A1+1")
		self.assertEqual(self.sheet.get_value("A1"), "hello")
		with self.assertRaises(NonNumericCellError):
			self.sheet.get_value("B1")

	def test_divide_by_zero_raises(self):
		self.sheet.set_value("A1", "=10/0")
		with self.assertRaises(DivisionByZeroError):
			self.sheet.get_value("A1")

	def test_multi_op_formula_raises(self):
		self.sheet.set_value("C1", "=A1+B1*2")
		with self.assertRaises(InvalidFormulaError):
			self.sheet.get_value("C1")

	def test_single_operand_formula_raises(self):
		for formula in ("=A1", "=5"):
			with self.subTest(formula=formula):
				self.sheet.set_value("B1", formula)
				with self.assertRaises(InvalidFormulaError):
					self.sheet.get_value("B1")

	def test_self_reference_raises(self):
		self.sheet.set_value("A1", "=A1+1")
		with self.assertRaises(CircularFormulaError):
			self.sheet.get_value("A1")


if __name__ == "__main__":
	unittest.main()