# Frame Search

Frame Search is a Python library that adds a GitHub search inspired interface to DataFrames. It provides a `.search()` method that works with both pandas and polars DataFrames using GitHub-style query syntax.

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Working Effectively

### Bootstrap and Setup
- Install uv package manager: `pip install uv` (takes ~10 seconds)
- Sync all dependencies: `uv sync --locked --all-extras --dev` (takes <1 second on subsequent runs, ~8 seconds on first run)
- Verify installation: `uv --version`

### Testing
- Run all tests: `uv run pytest tests/` (takes ~4 seconds, 46 tests with 97% coverage)
- Run tests with make: `make test` (takes ~2 seconds)
- Tests include both pandas and polars DataFrame functionality
- All tests should pass - if they don't, the issue is likely with your environment setup

### Linting and Code Quality
- Check code style: `uv run ruff check .` (takes <1 second)
- Check formatting: `uv run ruff format --check .` (takes <1 second)
- Fix formatting: `uv run ruff format .` (takes <1 second)
- Pre-commit hooks are configured but may fail due to network timeouts - use ruff commands directly

### Building
- Build package: `uv build` (takes <1 second)
- Creates dist/frame_search-0.1.0.tar.gz and dist/frame_search-0.1.0-py3-none-any.whl

## Validation

### Manual Testing
Always test functionality manually after making changes:
```python
# Basic functionality test
import frame_search
import polars as pl

df = pl.DataFrame({
    "name": ["Alice Smith", "Bob J. Dawkins", "Charlie Brown"],
    "age": [25, 30, 35],
    "hometown": ["New York", "New York", "Chicago"]
})

# Test search functionality
result = df.search('age:<30 hometown:"New York"')
# Should return 1 row: Alice Smith, 25, New York

# Test with pandas
import pandas as pd
df_pd = pd.DataFrame(df.to_pandas())
result_pd = df_pd.search('age:<30 hometown:"New York"')
# Should return same result
```

### CI Validation
- Always run `uv run ruff check .` and `uv run ruff format --check .` before committing
- The GitHub Actions workflow (.github/workflows/tests.yml) only runs tests, not linting
- Tests run on Python 3.9, 3.10, 3.11, 3.12, and 3.13

### Performance Expectations
- Dependency installation: <1 second (subsequent), ~8 seconds (first time)
- Test suite: ~4 seconds (46 tests)
- Linting: <1 second
- Formatting check: <1 second
- Build: <1 second

## Common Tasks

### Repository Structure
```
.
├── .github/
│   ├── workflows/
│   │   ├── tests.yml           # CI tests on multiple Python versions
│   │   ├── publish.yml         # PyPI publishing on tags
│   │   └── ...
│   └── copilot-instructions.md # This file
├── src/frame_search/
│   ├── __init__.py            # Main imports and conditional pandas/polars loading
│   ├── search.py              # Core search functionality and query parsing
│   ├── extension.py           # DataFrame extension base class
│   ├── pandas.py              # Pandas-specific search extension
│   └── polars.py              # Polars-specific search extension
├── tests/
│   ├── test_search.py         # Core search functionality tests
│   ├── test_pandas.py         # Pandas-specific tests
│   ├── test_polars.py         # Polars-specific tests
│   └── conftest.py            # Test configuration
├── pyproject.toml             # Project configuration and dependencies
├── Makefile                   # Simple test command
├── .pre-commit-config.yaml    # Pre-commit hooks (ruff check/format)
└── README.md                  # Usage examples and documentation
```

### Key Files to Check When Making Changes
- `src/frame_search/search.py` - Core search logic and query parsing
- `src/frame_search/pandas.py` - Pandas DataFrame extension
- `src/frame_search/polars.py` - Polars DataFrame extension
- `tests/test_search.py` - Add tests here for new search functionality
- `pyproject.toml` - Dependencies and project configuration

### Search Query Syntax
The library supports GitHub-style search queries:
- `name:alice` - Search for "alice" in name column
- `age:>30` - Numeric comparisons (>, <, >=, <=)
- `age:30..35` - Range queries
- `hometown:"New York"` - Quoted strings for exact matches
- `alice age:>30` - Multiple terms (AND logic)
- Case-insensitive text search by default

### Troubleshooting
- If `uv` is not available: `pip install uv`
- If pre-commit fails with network timeouts: Use `uv run ruff check .` and `uv run ruff format .` directly
- If tests fail: Check that both pandas and polars are installed via `uv sync --locked --all-extras --dev`
- If import errors occur: The library conditionally imports pandas/polars, ensure they're in dev dependencies

### Development Workflow
1. Make changes to source code
2. Run `uv run ruff format .` to format code
3. Run `uv run ruff check .` to check for issues
4. Run `uv run pytest tests/` to test functionality
5. Test manually with the validation script above
6. The library automatically extends pandas/polars DataFrames when imported
