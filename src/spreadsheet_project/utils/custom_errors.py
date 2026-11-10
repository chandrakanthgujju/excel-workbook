class SpreadSheetError(Exception):
	pass

class InvalidCellIdError(SpreadSheetError):
	pass

class CellNotPresentError(SpreadSheetError):
	pass

class MalformedFormulaError(SpreadSheetError):
	pass

class DivisionByZeroError(SpreadSheetError):
	pass

class CircularReferenceError(SpreadSheetError):
	pass

class NonNumericCellError(SpreadSheetError):
	pass
