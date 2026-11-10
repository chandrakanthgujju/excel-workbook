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

AGG_FUNCTION_PATTERN = re.compile(rf"(?P<func>SUM|MIN|MAX|AVG)\(\s*"
	rf"(?P<start>{CELL_ID_PATTERN_STRING})\s*:\s*"
	rf"(?P<end>{CELL_ID_PATTERN_STRING})\s*\)"
	)

CELL_PARTS = re.compile(r"(?P<col>[A-Z]+)(?P<row>[1-9][0-9]*)")

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

def parse_function(raw_value: str) -> tuple[str, str, str] | None:
	function_match = AGG_FUNCTION_PATTERN.fullmatch(raw_value)
	if function_match is None:
		return None
	func = function_match.group("func")
	start = function_match.group("start")
	end = function_match.group("end")
	return func, start, end

def split_cell_id(cell_id: str) -> tuple[int, int]:
	cell_match = CELL_PARTS.fullmatch(cell_id)
	col = 0
	for char in cell_match.group("col"):
		col = col*26 + (ord(char) - ord('A')+1)
	row = int(cell_match.group("row"))
	return col, row	

def get_column_name(col: int) -> str:
	col_name = ""
	while col>0:
		quotient = (col-1)//26
		rem = (col-1)%26
		col_name = chr(ord("A")+rem)+col_name
		col = quotient
	return col_name

def get_cell_id(col: int, row: int) -> str:
	col_name = get_column_name(col)
	return col_name+str(row)


def get_cell_ids(start_cell_id: str, end_cell_id: str) -> list[str]:
	c1, r1 = split_cell_id(start_cell_id)
	c2, r2 = split_cell_id(end_cell_id)
	cell_ids = []
	for c in range(min(c1,c2), max(c1,c2)+1):
		for r in range(min(r1,r2), max(r1,r2)+1):
			cell_ids.append(get_cell_id(c,r))

	return cell_ids




