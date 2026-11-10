# Spreadsheet

Small example of a sheet that stores cell values and evaluates a simple formula when a cell is read.

## Formulas

A value that starts with `=` must be exactly one operation:

`=<operand> <op> <operand>`

An operand is an integer, a decimal, a number with a leading minus, or a cell id such as `A1` or `A34`. The operator is one of `+`, `-`, `*`, or `/`. Spaces around the operator are allowed.

`=A1+A34`, `=A1*2.3`, `=3-B2`, and `=10/4` are valid. A formula that is only one operand (`=A1`, `=5`) or that chains operators (`=A1+B1*2`) is invalid and raises `InvalidFormulaError`. Parentheses are not supported.

Each cell reference is read with `get_value`. A cell that was never set, or that stores an empty string, counts as `0` inside a formula. Reading that cell directly still returns `None` or `""`. Other non-numeric text raises `NonNumericCellError`. Division by zero raises `DivisionByZeroError`. A formula that depends on its own cell raises `CircularReferenceError`.

Integer text stays an `int` (`1`, `=1+2` is `3`). Division returns a `float` (`=10/4` is `2.5`).

Results are computed on each read, so changing `A1` changes the next read of a formula that uses `A1`.

## Run the tests

From the repository root:

```bash
PYTHONPATH=src python3 -m unittest discover -s test -v
```
