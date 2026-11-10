import unittest

from spreadsheet_project.sheet import Sheet
from spreadsheet_project.utils.custom_errors import InvalidCellIdError


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


if __name__ == "__main__":
	unittest.main()
