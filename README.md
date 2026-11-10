# Spreadsheet

Small example of a sheet that stores cell values.

## Layout

- `src/spreadsheet_project/` holds `Cell` and `Sheet`
- `utils/` holds cell-id checks and error types
- `test/` holds tests

## Run the tests

From the repository root:

```bash
python3 -m unittest discover -s test -v
```

The standard-library `unittest` runner is enough. No extra packages are required. `test/test_sheet_happy_path.py` sets a literal, reads it back, and evaluates a one-cell addition formula. On the current source those two tests are expected failures.
