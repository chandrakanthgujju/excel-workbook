class SpreadSheetError(Exception):
	pass

class InvalidCellIdError(SpreadSheetError):
	pass

class CellNotPresentError(SpreadSheetError):
	pass

class InvalidFormulaError(SpreadSheetError):
	pass

class DivisionByZeroError(SpreadSheetError):
	pass

class NonNumericCellError(SpreadSheetError):
	pass

class CircularReferenceError(SpreadSheetError):
	pass