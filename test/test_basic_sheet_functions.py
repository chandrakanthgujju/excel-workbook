import unittest

from spreadsheet_project.sheet import Sheet
from spreadsheet_project.utils.custom_errors import InvalidCellIdError
from spreadsheet_project.utils.cell_utils import parse_number, parse_formula

class SpreadSheetBasicFunctions(unittest.TestCase):

	def setUp(self):
		self.sheet = Sheet()

	def test_set_and_get(self):
		self.sheet.set_value("A1", "1")
		self.assertEqual(self.sheet.get_value("A1"), 1)

	def test_invalid_cell_id_raises(self):
		for cell_id in ("A0", "1A"):
			with self.subTest(cell_id=cell_id):
				with self.assertRaises(InvalidCellIdError):
					self.sheet.set_value(cell_id, "1")

	def test_unset_cell_returns_none(self):
		self.assertIsNone(self.sheet.get_value("A1"))

	def test_parse_number(self):
		raw_decimal = "1.2"
		raw_int = "45"
		raw_neg_decimal = "-23.543"
		self.assertEqual(parse_number(raw_decimal), 1.2)
		self.assertEqual(parse_number(raw_int), 45)
		self.assertEqual(parse_number(raw_neg_decimal), -23.543)

	def test_parse_formula(self):
		raw_formula = "A1+2"
		(left, op, right) = parse_formula(raw_formula)
		self.assertEqual(left, "A1")
		self.assertEqual(op, "+")
		self.assertEqual(right, "2")


if __name__ == "__main__":
	unittest.main()
