# Spotify Data Analysis
> A data engineering and analysis project that explores a Spotify dataset across five parts — from statistical modelling and data cleaning to an interactive multi-page dashboard.

---

## What does this project do?

This project analyses a Spotify music dataset to uncover patterns in artist popularity, audio features, genres, and musical eras. It progresses from raw data exploration to a fully interactive Streamlit dashboard where you can search artists, compare audio profiles, and explore genres.

---

## Quick Start

### 1. Install dependencies

```bash
pip install pandas numpy matplotlib seaborn statsmodels streamlit
```

> `sqlite3` is part of Python's standard library — no installation needed.

### 2. Run the dashboard

```bash
streamlit run "Part 5.py"
```

Then open your browser at **http://localhost:8501**

### 3. Run individual analysis scripts

```bash
python "Part 1.py"   # Artist analysis
python "Part 3.py"   # Explicit content analysis
python part4.py      # Data cleaning & outlier detection
```

---

## Dashboard Pages

The Streamlit dashboard (`Part 5.py`) has **6 pages**:

| Page | Description |
|------|-------------|
| **Home** | Dataset overview with key metrics and audio feature distributions |
| **Feature Analysis** | Explore any audio feature: distribution, correlation with popularity, top artists |
| **Artist Analysis** | Most popular and most prolific artists with popularity distribution |
| **Artist Search** | Search the top 200 artists to view their full audio profile |
| **Compare Artists** | Side-by-side comparison of two artists across all metrics |
| **Genre Explorer** | Browse genres and view popularity-per-follower rankings |

---

## Project Structure

```
Spotifiy_4/
├── Part 1.py              # Artist analysis (CSV)
├── Part 3.py              # Explicit content analysis (database)
├── part4.py               # Outlier detection & data cleaning
├── Part 5.py              # Interactive Streamlit dashboard
├── spotify_database.db    # SQLite database (artists, albums, tracks, features)
└── artist_data.csv        # Artist metadata source for Part 1
```