"""Happy path for storing a cell and evaluating a simple formula.

Both tests are expected failures on the current source. The comments on each
test name the failure that stops that path. Source files are not modified here.

Run from the repository root:

    python3 -m unittest discover -s test -v
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))


class SheetHappyPathTest(unittest.TestCase):
    @unittest.expectedFailure
    def test_set_value_and_read_it_back(self):
        """Set a literal on A1 and read that same value back.

        Expected failure: src/spreadsheet_project/sheet.py lines 2-5 are
        invalid import syntax, so Sheet cannot be imported. Past that,
        utils/cell_utils.py is_valid_cell_id raises ValueError for a string
        cell id (the isinstance check is inverted), so set_value never stores
        A1.
        """
        from spreadsheet_project.sheet import Sheet

        sheet = Sheet()
        sheet.set_value("A1", "42")
        self.assertEqual(sheet.get_value("A1"), "42")

    @unittest.expectedFailure
    def test_simple_addition_formula(self):
        """A1=2, B1=3, and C1==A1+B1 should read back as 5.

        Expected failure: the same import and cell-id failures as the literal
        test. Sheet.get_value also returns the raw stored string and never
        evaluates formulas (sheet.py get_value; Cell.evaluated_value stays
        unset), so C1 would come back as the text '=A1+B1'.
        """
        from spreadsheet_project.sheet import Sheet

        sheet = Sheet()
        sheet.set_value("A1", "2")
        sheet.set_value("B1", "3")
        sheet.set_value("C1", "=A1+B1")
        self.assertEqual(sheet.get_value("C1"), "5")


if __name__ == "__main__":
    unittest.main()
