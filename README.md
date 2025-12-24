# grii-europe-slide-maker

Lightweight Streamlit app and utilities to generate bilingual (English / Indonesian / German) church slides (PowerPoint) using in-memory images from Google Drive and Bible passages from ESV/BibleSuperSearch.

## Quick links
- Web app entry: [`entry_point.py`](entry_point.py) → runs [`main.create_website`](main.py)  
- Slide generation & layouts: [`pptx_creator.py`](pptx_creator.py)  
- Song download + Drive helpers: [`Pujian.download_new_song_pipeline`](Pujian.py) / [`Pujian.save_images_from_google_folder_to_memory`](Pujian.py)  
- ESV wrapper: [`services.esv_service.EsvService`](services/esv_service.py)  
- App settings (env/secrets): [`settings.Settings`](settings.py)  
- Dockerfile: [Dockerfile](Dockerfile)  
- PyInstaller CLI: [pyinstaller_command.txt](pyinstaller_command.txt)

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
- Place service account / Drive credentials into Streamlit secrets (`.streamlit/secrets.toml`) or use `token.json` / `credentials.json` as needed. See [`settings.Settings`](settings.py).

## Run (development)
Start the Streamlit app:
```bash
streamlit run entry_point.py
```
The Streamlit app is built in [`main.create_website`](main.py).

## Docker
Build and run (example):
```bash
docker build -t stepkurniawan/slidemaker:latest .
docker run -p 8000:8000 stepkurniawan/slidemaker:latest
```
The Dockerfile uses uv to sync dependencies and runs:
`streamlit run /app/entry_point.py`.

## Build standalone executable
A PyInstaller command is provided in [pyinstaller_command.txt](pyinstaller_command.txt).

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
- Slides, templates and output handling are in [`pptx_creator.py`](pptx_creator.py) and [`main.py`](main.py).
- Announcement images are read from a Google Drive folder id defined in settings and inserted via [`annoucement.insert_annoucement_slides`](annoucement.py).
- Keep private credentials out of the repo — `.gitignore` includes token and credentials files.

## Contributing
- Follow existing style and tests (see `.github/workflows/python-app.yml` for CI).
- Add tests for new functionality where applicable.
