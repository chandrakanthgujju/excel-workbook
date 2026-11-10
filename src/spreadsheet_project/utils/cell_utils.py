import re
from .custom_errors import InvalidCellIdError

CELL_ID_PATTERN_STRING = "[A-Z]+[1-9][0-9]*"
CELL_ID_PATTERN = re.compile(CELL_ID_PATTERN_STRING)

NUMBER_PATTERN_STRING = r"-?\d+(?:\.\d+)?"
OPERATOR_PATTERN_STRING = r"[+*/-]"
FORMULA_PATTERN = re.compile(
	rf"(?P<left>(?:{NUMBER_PATTERN_STRING}|{CELL_ID_PATTERN_STRING}))"
	rf"\s*(?P<op>{OPERATOR_PATTERN_STRING})\s*"
	rf"(?P<right>(?:{NUMBER_PATTERN_STRING}|{CELL_ID_PATTERN_STRING}))"
)

EvaluatedCellValue = int | float | str | None

def is_valid_cell_id(cell_id: str) -> bool:
	if not isinstance(cell_id, str):
		raise ValueError("cell_id must be string")
	cell_id_pattern_match = CELL_ID_PATTERN.fullmatch(cell_id)
	if cell_id_pattern_match is None:
		return False
	return True

def parse_number(raw_value) -> int | float | None:
	if not isinstance(raw_value, str):
		return None
	# Capturing group is the optional decimal part, so integers stay int.
	number_match = re.fullmatch(r"-?\d+(\.\d+)?", raw_value.strip())
	if number_match is None:
		return None
	if number_match.group(1) is not None:
		return float(number_match.group(0))
	return int(number_match.group(0))

def parse_formula(raw_value) -> tuple[str, str, str] | None:
	if not isinstance(raw_value, str):
		return None
	formula_match = FORMULA_PATTERN.fullmatch(raw_value.strip())
	if formula_match is None:
		return None
	left, arithop, right = formula_match.groups()
	return left, arithop, right
