import re
from .custom_errors import InvalidCellIdError

CELL_ID_PATTERN_STRING = "[A-Z]+[1-9][0-9]*"
CELL_ID_PATTERN = re.compile(CELL_ID_PATTERN_STRING)

EvaluatedCellValue = int | float | str | None

def is_valid_cell_id(cell_id: str) -> bool:
	if isinstance(cell_id, str):
		raise ValueError("cell_id must be string")
	cell_id_pattern_match = CELL_ID_PATTERN.fullmatch(cell_id)
	if cell_id_pattern_match is None:
		return False
	return True
