# zapinit

Start a WhatsApp conversation with any phone number — no need to save the contact first.

Enter a phone number, select the country, click **Open on WhatsApp**, and you're redirected straight to a chat in WhatsApp Web.

## Stack

- **Backend:** FastAPI + Jinja2
- **Frontend:** Tailwind CSS + intl-tel-input
- **Language:** Python 3.11+

## Running locally

```bash
# 1. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows

# 2. Install dependencies
pip install -r requirements-dev.txt

# 3. Start the dev server
uvicorn app.main:app --reload
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

The `--reload` flag restarts the server automatically on every file change.

## Debugging in VS Code

A `launch.json` is included with two configurations:

| Configuration | What it does |
|---|---|
| **zapinit: run** | Starts the FastAPI server with the VS Code debugger attached — breakpoints in Python files work |
| **zapinit: test** | Runs the full test suite under the debugger — breakpoints inside test step definitions work |

**Requirements:**
- Install the [Python extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python) for VS Code
- Select the `.venv` interpreter: `Ctrl+Shift+P` → `Python: Select Interpreter` → choose `./.venv/bin/python`

To start debugging: open the **Run and Debug** panel (`Ctrl+Shift+D`), pick a configuration, press **F5**.

## Running tests

```bash
# Run the full test suite
pytest

# Run with verbose output
pytest -v

# Run a specific feature
pytest tests/step_defs/test_main_page.py -v

# Run linting
ruff check .

# Run linting + auto-fix
ruff check . --fix
```

Tests are written using [pytest-bdd](https://pytest-bdd.readthedocs.io/) with Gherkin feature files in `tests/features/` and step definitions in `tests/step_defs/`.

## License

MIT
