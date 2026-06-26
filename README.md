# grii-europe-slide-maker

Lightweight Streamlit app and utilities to generate bilingual (English / Indonesian / German) church slides (PowerPoint) using in-memory images from Google Drive and Bible passages from ESV/BibleSuperSearch.

## Quick links
- Web app entry: [`main.py`](main.py) → runs [`grii_slide_maker.app.create_website`](grii_slide_maker/app.py)  
- Slide generation & layouts: [`grii_slide_maker/slides/creator.py`](grii_slide_maker/slides/creator.py)  
- Song download + Drive helpers: [`grii_slide_maker.songs.drive.download_new_song_pipeline`](grii_slide_maker/songs/drive.py) / [`grii_slide_maker.songs.drive.save_images_from_google_folder_to_memory`](grii_slide_maker/songs/drive.py)  
- ESV wrapper: [`grii_slide_maker.services.esv_service.EsvService`](grii_slide_maker/services/esv_service.py)  
- App settings (env/secrets): [`grii_slide_maker.config.Settings`](grii_slide_maker/config.py)  
- Dockerfile: [Dockerfile](Dockerfile)  

## Requirements / Prerequisites
- Python >= 3.13
- uv (used to manage install sync as in the Dockerfile)
- Streamlit

Note: This project no longer uses Poetry.

## Install (local dev)
1. Create & activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install uv and sync dependencies (mirrors the Dockerfile):
```bash
pip install uv
uv sync --frozen --no-install-project --no-dev
```

Alternatively, you can install via pip:
```bash
pip install -r requirements.txt
```

3. Provide secrets:
- Place service account / Drive credentials into Streamlit secrets (`.streamlit/secrets.toml`) or use `token.json` / `credentials.json` as needed. See [`grii_slide_maker.config.Settings`](grii_slide_maker/config.py).

## Run (development)
Start the Streamlit app:
```bash
streamlit run main.py
```
The Streamlit app is built in [`grii_slide_maker.app.create_website`](grii_slide_maker/app.py).

## Docker
Build and run (example):
```bash
docker build -t stepkurniawan/slidemaker:latest .
docker run -p 8000:8000 stepkurniawan/slidemaker:latest
```
The Dockerfile uses uv to sync dependencies and runs:
`streamlit run /app/main.py`.

## Testing & Lint
- Lint: flake8
- Tests: pytest

Example:
```bash
pip install flake8 pytest
flake8 .
pytest
```

## Notes
- Slides, templates and output handling are in [`grii_slide_maker/slides/creator.py`](grii_slide_maker/slides/creator.py) and [`grii_slide_maker/app.py`](grii_slide_maker/app.py).
- To change the slide template, edit `master_slide_template_en.pptx`.
- Announcement images are read from a Google Drive folder id defined in settings and inserted via [`grii_slide_maker.slides.announcements.insert_annoucement_slides`](grii_slide_maker/slides/announcements.py).
- Keep private credentials out of the repo — `.gitignore` includes token and credentials files.

## Contributing
- Follow existing style and tests (see `.github/workflows/python-app.yml` for CI).
- Add tests for new functionality where applicable.
