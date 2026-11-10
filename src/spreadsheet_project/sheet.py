from spreadsheet_project.cell import Cell
from spreadsheet_project.formula import evaluate_formula

from spreadsheet_project.utils.cell_utils import is_valid_cell_id, EvaluatedCellValue, parse_number
from spreadsheet_project.utils.custom_errors import InvalidCellIdError, CircularReferenceError

class Sheet:
	def __init__(self)-> None:
		self._cells: dict[str, Cell] = {}
		self._evaluating: set[str] = set()

	def _create_if_not_exists(self, cell_id: str) -> None:
		if not is_valid_cell_id(cell_id):
			raise InvalidCellIdError(f"{cell_id} is not in valid cell id format")
		if cell_id not in self._cells:
			self._cells[cell_id] = Cell(cell_id)

	def set_value(self, cell_id: str, cell_value: str) -> None:
		self._create_if_not_exists(cell_id)
		self._cells[cell_id].cell_value = cell_value

	def get_value(self, cell_id: str) -> EvaluatedCellValue:
		if cell_id not in self._cells:
			return None

		raw_value = self._cells[cell_id].cell_value
		number = parse_number(raw_value)
		if number is not None:
			return number

		if isinstance(raw_value, str) and raw_value.startswith("="):
			if cell_id in self._evaluating:
				raise CircularReferenceError(f"circular reference detected at {cell_id}")
			self._evaluating.add(cell_id)
			try:
				return self._evaluate_formula(raw_value[1:])
			finally:
				self._evaluating.discard(cell_id)

		return raw_value

	def _evaluate_formula(self, raw_value: str) -> int | float:
		return evaluate_formula(raw_value, self.get_value)
