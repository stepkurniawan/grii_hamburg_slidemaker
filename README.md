# GRII Hamburg Slide Maker

Streamlit app and helper utilities for generating church service PowerPoint slides for GRII/MRII Europe. The app builds the Sunday service deck from song slide images, Bible passages, preacher details, Holy Communion options, offering slides, and Google Drive announcement images.

## Quick links
- Web app entry: [`main.py`](main.py) -> runs [`grii_slide_maker.app.create_website`](grii_slide_maker/app.py)
- Slide generation and layouts: [`grii_slide_maker/slides/creator.py`](grii_slide_maker/slides/creator.py)
- Announcement slides: [`grii_slide_maker/slides/announcements.py`](grii_slide_maker/slides/announcements.py)
- Song download pipeline: [`grii_slide_maker.songs.drive.download_new_song_pipeline`](grii_slide_maker/songs/drive.py)
- Google Drive helpers: [`grii_slide_maker.services.google_drive`](grii_slide_maker/services/google_drive.py)
- ESV wrapper: [`grii_slide_maker.services.esv_service.EsvService`](grii_slide_maker/services/esv_service.py)
- Service input models: [`grii_slide_maker/models`](grii_slide_maker/models)
- App settings and secrets: [`grii_slide_maker.config.Settings`](grii_slide_maker/config.py)
- Dockerfile: [`Dockerfile`](Dockerfile)
- Agent guidance: [`AGENTS.md`](AGENTS.md)

## Requirements / Prerequisites
- Python >= 3.13
- uv, used by Docker and CI
- Streamlit

Note: this project no longer uses Poetry.

## Install (local dev)
1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install uv and sync dependencies:

```bash
pip install uv
uv sync --frozen --no-install-project --no-dev
```

Alternatively, install from `requirements.txt`:

```bash
pip install -r requirements.txt
```

3. Provide secrets:
- Place service account / Drive credentials into Streamlit secrets (`.streamlit/secrets.toml`) or use external `token.json` / `credentials.json` as needed.
- Set `ESV_BIBLE_API_KEY` for ESV passage lookup.
- Set `GOOGLE_DRIVE_SONG_MASTER_FOLDER_ID`, `ANNOUCEMENT_FOLDER_ID`, and `GOOGLE_DRIVE_OUTPUT_FOLDER_ID` for Drive folder lookup.
- Optional settings include `ESV_TEXT_API_URL` and `ESV_HTML_API_URL`. See [`grii_slide_maker.config.Settings`](grii_slide_maker/config.py).

## Run (development)
Start the Streamlit app:

```bash
streamlit run main.py
```

The Streamlit app is built in [`grii_slide_maker.app.create_website`](grii_slide_maker/app.py).

## Docker
Build and run:

```bash
docker build -t stepkurniawan/slidemaker:latest .
docker run -p 8502:8502 stepkurniawan/slidemaker:latest
```

The Dockerfile uses uv to sync dependencies and runs:

```bash
streamlit run /app/main.py --server.port=8502 --server.address=0.0.0.0
```

You can also use [`docker-compose.yml`](docker-compose.yml), which maps port `8502` and mounts `.streamlit` secrets read-only.

## Testing & Lint
- Tests: pytest
- Lint: Ruff via pre-commit

Examples:

```bash
uv sync --all-groups
uv run pytest
uvx pre-commit run --all-files
```

To run Ruff directly:

```bash
uvx ruff check --fix .
```

## Versioning
The app version has one source of truth: `project.version` in [`pyproject.toml`](pyproject.toml). The Streamlit UI reads that value and displays it in the page header.

To bump the patch version:

```bash
uv version --bump patch
```

You can also bump a minor or major version:

```bash
uv version --bump minor
uv version --bump major
```

## Notes
- Slides, templates, and output handling are in [`grii_slide_maker/slides/creator.py`](grii_slide_maker/slides/creator.py) and [`grii_slide_maker/app.py`](grii_slide_maker/app.py).
- To change the slide template, edit `master_slide_template_en.pptx`.
- Announcement images are read from a Google Drive folder id defined in settings and inserted via [`grii_slide_maker.slides.announcements.insert_annoucement_slides`](grii_slide_maker/slides/announcements.py).
- Keep private credentials out of the repo. `.gitignore` includes Streamlit secrets, token files, credentials files, JSON secrets, specs, logs, build output, and Python caches.

## Contributing
- Follow existing style and tests.
- CI lives in [`.github/workflows/docker_pipeline.yml`](.github/workflows/docker_pipeline.yml). On pushes to `main`, it installs dependencies with `uv sync --all-groups`, runs `uv run pytest`, then builds and pushes the Docker image.
- Add tests for new functionality where applicable.
