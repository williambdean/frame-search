test:
	uv run pytest --cov src/frame_search

docs:
	uv run marimo export html-wasm docs.py -o docs/index.html --mode edit
