import re
from collections.abc import Callable

from spreadsheet_project.utils.cell_utils import EvaluatedCellValue, is_valid_cell_id, parse_number
from spreadsheet_project.utils.custom_errors import (
	DivisionByZeroError,
	InvalidCellIdError,
	MalformedFormulaError,
	NonNumericCellError,
)

# Whitespace, unsigned number, cell-like reference, or one operator/paren.
_TOKEN_RE = re.compile(r"\s+|[0-9]+(?:\.[0-9]+)?|[A-Za-z]+[0-9]+|[+\-*/()]")

# expr -> term (("+" | "-") term)*
# term -> factor (("*" | "/") factor)*
# factor -> NUMBER | CELL | "(" expr ")" | "-" factor
Node = tuple


def evaluate_formula(source: str, get_value: Callable[[str], EvaluatedCellValue]) -> int | float:
	"""Evaluate a formula body with the leading '=' already removed.

	Cell references call get_value. A referenced cell that was never set
	(None) or holds an empty string is 0. Any other non-numeric value is an
	error. Parsing finishes before any cell is read, so a broken formula is
	reported as malformed even when it also names the cell being evaluated.
	"""
	tree = _Parser(tokenize(source), source).parse()
	return _evaluate(tree, get_value)


def tokenize(source: str) -> list[tuple[str, str]]:
	tokens: list[tuple[str, str]] = []
	position = 0
	while position < len(source):
		match = _TOKEN_RE.match(source, position)
		if match is None:
			raise MalformedFormulaError(f"malformed formula: {source!r}")
		position = match.end()
		text = match.group()
		if text.isspace():
			continue
		if text[0].isdigit():
			tokens.append(("NUMBER", text))
			continue
		if text[0].isalpha():
			if not is_valid_cell_id(text):
				raise InvalidCellIdError(f"{text} is not in valid cell id format")
			tokens.append(("CELL", text))
			continue
		tokens.append((text, text))
	return tokens


class _Parser:
	def __init__(self, tokens: list[tuple[str, str]], source: str) -> None:
		self._tokens = tokens
		self._source = source
		self._index = 0

	def parse(self) -> Node:
		tree = self._expr()
		if not self._at_end():
			self._fail()
		return tree

	def _expr(self) -> Node:
		node = self._term()
		while self._peek_kind() in ("+", "-"):
			operator = self._advance()[0]
			node = ("bin", operator, node, self._term())
		return node

	def _term(self) -> Node:
		node = self._factor()
		while self._peek_kind() in ("*", "/"):
			operator = self._advance()[0]
			node = ("bin", operator, node, self._factor())
		return node

	def _factor(self) -> Node:
		kind = self._peek_kind()
		if kind is None:
			self._fail()
		if kind == "-":
			self._advance()
			return ("neg", self._factor())
		if kind == "(":
			self._advance()
			node = self._expr()
			if self._peek_kind() != ")":
				self._fail()
			self._advance()
			return node
		if kind == "NUMBER":
			text = self._advance()[1]
			number = parse_number(text)
			if number is None:
				self._fail()
			return ("num", number)
		if kind == "CELL":
			return ("cell", self._advance()[1])
		self._fail()

	def _peek_kind(self) -> str | None:
		if self._at_end():
			return None
		return self._tokens[self._index][0]

	def _advance(self) -> tuple[str, str]:
		if self._at_end():
			self._fail()
		token = self._tokens[self._index]
		self._index += 1
		return token

	def _at_end(self) -> bool:
		return self._index >= len(self._tokens)

	def _fail(self) -> None:
		raise MalformedFormulaError(f"malformed formula: {self._source!r}")


def _evaluate(node: Node, get_value: Callable[[str], EvaluatedCellValue]) -> int | float:
	kind = node[0]
	if kind == "num":
		return node[1]
	if kind == "neg":
		return -_evaluate(node[1], get_value)
	if kind == "cell":
		return _number_from_cell(node[1], get_value)
	if kind == "bin":
		left = _evaluate(node[2], get_value)
		right = _evaluate(node[3], get_value)
		return _apply(node[1], left, right)
	raise MalformedFormulaError("malformed formula")


def _number_from_cell(cell_id: str, get_value: Callable[[str], EvaluatedCellValue]) -> int | float:
	value = get_value(cell_id)
	# Excel-style blank: an unset cell or a cell stored as "" contributes 0.
	# get_value itself still returns None or "" when that cell is read directly.
	if value is None or value == "":
		return 0
	if isinstance(value, bool) or not isinstance(value, (int, float)):
		raise NonNumericCellError(f"{cell_id} contains non-numeric text")
	return value


def _apply(operator: str, left: int | float, right: int | float) -> int | float:
	if operator == "+":
		return left + right
	if operator == "-":
		return left - right
	if operator == "*":
		return left * right
	if operator == "/":
		if right == 0:
			raise DivisionByZeroError("division by zero")
		# Two ints stay int when the quotient is whole; otherwise return a float.
		# 10/2 -> 5, 10/4 -> 2.5. A float operand keeps the result a float.
		if isinstance(left, int) and isinstance(right, int) and left % right == 0:
			return left // right
		return left / right
	raise MalformedFormulaError("malformed formula")
