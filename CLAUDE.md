# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project purpose

**RiffScope** investigates whether the alternative music revival is driven by nostalgia or by exhaustion with commercial music's pursuit of perfection and political correctness.

The goal is to explore how the human, imperfect, and emotionally complex could become the next cultural trend — particularly within alternative music revival — by comparing audio features between alternative and commercial genres using Spotify data.

**Research question:** ¿El revival de la música alternativa es nostalgia o una respuesta al agotamiento de la música comercial?

## Genre taxonomy

| Group | Genres |
|---|---|
| `alternative` | rock, punk, metal, alternative, indie, hard rock |
| `comercial` | pop, latin pop, reggaeton, dance |

Target: **500–1000 tracks per genre** for analysis.

## Key metrics (Spotify audio features)

| Field | Description |
|---|---|
| `valence` | Emotional attitude of the song (positive vs. negative) |
| `energy` | Intensity |
| `acousticness` | Acoustic vs. produced sound |
| `danceability` | How suitable for dancing |
| `popularity` | Spotify popularity score |
| `release_date_precision` | Release time granularity |
| `name` | Track name |
| `id` | Spotify track ID |

## Tech stack

Python 3.12 · Cookiecutter · Spotify API · GCP · Power BI · GitHub

## Project layout

The repo has a nested structure: the actual project lives inside `riffScope-insights-pipeline/` (a subdirectory of the repo root). All commands below should be run from that inner directory.

```
riffScope-insights-pipeline/   ← run commands from here
├── riffscope/                 ← Python package (source code)
│   ├── config.py              ← path constants and logger setup
│   ├── dataset.py             ← Spotify data ingestion (Typer CLI)
│   ├── features.py            ← feature engineering (Typer CLI)
│   ├── plots.py               ← visualization (Typer CLI)
│   └── modeling/
│       ├── train.py           ← model training (Typer CLI)
│       └── predict.py         ← model inference (Typer CLI)
├── data/{raw,interim,processed,external}/
├── models/
├── reports/figures/
└── .env                       ← SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI
```

## Environment setup

Requires `.env` in `riffScope-insights-pipeline/` with:
```
SPOTIFY_CLIENT_ID=...
SPOTIFY_CLIENT_SECRET=...
SPOTIFY_REDIRECT_URI=...
```

`config.py` loads this via `python-dotenv` on import. The Spotify connector in `dataset.py` is initialized at module level using these env vars.

## Common commands

All run from `riffScope-insights-pipeline/`:

```bash
make requirements        # install deps
make data                # run dataset.py ingestion
make lint                # ruff format --check && ruff check
make format              # ruff check --fix && ruff format
make clean               # remove .pyc files and __pycache__
make sync_data_down      # gsutil rsync from gs://riffscope-raw/data/
make sync_data_up        # gsutil rsync to gs://riffscope-raw/data/
```

Run individual pipeline stages directly:
```bash
python riffscope/dataset.py
python riffscope/features.py
python riffscope/modeling/train.py
python riffscope/modeling/predict.py
python riffscope/plots.py
```

## Architecture

Each pipeline stage (`dataset.py`, `features.py`, `modeling/train.py`, `modeling/predict.py`, `plots.py`) is an independent Typer CLI app with a `main()` entry point. They read/write files using path constants from `config.py` (`RAW_DATA_DIR`, `PROCESSED_DATA_DIR`, `MODELS_DIR`, `FIGURES_DIR`), all derived from `PROJ_ROOT = Path(__file__).parents[1]`.

Logging uses `loguru` throughout, configured in `config.py` to write via `tqdm.write` so progress bars and log lines don't interleave.

The genre taxonomy in `dataset.py` maps two groups (`"alternative"`, `"comercial"`) to Spotify genre search terms. The Spotify client uses Client Credentials flow (no user auth).

## Linter / formatter

`ruff` with line length 99, import sorting enabled (`extend-select = ["I"]`). Run `make format` before committing.
\
