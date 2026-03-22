import os
import sqlite3
from itertools import combinations
from collections import Counter

import numpy as np
import pandas as pd

import matplotlib

# Avoid blocking on plt.show() in environments without a GUI.
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

# Configuration
DB_PATH = "spotify_database.db"
PLOTS_DIR = "plots_part4"

sns.set(style="whitegrid")


def connect_db():
    return sqlite3.connect(DB_PATH)


def _ensure_plots_dir():
    os.makedirs(PLOTS_DIR, exist_ok=True)


def _save_fig(filename: str):
    _ensure_plots_dir()
    path = os.path.join(PLOTS_DIR, filename)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def categorize_era(dt):
    """Return era label like '70s', '80s', ..."""
    if pd.isna(dt):
        return "Unknown"
    dt = pd.to_datetime(dt, errors="coerce")
    if pd.isna(dt):
        return "Unknown"
    year = int(dt.year)
    decade = (year // 10) * 10
    return f"{decade}s"


def parse_genres_from_artist_row(row: pd.Series):
    """
    Extract genres as a list of normalized strings.
    Schema (from your DB):
      - artist_genres (string)
      - genre_0..genre_6 (columns)
    """
    genres = []

    # Prefer structured genre columns.
    for i in range(0, 7):
        c = f"genre_{i}"
        if c in row.index:
            v = row.get(c, None)
            if pd.notna(v):
                sv = str(v).strip()
                if sv:
                    genres.append(sv.lower())

    # Fallback to artist_genres if available.
    if not genres and "artist_genres" in row.index:
        v = row.get("artist_genres", None)
        if pd.notna(v):
            s = str(v).strip()
            # Common formats: "['rock', 'pop']" or "rock, pop"
            s = s.replace("[", "").replace("]", "").replace("'", "")
            parts = [p.strip().lower() for p in s.split(",") if p.strip()]
            genres.extend(parts)

    # Unique while preserving order.
    seen = set()
    out = []
    for g in genres:
        if g not in seen:
            seen.add(g)
            out.append(g)
    return out


def detect_and_clean_tracks_outliers():
    """
    Part 4 bullets:
    - Remove invalid records (missing IDs, negative duration)
    - Detect outliers and address them properly (winsorize/cap)
    Writes cleaned tables:
      - tracks_data_clean
      - albums_data_clean
      - features_data_clean
    """
    conn = connect_db()

    tracks = pd.read_sql_query("SELECT * FROM tracks_data", conn)
    albums = pd.read_sql_query("SELECT * FROM albums_data", conn)
    features = pd.read_sql_query("SELECT * FROM features_data", conn)

    # 1) Remove invalid IDs and negative durations.
    tracks_clean = tracks.dropna(subset=["id"]).copy()
    tracks_clean["track_popularity"] = pd.to_numeric(
        tracks_clean.get("track_popularity", np.nan), errors="coerce"
    )

    albums_clean = albums.dropna(subset=["track_id"]).copy()
    albums_clean["duration_ms"] = pd.to_numeric(
        albums_clean.get("duration_ms", np.nan), errors="coerce"
    )
    albums_clean = albums_clean[albums_clean["duration_ms"] > 0].copy()

    features_clean = features.dropna(subset=["id"]).copy()

    # Keep only rows that can be joined (avoid downstream empty merges).
    track_ids = set(tracks_clean["id"].dropna().unique())
    albums_clean = albums_clean[albums_clean["track_id"].isin(track_ids)].copy()
    feature_ids = set(features_clean["id"].dropna().unique())
    albums_clean = albums_clean[albums_clean["track_id"].isin(feature_ids)].copy()

    # 2) Detect outliers and address them:
    # - Cap popularity outliers using IQR.
    s = tracks_clean["track_popularity"].dropna()
    if not s.empty:
        q1 = s.quantile(0.25)
        q3 = s.quantile(0.75)
        iqr = q3 - q1
        low = q1 - 1.5 * iqr
        high = q3 + 1.5 * iqr
        tracks_clean["track_popularity"] = tracks_clean["track_popularity"].clip(low, high)

    # - Cap common audio features outliers using IQR.
    candidate_feature_cols = [
        "danceability",
        "energy",
        "loudness",
        "speechiness",
        "acousticness",
        "valence",
        "tempo",
        "instrumentalness",
        "liveness",
    ]
    for col in candidate_feature_cols:
        if col not in features_clean.columns:
            continue
        features_clean[col] = pd.to_numeric(features_clean[col], errors="coerce")
        s = features_clean[col].dropna()
        if s.empty:
            continue
        q1 = s.quantile(0.25)
        q3 = s.quantile(0.75)
        iqr = q3 - q1
        low = q1 - 1.5 * iqr
        high = q3 + 1.5 * iqr
        features_clean[col] = features_clean[col].clip(low, high)

    tracks_clean.to_sql("tracks_data_clean", conn, if_exists="replace", index=False)
    albums_clean.to_sql("albums_data_clean", conn, if_exists="replace", index=False)
    features_clean.to_sql("features_data_clean", conn, if_exists="replace", index=False)

    conn.close()


def resolve_artist_duplicates_and_capitalization():
    """
    Part 4 bullet: resolve duplicates (ambiguous names + capitalization).
    We create:
      - artist_data_clean (canonical id per normalized name)
      - update albums_data_clean.artist_id to canonical ids
    """
    conn = connect_db()
    artists = pd.read_sql_query("SELECT * FROM artist_data", conn)
    if artists.empty:
        conn.close()
        return

    artists["name_low"] = artists["name"].astype(str).str.lower().str.strip()
    artists["followers_num"] = pd.to_numeric(
        artists.get("followers", np.nan), errors="coerce"
    ).fillna(-1)

    idx = artists.groupby("name_low")["followers_num"].idxmax()
    canonical_ids = artists.loc[idx, ["id", "name_low"]].set_index("name_low")["id"].to_dict()
    artists["canonical_id"] = artists["name_low"].map(canonical_ids)

    canonical_rows = []
    for canonical_id, group in artists.groupby("canonical_id"):
        rep = group.sort_values(
            ["followers_num", "artist_popularity", "id"], ascending=False
        ).iloc[0]

        # Union genres across duplicates.
        genre_union = []
        for _, r in group.iterrows():
            genre_union.extend(parse_genres_from_artist_row(r))

        seen = set()
        genre_union_unique = []
        for g in genre_union:
            if g not in seen:
                seen.add(g)
                genre_union_unique.append(g)

        genre_cols = {f"genre_{i}": None for i in range(0, 7)}
        for i in range(0, min(7, len(genre_union_unique))):
            genre_cols[f"genre_{i}"] = genre_union_unique[i]

        canonical_rows.append(
            {
                "id": canonical_id,
                "name": str(rep["name"]).strip(),
                "artist_popularity": rep.get("artist_popularity", None),
                "followers": rep.get("followers", None),
                "artist_genres": str(genre_union_unique),
                **genre_cols,
            }
        )

    artist_clean = pd.DataFrame(canonical_rows)
    artist_clean.to_sql("artist_data_clean", conn, if_exists="replace", index=False)

    albums_clean = pd.read_sql_query("SELECT * FROM albums_data_clean", conn)
    mapping = artists.set_index("id")["canonical_id"].to_dict()
    albums_clean["artist_id"] = albums_clean["artist_id"].map(mapping)
    albums_clean.to_sql("albums_data_clean", conn, if_exists="replace", index=False)

    conn.close()


def add_era_to_albums_clean():
    """Part 4 bullet: group by era added to albums_data."""
    conn = connect_db()
    albums_clean = pd.read_sql_query("SELECT * FROM albums_data_clean", conn)
    albums_clean["release_date"] = pd.to_datetime(
        albums_clean["release_date"], errors="coerce"
    )
    albums_clean["era"] = albums_clean["release_date"].apply(categorize_era)
    albums_clean.to_sql(
        "albums_data_clean_with_era", conn, if_exists="replace", index=False
    )
    conn.close()


def analyze_trends_over_time():
    """
    Part 4 bullet: trend of features over time by averaging over songs released on a date.
    Returns a merged dataframe (features joined with release_date).
    """
    conn = connect_db()
    albums = pd.read_sql_query(
        "SELECT track_id, release_date FROM albums_data_clean_with_era", conn
    )
    features = pd.read_sql_query("SELECT * FROM features_data_clean", conn)
    conn.close()

    merged = albums.merge(features, left_on="track_id", right_on="id", how="inner")
    merged["release_date"] = pd.to_datetime(merged["release_date"], errors="coerce")
    merged = merged.dropna(subset=["release_date"])

    audio_cols = [c for c in ["danceability", "energy", "loudness", "valence", "tempo"] if c in merged.columns]
    daily_avg = merged.groupby("release_date")[audio_cols].mean().reset_index()
    print("\nSample daily feature averages:")
    print(daily_avg.head())
    return merged


def get_album_summary(album_name):
    """
    Part 4 bullet: summary of album feature scores.
    """
    conn = connect_db()
    query = """
        SELECT
            f.danceability, f.energy, f.loudness, f.speechiness,
            f.acousticness, f.valence, f.tempo
        FROM albums_data_clean_with_era a
        JOIN features_data_clean f ON a.track_id = f.id
        WHERE lower(a.album_name) = lower(?)
    """
    df = pd.read_sql_query(query, conn, params=[album_name])
    conn.close()

    if df.empty:
        return f"No data found for album: {album_name}"

    return df.describe().T[["mean", "std", "min", "max"]]


def plot_features_by_era(merged_df):
    """
    Part 4 bullet: group features by era and create barplots.
    """
    conn = connect_db()
    era_lookup = pd.read_sql_query(
        "SELECT track_id, era FROM albums_data_clean_with_era", conn
    )
    conn.close()

    df = merged_df.merge(era_lookup, on="track_id", how="left")
    df = df.dropna(subset=["era"])

    features = [c for c in ["danceability", "energy", "loudness", "valence", "tempo"] if c in df.columns]
    era_avg = df.groupby("era")[features].mean().reset_index()

    n = len(features)
    fig, axes = plt.subplots(1, n, figsize=(5 * n, 5), squeeze=False)
    for i, col in enumerate(features):
        ax = axes[0, i]
        sns.barplot(data=era_avg, x="era", y=col, ax=ax, color="#1DB954")
        ax.set_xlabel("Era")
        ax.set_ylabel(col)
        ax.set_title(f"Avg {col.capitalize()} by Era")
        ax.tick_params(axis="x", rotation=45)

    _ensure_plots_dir()
    out_path = os.path.join(PLOTS_DIR, "features_by_era.png")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def plot_monthly_popularity_as_streams_proxy(top_n_tracks: int = 20):
    """
    Part 4 bullet: aggregate popularity and streams by month for songs with most total streams.
    Your DB schema has no 'streams' column; we use 'track_popularity' as a proxy.
    """
    conn = connect_db()
    albums = pd.read_sql_query(
        "SELECT track_id, release_date FROM albums_data_clean_with_era", conn
    )
    tracks = pd.read_sql_query(
        "SELECT id, track_popularity FROM tracks_data_clean", conn
    )
    conn.close()

    df = albums.merge(tracks, left_on="track_id", right_on="id", how="inner")
    df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")
    df = df.dropna(subset=["release_date", "track_popularity"])
    df["month"] = df["release_date"].dt.to_period("M").astype(str)

    track_totals = df.groupby("track_id")["track_popularity"].sum()
    top_track_ids = track_totals.nlargest(top_n_tracks).index.tolist()
    df_top = df[df["track_id"].isin(top_track_ids)].copy()

    monthly = df_top.groupby("month")["track_popularity"].sum().reset_index()
    if monthly.empty:
        print("No monthly data found for top tracks.")
        return

    plt.figure(figsize=(12, 4))
    sns.lineplot(data=monthly, x="month", y="track_popularity", marker="o")
    plt.xticks(rotation=90)
    plt.title(f"Monthly Streams Proxy (track_popularity) for Top {top_n_tracks} Tracks")
    plt.xlabel("Month")
    plt.ylabel("Total Streams Proxy")
    _save_fig("monthly_streams_proxy_top_tracks.png")


def analyze_genre_pairs():
    """
    Part 4 bullet: identify genres that appear together most frequently.
    We treat the (primary) artist genres as the track's genre list.
    """
    conn = connect_db()
    query = """
        SELECT al.track_id,
               ar.artist_genres,
               ar.genre_0, ar.genre_1, ar.genre_2, ar.genre_3, ar.genre_4, ar.genre_5, ar.genre_6
        FROM albums_data_clean_with_era al
        JOIN artist_data_clean ar ON al.artist_id = ar.id
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    genre_pairs = []
    for _, row in df.iterrows():
        genres = parse_genres_from_artist_row(row)
        if len(genres) >= 2:
            genre_pairs.extend(list(combinations(sorted(set(genres)), 2)))

    if not genre_pairs:
        print("No genre pairs found.")
        return

    top_pairs = Counter(genre_pairs).most_common(10)
    print("\nMost frequent genre co-occurrence pairs (top 10):")
    print(top_pairs)


def label_and_identify_genres(feature: str = "energy", q: int = 5):
    """
    Part 4 bullet: label tracks by feature intensity and identify frequent genres
    among very low and very high tracks.
    """
    conn = connect_db()
    query = f"""
        SELECT f.{feature} AS feature_value,
               ar.genre_0, ar.genre_1, ar.genre_2, ar.genre_3, ar.genre_4, ar.genre_5, ar.genre_6,
               ar.artist_genres
        FROM features_data_clean f
        JOIN albums_data_clean_with_era al ON f.id = al.track_id
        JOIN artist_data_clean ar ON al.artist_id = ar.id
        WHERE f.{feature} IS NOT NULL
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    if df.empty:
        print(f"No data available to label feature '{feature}'.")
        return

    df["feature_value"] = pd.to_numeric(df["feature_value"], errors="coerce")
    df = df.dropna(subset=["feature_value"])

    labels = ["very low", "low", "medium", "high", "very high"] if q == 5 else None
    if labels is None:
        raise ValueError("This script currently supports q=5 for 'very low'..'very high'.")

    df["intensity"] = pd.qcut(
        df["feature_value"],
        q=q,
        labels=labels,
        duplicates="drop",
    )

    for target_label in ["very low", "very high"]:
        subset = df[df["intensity"] == target_label]
        if subset.empty:
            print(f"No tracks found in intensity '{target_label}' for feature '{feature}'.")
            continue

        genre_counter = Counter()
        for _, row in subset.iterrows():
            for g in parse_genres_from_artist_row(row):
                genre_counter[g] += 1

        top_genres = genre_counter.most_common(10)
        print(f"\nTop genres for feature '{feature}' in '{target_label}' (top 10):")
        print(top_genres)


if __name__ == "__main__":
    detect_and_clean_tracks_outliers()
    resolve_artist_duplicates_and_capitalization()
    add_era_to_albums_clean()

    merged = analyze_trends_over_time()
    print("\nAlbum feature summary (example):")
    print(get_album_summary("Yours Truly"))

    plot_features_by_era(merged)
    plot_monthly_popularity_as_streams_proxy(top_n_tracks=20)
    analyze_genre_pairs()
    label_and_identify_genres("danceability")