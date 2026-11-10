from cell import Cell
from ./utils/cell_utils import is_valid_cell_id
from ./utils/custom_errors import InvalidCellIdError
from ./utils/custom_errors import CellNotPresentError
from ./utils/cell_utils import EvaluatedCellValue

class Sheet:
	def __init__(self)-> None:
		self._cells: dict[str, Cell] = {}

	def _create_if_not_exists(self, cell_id: str) -> None:
		if not is_valid_cell_id(cell_id):
			raise InvalidCellIdError(f"{cell_id} is not in valid cell id formula")
		if cell_id not in self._cells:
			self._cells[cell_id] = Cell(cell_id)

	def set_value(self, cell_id: str, cell_value: str) -> None:
		self._create_if_not_exists(cell_id)
		self._cells[cell_id].cell_value = cell_value

	def get_value(self, cell_id: str) -> EvaluatedCellValue:
		if cell_id not in self._cells:
			return None
		return self._cells[cell_id].cell_value
