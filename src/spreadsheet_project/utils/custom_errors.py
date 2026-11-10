class SpreadSheetError(Exception):
	pass

class InvalidCellIdError(SpreadSheetError):
	pass

class CellNotPresentError(SpreadSheetError):
	pass

class MethodNotImplementedError(SpreadSheetError):
	pass