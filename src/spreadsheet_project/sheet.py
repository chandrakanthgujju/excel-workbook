import operator

from spreadsheet_project.cell import Cell

from spreadsheet_project.utils.cell_utils import is_valid_cell_id, EvaluatedCellValue, parse_number, parse_formula
from spreadsheet_project.utils.custom_errors import InvalidCellIdError, \
CellNotPresentError, InvalidFormulaError, DivisionByZeroError, \
NonNumericCellError, CircularReferenceError

_OPERATORS = {
	"+": operator.add,
	"-": operator.sub,
	"*": operator.mul,
	"/": operator.truediv,
}

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
		parsed = parse_formula(raw_value)
		if parsed is None:
			raise InvalidFormulaError(f"invalid formula: {raw_value!r}")
		left, arithop, right = parsed
		left_value = self._value_of_operand(left)
		right_value = self._value_of_operand(right)
		if arithop == "/" and right_value == 0:
			raise DivisionByZeroError("division by zero")
		return _OPERATORS[arithop](left_value, right_value)

	def _value_of_operand(self, operand: str) -> int | float:
		number = parse_number(operand)
		if number is not None:
			return number
		# A formula reads other cells through get_value. An unset cell or a
		# cell stored as "" counts as 0 here; get_value itself still returns
		# None or "" when that cell is read directly.
		value = self.get_value(operand)
		if value is None or value == "":
			return 0
		if isinstance(value, bool) or not isinstance(value, (int, float)):
			raise NonNumericCellError(f"{operand} contains non-numeric text")
		return value
