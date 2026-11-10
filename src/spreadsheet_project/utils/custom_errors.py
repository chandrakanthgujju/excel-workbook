class SpreadSheetError(Exception):
	pass

class InvalidCellIdError(SpreadSheetError):
	pass

class CellNotPresentError(SpreadSheetError):
	pass

class CircularFormulaError(SpreadSheetError):
	pass

class InvalidFormulaError(SpreadSheetError):
	pass

class DivisionByZeroError(SpreadSheetError):
	pass

class NonNumericCellError(SpreadSheetError):
	pass