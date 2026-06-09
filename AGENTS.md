# Repository Guidelines

## Project Structure & Module Organization

This repository is currently an early-stage educational Python project for a 2026 World Cup betting pool (`bolao`) built with Streamlit. Keep source code in a future `src/` or `app/` directory, with the main Streamlit entry point named clearly, for example `app.py` or `src/app.py`. Store tests in `tests/` using the same module names as the code under test. Keep design references and static images in `picture/`; `picture/captura.png` is the current UI reference. Project notes live in `.llm/escopo.md`. Agent skills are installed under `.agents/` and should not be mixed with application code.

## Build, Test, and Development Commands

No application commands are defined yet. When code is added, prefer a minimal Python workflow:

- `python -m venv .venv` creates a local virtual environment.
- `source .venv/bin/activate` activates it on Linux/macOS.
- `pip install -r requirements.txt` installs dependencies once `requirements.txt` exists.
- `streamlit run app.py` runs the local app; update the path if the entry point is placed under `src/`.
- `pytest` runs the test suite once tests are present.

Document any new command in this file when adding tooling.

## Coding Style & Naming Conventions

Use Python 3 with 4-space indentation. Prefer simple, readable functions because this is an educational project. Use `snake_case` for modules, functions, variables, and database fields. Use `PascalCase` only for classes. Keep Streamlit page code thin; move validation, group selection logic, and database access into separate modules when they grow beyond a few functions. Avoid committing generated files, caches, logs, or local virtual environments; `.gitignore` already covers common Python, Node, and build artifacts.

## Testing Guidelines

Use `pytest` for Python tests. Name test files `test_<module>.py` and test functions `test_<behavior>()`. Prioritize tests for form validation, group ranking rules, random third-place selection, and database persistence. Keep randomness deterministic in tests by injecting a seed or random generator.

## Commit & Pull Request Guidelines

There is no commit history yet, so use concise imperative commit messages such as `Add Streamlit entry point` or `Implement group selection validation`. Pull requests should include a short description, affected screens or modules, test results, and screenshots when UI changes are made.

## Security & Configuration Tips

Do not commit database credentials, API keys, phone numbers, emails, or participant data. Store secrets in Streamlit secrets or environment variables, and provide a sanitized example config when needed.
