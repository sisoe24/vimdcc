# Contributing

## Getting Started

1. Fork the repository on GitHub
2. Clone the forked repository to your local machine
3. Create a new branch for your feature

## Development

The project uses [uv](https://docs.astral.sh/uv/).

```bash
uv sync           # PySide6, Python 3.11 (from .python-version)
uv run pytest
uv run vimdcc     # local test window, reads sample.txt from the repo root
```

To test against PySide2 (Nuke 15 and older), use Python 3.10 in a separate venv.
PySide2 has no Apple Silicon wheels, so on an M-series Mac use an x86_64 Python:

```bash
UV_PROJECT_ENVIRONMENT=.venv-pyside2 uv run -p cpython-3.10-macos-x86_64 pytest
```
