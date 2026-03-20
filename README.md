# Spotify Data Analysis — Group Project

A data engineering and analysis project using a Spotify dataset.

---

## Project Structure

| File | Description |
|------|-------------|
| `Part 1.py` | Part 1 — Artist analysis using `artist_data.csv` (popularity, followers, genres, regression model) |
| `Part 3.py` | Part 3 — Database exploration (album feature consistency, top-10% filtering, correlations, eras, explicit & collaborations) |
| `part4.py` | Part 4 — Data wrangling (cleaning, outliers, trends over time, era grouping, monthly trends, genres, feature labeling) |
| `Part 5` / `part5.py` | Part 5 — Streamlit dashboard (Home, Feature/Genre analysis, Artist Analysis, Artist Search, Compare Artists) |
| `spotify_database.db` | Local SQLite database containing all Spotify data |
| `artist_data.csv` | CSV source file used by Part 1 |

---

## Parts Overview

### Part 1 — Artist Analysis (`Part 1`)
Reads from `artist_data.csv` and performs:
- Column inspection and data type overview
- Counting unique artists
- Top 10 artists by popularity and by followers (with bar charts)
- Correlation between popularity and log(followers)
- OLS regression model: predicts popularity from followers
- Identifies overperformers (more popular than predicted) and legacy artists (less popular than predicted)
- Genre filtering: top 10 artists per genre
- Genre count analysis: correlation between number of genres and popularity/followers

### Part 3 — Database Exploration (`Part 3.py`)
- Inspects all tables and their columns
- Identifies the top 10% of tracks by danceability
- Finds which artists appear most frequently among high-danceability tracks
- Classifies albums into music eras (70s, 80s, 90s, etc.) based on release date
- Creates a new `albums_with_era` table in the database
- Compares average popularity of explicit vs. non-explicit tracks
- Finds the artist(s) with the highest proportion of explicit tracks

### Part 4 — Data Wrangling (`part4.py`)
- Removes invalid records (missing IDs, non-positive duration)
- Detects and addresses outliers (IQR-based capping)
- Computes feature trends over time and summarizes album features
- Resolves artist name duplicates (canonicalization) and adds `era`
- Aggregates popularity over months (uses `track_popularity` as proxy for streams)
- Finds frequent genre co-occurrence pairs
- Labels tracks into `very low/low/medium/high/very high` and reports frequent genres

### Part 5 — Interactive Dashboard (`part5.py`)
A Streamlit web application with four pages:

- **Home** — Dataset overview with key metrics and audio feature distributions
- **Feature Analysis** — Explore any audio feature: distribution histogram, correlation with popularity, top artists
- **Artist Analysis** — Most popular and most prolific artists with popularity distribution
- **Artist Search** — Search for an artist (top 200) to see their audio profile and track statistics

---

## Requirements

Install dependencies with:

```bash
pip install pandas numpy matplotlib seaborn statsmodels streamlit
```

---

## Running the Dashboard

```bash
streamlit run part5.py
```

Then open your browser at `http://localhost:8501`.

---

## Running the Analysis Scripts

```bash
python "Part 1.py"
python part3.py
python part4.py
```
