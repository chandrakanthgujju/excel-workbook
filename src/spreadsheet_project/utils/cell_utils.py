import re
from .custom_errors import InvalidCellIdError

CELL_ID_PATTERN_STRING = "[A-Z]+[1-9][0-9]*"
CELL_ID_PATTERN = re.compile(CELL_ID_PATTERN_STRING)
NUMBER_PATTERN_STRING = r"-?\d+(?:\.\d+)?"
NUMBER_PATTERN = re.compile(NUMBER_PATTERN_STRING)
OPERATOR_PATTERN_STRING = r"[+\-*/]"

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

def parse_number(raw_value: str) -> int | float | None:

	if not isinstance(raw_value, str):
		return None

	num_match = NUMBER_PATTERN.fullmatch(raw_value.strip())
	if num_match is None:
		return None

	num_text = num_match.group(0)

	if "." in num_text:
		return float(num_text)
	return int(num_text)

def parse_formula(raw_value: str) -> tuple[str, str, str] | None:
	formula_match = FORMULA_PATTERN.fullmatch(raw_value)
	if formula_match is None:
		return None
	left = formula_match.group("left")
	arithop = formula_match.group("op")
	right = formula_match.group("right")
	return left, arithop, right


