# RiffScope Insights Pipeline

<a target="_blank" href="https://cookiecutter-data-science.drivendata.org/">
    <img src="https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter" />
</a>

<a target="_blank">
    <img src="https://img.shields.io/badge/Spotify-API-1DB954?logo=spotify&logoColor=white" />
</a>

<a target="_blank">
    <img src="https://img.shields.io/badge/Power%20BI-Dashboard-F2C811?logo=powerbi&logoColor=black" />
</a>

<a target="_blank">
    <img src="https://img.shields.io/badge/Power%20BI-Dashboard-F2C811?logo=powerbi&logoColor=black" />
</a>

<a target="_blank">
    <img src="https://img.shields.io/badge/Azure-Blob%20Storage-0078D4?logo=microsoftazure&logoColor=white" />
</a>




> **Is the alternative music revival driven by nostalgia, or by exhaustion with commercial music?**

RiffScope is an end-to-end data pipeline that collects, cleans, and statistically validates audio features from Spotify tracks across alternative and commercial genres — then visualizes the findings in Power BI.

---

## Research Question

> Do contemporary alternative music tracks exhibit emotional and sonic characteristics that differentiate them from dominant commercial music?

---

## Pipeline Architecture

```
Spotify API ──┐
              ├──▶ dataset.py ──▶ features.py ──▶ dataset_clean.csv ──▶ test.ipynb ──▶ Power BI
ReccoBeats ───┘      (ingest)      (clean)           (1,695 tracks)     (validate)     (report)
```

| Stage | File | Description |
|---|---|---|
| Ingestion | `riffscope/dataset.py` | Search tracks by genre on Spotify, fetch audio features from ReccoBeats API |
| Cleaning | `riffscope/features.py` | Deduplicate, parse dates, label groups, export clean CSV |
| Validation | `notebooks/test.ipynb` | Mann-Whitney U test + Cohen's d effect size per feature |
| Reporting | Power BI | Visual comparison of alternative vs. commercial audio profiles |

---

## Genre Taxonomy

| Group | Genres |
|---|---|
| `alternative` | rock, punk, metal, alternative, indie, hard-rock, grunge, garage-rock, shoegaze |
| `comercial` | pop, latin-pop, reggaeton, dance, trap, k-pop, hip-hop, corridos-tumbados, regional-mexican |

---

## Audio Features

Sourced from the **ReccoBeats API** — Spotify deprecated `audio_features` for individual developers in May 2025.

| Feature | Description |
|---|---|
| `valence` | Emotional positivity — high = happy, low = dark |
| `energy` | Intensity and activity level |
| `acousticness` | Degree of acoustic vs. produced sound |
| `danceability` | Suitability for dancing |

---

## Key Findings

Statistical validation across **1,695 tracks** confirmed all four features differ significantly between groups (p ≈ 0 for all):

| Feature | Cohen's d | Interpretation |
|---|---|---|
| `danceability` | -1.30 | **Large** — commercial music is significantly more danceable |
| `acousticness` | -0.39 | Small-medium — commercial scores higher |
| `valence` | -0.36 | Small-medium — commercial music is more emotionally positive |
| `energy` | +0.33 | Small-medium — alternative music is more intense |

Alternative music is more intense, emotionally darker, and less danceable — a statistically validated sonic identity, not just cultural perception.

---

## Tech Stack

- **Python 3.12** · pandas · scipy · numpy
- **Spotify Web API** — track search via Client Credentials flow
- **ReccoBeats API** — audio features in batches of up to 100 IDs
- **Typer** — CLI entrypoints per pipeline stage
- **loguru** — structured logging with tqdm integration
- **Azure Blob Storage** — cloud storage for processed data
- **Power BI** — visual analysis and reporting
- **Cookiecutter Data Science** — project structure

---

## Setup

**1. Clone and navigate to the project:**
```bash
git clone https://github.com/Axelbau/riffScope-insights-pipeline.git
cd riffScope-insights-pipeline/riffScope-insights-pipeline
```

**2. Install dependencies:**
```bash
make requirements
```

**3. Create a `.env` file with your Spotify credentials:**
```
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
SPOTIFY_REDIRECT_URI=your_redirect_uri
```

---

## Running the Pipeline

```bash
make data                     # ingest tracks from Spotify + ReccoBeats → data/raw/
python riffscope/features.py  # clean and export → data/processed/dataset_clean.csv
```

Then open `notebooks/test.ipynb` to run the statistical validation.
