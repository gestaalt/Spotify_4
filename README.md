# Spotify Data Analysis — Group Project

A data engineering and analysis project using a Spotify dataset.

---

## Project Structure

| File | Description |
|------|-------------|
| `Part 1` | Part 1 — Artist analysis using CSV data (popularity, followers, genres, regression model) |
| `part3.py` | Part 3 — Database inspection and exploratory analysis (top danceability tracks, era classification) |
| `Part 3.py` | Part 3 — Explicit content analysis (popularity comparison and artist ratios) |
| `Part 4.py` | Part 4 — Outlier detection for artist popularity, audio features, and track popularity |
| `part5.py` | Part 5 — Interactive Streamlit dashboard for exploring artists, tracks, and audio features |
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

### Part 3 — Exploratory Analysis (`part3.py`)
- Inspects all tables and their columns
- Identifies the top 10% of tracks by danceability
- Finds which artists appear most frequently among high-danceability tracks
- Classifies albums into music eras (70s, 80s, 90s, etc.) based on release date
- Creates a new `albums_with_era` table in the database

### Part 3 — Explicit Content Analysis (`Part 3.py`)
- Compares average popularity of explicit vs. non-explicit tracks
- Finds the artist(s) with the highest proportion of explicit tracks

### Part 4 — Outlier Detection (`Part 4.py`)
- Detects outlier artists by popularity using the IQR method
- Detects outliers in all audio features and applies log transformation to clean the data
- Detects outliers in track popularity scores

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
pip install pandas numpy matplotlib seaborn statsmodels streamlit sqlite3
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
python "Part 1"
python part3.py
python "Part 3.py"
python "Part 4.py"
```
