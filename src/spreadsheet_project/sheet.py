from spreadsheet_project.cell import Cell

from spreadsheet_project.utils.cell_utils import (is_valid_cell_id, 
	EvaluatedCellValue, 
	parse_number,
	parse_formula
	)
from spreadsheet_project.utils.custom_errors import (InvalidCellIdError, 
	CellNotPresentError, 
	CircularFormulaError,
	InvalidFormulaError,
	DivisionByZeroError,
	NonNumericCellError
	)
import operator


_OPERATORS = {
	"+" : operator.add,
	"-" : operator.sub,
	"*" : operator.mul,
	"/" : operator.truediv
}

class Sheet:
	def __init__(self)-> None:
		self._cells: dict[str, Cell] = {}

	def _create_if_not_exists(self, cell_id: str) -> None:
		if not is_valid_cell_id(cell_id):
			raise InvalidCellIdError(f"{cell_id} is not in valid cell id format")
		if cell_id not in self._cells:
			self._cells[cell_id] = Cell(cell_id)

	def set_value(self, cell_id: str, cell_value: str) -> None:
		self._create_if_not_exists(cell_id)
		self._cells[cell_id].cell_value = cell_value

	def get_value(self, cell_id: str, visited: set[str]|None = None) -> EvaluatedCellValue:

		if visited is None:
			visited : set[str] = set()

		if cell_id not in self._cells:
			return None

		raw_value = self._cells[cell_id].cell_value

		if parse_number(raw_value) is not None:
			return parse_number(raw_value)

		if isinstance(raw_value, str) and raw_value.startswith("="):
			if cell_id in visited:
				raise CircularFormulaError(f"Circular formula error with cell {cell_id} repeating")
			visited.add(cell_id)
			try:
				return self._evaluate_formula(raw_value[1:], visited)

			finally:
				visited.discard(cell_id)

		return raw_value

	def _evaluate_formula(self, raw_value:str, visited: set[str]) -> EvaluatedCellValue:
		if not isinstance(raw_value, str):
			return None
		parsed_formula = parse_formula(raw_value)
		if parsed_formula is None:
			raise InvalidFormulaError(f"{raw_value} is invalid formula")
		left, op, right = parsed_formula
		left_value = self._get_operand_value(left, visited)
		right_value = self._get_operand_value(right, visited)
		if right_value == 0 and op == '/':
			raise DivisionByZeroError("Division by zero")
		return _OPERATORS[op](left_value, right_value)


	def _get_operand_value(self, cell_value: str, visited: set[str]) -> int | float : 
		number = parse_number(cell_value)
		if number is not None:
			return number

		value = self.get_value(cell_value, visited)
		if value is None or value == "":
			return 0
		if isinstance(value, bool) or not isinstance(value, (int, float)):
			raise NonNumericCellError("Cell is not a numeric value")
		return value


