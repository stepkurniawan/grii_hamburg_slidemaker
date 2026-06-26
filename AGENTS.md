# AI Agent Guidance

## Purpose
This repository is a Python-based Streamlit app plus helper utilities for generating bilingual church service PowerPoint slides.

## Key files
- `main.py` - Streamlit entry wrapper.
- `grii_slide_maker/app.py` - Streamlit app and website flow. Use this when updating the app UI or any request flow.
- `grii_slide_maker/slides/creator.py` - slide generation logic and PowerPoint layout helpers.
- `grii_slide_maker/slides/announcements.py` - Google Drive announcement slide insertion.
- `grii_slide_maker/songs/drive.py` - song download and Drive-related helpers.
- `grii_slide_maker/services/esv_service.py` - ESV Bible API wrapper.
- `grii_slide_maker/config.py` - application settings and secret management.
- `README.md` - install, run, Docker, and test instructions.

## Environment and commands
- Python version: `>=3.13`
- Local dev install:
  - `python -m venv .venv`
  - `source .venv/bin/activate`
  - `pip install -r requirements.txt`
  - or use `uv sync --frozen --no-install-project --no-dev`
- Run app locally:
  - `streamlit run main.py`
- Tests:
  - `pytest`
- Lint:
  - `flake8 .`

## CI and build notes
- GitHub Actions workflow: `.github/workflows/docker_pipeline.yml`
- CI uses Python 3.13 and runs:
  - `uv sync --all-groups`
  - `uv run pytest`
- Docker build uses the repository root and runs `streamlit run /app/main.py`.

## Project-specific guidance
- The app is built around Streamlit and in-memory slide/image handling; avoid design changes that require persistent storage unless the feature explicitly adds it.
- Secrets and service account credentials should not be committed. Use `.streamlit/secrets.toml` or external `token.json` / `credentials.json` as described in `README.md`.
- Keep new behavior covered by tests in `tests/` and use existing test patterns found under `tests/` and `tests/models/`.
- When modifying import paths or app entry points, note the repository has both `pyproject.toml` and `requirements.txt`, and the Docker workflow is tied to `uv`.

## Useful links
- Repository README: `README.md`
- Dockerfile: `Dockerfile`
