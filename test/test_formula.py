import unittest

from spreadsheet_project.sheet import Sheet
from spreadsheet_project.utils.custom_errors import (
	CircularReferenceError,
	DivisionByZeroError,
	InvalidCellIdError,
	MalformedFormulaError,
	NonNumericCellError,
)


class FormulaEvaluationTest(unittest.TestCase):

	def setUp(self):
		self.sheet = Sheet()

	def test_arithmetic(self):
		cases = (
			("=1+2", 3, int),
			("=2+3*4", 14, int),
			("=(2+3)*4", 20, int),
			("=10/4", 2.5, float),
			("=10/2", 5, int),
			("=-3+5", 2, int),
			("=8-3-2", 3, int),
			("=1 + 2", 3, int),
		)
		for formula, expected, kind in cases:
			with self.subTest(formula=formula):
				self.sheet.set_value("A1", formula)
				result = self.sheet.get_value("A1")
				self.assertEqual(result, expected)
				self.assertIs(type(result), kind)

	def test_cell_reference_precedence(self):
		self.sheet.set_value("A1", "1")
		self.sheet.set_value("B1", "3")
		self.sheet.set_value("C1", "=A1+B1*2")
		result = self.sheet.get_value("C1")
		self.assertEqual(result, 7)
		self.assertIs(type(result), int)

	def test_chained_references(self):
		self.sheet.set_value("A1", "2")
		self.sheet.set_value("B1", "=A1+1")
		self.sheet.set_value("C1", "=B1+1")
		self.assertEqual(self.sheet.get_value("C1"), 4)

	def test_update_propagation(self):
		self.sheet.set_value("A1", "1")
		self.sheet.set_value("B1", "2")
		self.sheet.set_value("C1", "=A1+B1")
		self.assertEqual(self.sheet.get_value("C1"), 3)
		self.sheet.set_value("A1", "10")
		self.assertEqual(self.sheet.get_value("C1"), 12)

	def test_divide_by_zero(self):
		for formula in ("=1/0", "=8/(3-3)"):
			with self.subTest(formula=formula):
				self.sheet.set_value("A1", formula)
				with self.assertRaises(DivisionByZeroError):
					self.sheet.get_value("A1")

	def test_circular_reference_between_two_cells(self):
		self.sheet.set_value("A1", "=B1")
		self.sheet.set_value("B1", "=A1")
		self.sheet.set_value("C1", "4")
		with self.assertRaises(CircularReferenceError):
			self.sheet.get_value("A1")
		self.assertEqual(self.sheet.get_value("C1"), 4)
		with self.assertRaises(CircularReferenceError):
			self.sheet.get_value("B1")

	def test_self_reference(self):
		self.sheet.set_value("A1", "=A1")
		with self.assertRaises(CircularReferenceError):
			self.sheet.get_value("A1")

	def test_malformed_formulas(self):
		for formula in ("=1+", "=*2", "=A1+", "=1 2"):
			with self.subTest(formula=formula):
				self.sheet.set_value("A1", formula)
				with self.assertRaises(MalformedFormulaError):
					self.sheet.get_value("A1")

	def test_invalid_cell_ref_in_formula(self):
		self.sheet.set_value("A1", "=A0+1")
		with self.assertRaises(InvalidCellIdError):
			self.sheet.get_value("A1")

	def test_non_numeric_referenced_cell(self):
		self.sheet.set_value("A1", "hello")
		self.sheet.set_value("B1", "=A1+1")
		self.assertEqual(self.sheet.get_value("A1"), "hello")
		with self.assertRaises(NonNumericCellError):
			self.sheet.get_value("B1")

	def test_unset_and_empty_reference_are_zero(self):
		self.sheet.set_value("B1", "=A1+2")
		self.assertIsNone(self.sheet.get_value("A1"))
		self.assertEqual(self.sheet.get_value("B1"), 2)
		self.sheet.set_value("A1", "")
		self.assertEqual(self.sheet.get_value("A1"), "")
		self.assertEqual(self.sheet.get_value("B1"), 2)

	def test_float_cell_value(self):
		self.sheet.set_value("A1", "2.5")
		result = self.sheet.get_value("A1")
		self.assertEqual(result, 2.5)
		self.assertIs(type(result), float)
		self.sheet.set_value("B1", "=A1+1")
		self.assertEqual(self.sheet.get_value("B1"), 3.5)
		self.assertIs(type(self.sheet.get_value("B1")), float)
