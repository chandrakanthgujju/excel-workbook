# Spreadsheet

Small example of a sheet that stores cell values and evaluates formulas when they are read.

## Values

`set_value` stores text. `get_value` returns:

- an `int` when the text is an integer, such as `1` or `-3`
- a `float` when the text is a non-integer number, such as `1.5`
- the formula result when the text starts with `=`
- the original text for anything else
- `None` when the cell was never set

## Formulas

A value that starts with `=` is a formula. The rest of the text supports:

- numbers: digits with an optional decimal part (`2`, `10.5`) and an optional unary minus (`-3`)
- cell references such as `A1` (one or more letters `A`–`Z`, then a row starting at 1)
- the operators `+`, `-`, `*`, and `/`
- parentheses

`*` and `/` bind before `+` and `-`. Operators at the same level group to the left, so `8-3-2` is `(8-3)-2`. Unary minus applies to the next factor, so `-3+5` is `(-3)+5`.

Formulas are not passed to `eval`. Evaluation has three steps:

1. A regex tokenizer splits the text into numbers, cell references, operators, and parentheses.
2. A recursive-descent parser matches `expr -> term -> factor` and builds a small tree. A formula that does not match this grammar raises `MalformedFormulaError`.
3. A walk of that tree computes the value. Each cell reference calls `Sheet.get_value`, so a formula can depend on numbers or on other formulas.

The raw text stays on the cell. Every read computes the result again, so changing `A1` changes the next read of a formula that uses `A1`.

### Integers and floats

`+`, `-`, and `*` follow the operand types: two ints produce an int, and a float operand produces a float. `/` returns an int when both operands are ints and the quotient is a whole number (`10/2` is `5`). Otherwise `/` returns a float (`10/4` is `2.5`).

### Blank cells in a formula

A reference to a cell that was never set (`get_value` returns `None`) or that stores an empty string is treated as `0`. Reading that cell on its own still returns `None` or `""`. Any other non-numeric text, such as `hello`, raises `NonNumericCellError` when a formula uses the cell.

### Errors

- `InvalidCellIdError` — a cell id, or a reference written in a formula, does not match the `A1` pattern (`A0`, `1A`)
- `MalformedFormulaError` — the formula text does not match the grammar (`=1+`, `=*2`, `=A1+`, `=1 2`)
- `DivisionByZeroError` — a divisor is zero
- `CircularReferenceError` — a formula depends on its own cell, directly (`=A1` in `A1`) or through other cells (`A1` reads `B1` and `B1` reads `A1`)
- `NonNumericCellError` — a referenced cell contains text that is not a number

## Run the tests

From the repository root:

```bash
PYTHONPATH=src python3 -m unittest discover -s test -v
```
