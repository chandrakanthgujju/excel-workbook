from spreadsheet_project.cell import Cell

from spreadsheet_project.utils.cell_utils import (is_valid_cell_id, 
	EvaluatedCellValue, 
	parse_number,
	parse_formula
	)
from spreadsheet_project.utils.custom_errors import (InvalidCellIdError,
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
		self._cache: dict[str, EvaluatedCellValue] = {}
		self._depends_on: dict[str, set[str]] = {}
		self._dependants: dict[str, set[str]] = {}

	def _create_if_not_exists(self, cell_id: str) -> None:
		if not is_valid_cell_id(cell_id):
			raise InvalidCellIdError(f"{cell_id} is not in valid cell id format")
		if cell_id not in self._cells:
			self._cells[cell_id] = Cell(cell_id)

	def set_value(self, cell_id: str, cell_value: str) -> None:
		self._create_if_not_exists(cell_id)
		self._cells[cell_id].cell_value = cell_value
		old_refs = set(self._depends_on.get(cell_id, ()))
		for ref in old_refs:
			dependants = self._dependants.get(ref)
			if dependants is None:
				continue
			dependants.discard(cell_id)
		self._depends_on[cell_id] = set()
		if isinstance(cell_value, str) and cell_value.startswith("="):
			parsed_formula = parse_formula(cell_value[1:].strip())
			if parsed_formula is not None:
				left, _op, right = parsed_formula
				for operand in (left, right):
					if is_valid_cell_id(operand):
						self._depends_on[cell_id].add(operand)
						self._dependants.setdefault(operand, set()).add(cell_id)
		self._invalidate(cell_id)

	def _invalidate(self, cell_id: str) -> None:
		stack = [cell_id]
		seen: set[str] = set()
		while stack:
			current = stack.pop()
			if current in seen:
				continue
			seen.add(current)
			self._cache.pop(current, None)
			stack.extend(self._dependants.get(current, ()))

def get_value(self, cell_id: str, visited: set[str]|None = None) -> EvaluatedCellValue:

		if cell_id in self._cache:
			return self._cache[cell_id]			

		if visited is None:
			visited : set[str] = set()

		if cell_id not in self._cells:
			return None

		raw_value = self._cells[cell_id].cell_value

		if parse_number(raw_value) is not None:
			numeric_value = parse_number(raw_value)
			self._cache[cell_id] = numeric_value
			return numeric_value
		if isinstance(raw_value, str) and raw_value.startswith("="):
			if cell_id in visited:
				raise CircularFormulaError(f"Circular formula error with cell {cell_id} repeating")
			visited.add(cell_id)
			try:
				evaluated_value = self._evaluate_formula(raw_value[1:], visited)
				self._cache[cell_id] = evaluated_value
				return evaluated_value
			finally:
				visited.discard(cell_id)

		return raw_value

	def _evaluate_formula(self, raw_value:str, visited: set[str]) -> EvaluatedCellValue:
		if not isinstance(raw_value, str):
			return None
		parsed_formula = parse_formula(raw_value.strip())
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


