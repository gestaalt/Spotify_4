import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

DB_PATH = "spotify_database.db"

# Investigating the database #

def connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  
    return conn

def list_tables(conn: sqlite3.Connection) -> list[str]:
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    return [r["name"] for r in cur.fetchall()]

def list_columns(conn: sqlite3.Connection, table: str) -> list[tuple]:
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table});")

# Getting information about the table columns #

    return [(r["name"], r["type"], r["pk"]) for r in cur.fetchall()]

def main():
    conn = connect(DB_PATH)

    print("Tables:")
    tables = list_tables(conn)
    for t in tables:
        print(" -", t)

    print("\nColumns per table:")
    for t in tables:
        cols = list_columns(conn, t)
        print(f"\n{t}:")
        for name, coltype, pk in cols:
            pk_flag = " (PK)" if pk else ""
            print(f"  - {name} : {coltype}{pk_flag}")

    conn.close()

if __name__ == "__main__":
    main()

# Analysing album features of The Divine Feminine; an album by Mac Miller #

ALBUM_NAME = "The Divine Feminine"  

def connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def fetch_album_tracks_with_features(conn: sqlite3.Connection, album_name: str) -> pd.DataFrame:
    sql = """
    SELECT
        a.album_name AS album_name,
        a.track_name AS track_name,
        f.danceability,
        f.loudness
    FROM albums_data a
    JOIN features_data f
        ON a.track_id = f.id
    WHERE a.album_name = ?
    ORDER BY a.track_number ASC
    """
    return pd.read_sql_query(sql, conn, params=(album_name,))

def summarize_consistency(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    summary = []
    for c in cols:
        s = df[c].dropna()
        summary.append({
            "feature": c,
            "count": int(s.shape[0]),
            "mean": float(s.mean()) if len(s) else None,
            "std": float(s.std(ddof=1)) if len(s) > 1 else 0.0,
            "min": float(s.min()) if len(s) else None,
            "max": float(s.max()) if len(s) else None,
            "range": float(s.max() - s.min()) if len(s) else None
        })
    return pd.DataFrame(summary)

def main():
    conn = connect(DB_PATH)
    
    try:
        df = fetch_album_tracks_with_features(conn, ALBUM_NAME)

# Print track features and summary #

        print("\nTracks and their features:")
        print(df[["track_name", "danceability", "loudness"]].to_string(index=False))

        summary = summarize_consistency(df, ["danceability", "loudness"])
        print("\nConsistency summary (lower std/range = more consistent):")
        print(summary.to_string(index=False))

# Interpretation of the album features #

        dance_range = summary.loc[summary["feature"] == "danceability", "range"].iloc[0]
        loud_range = summary.loc[summary["feature"] == "loudness", "range"].iloc[0]
        print("\nQuick interpretation:")
        print(f"- Danceability range: {dance_range:.3f} -> {'consistent-ish' if dance_range < 0.15 else 'varies'}")
        print(f"- Loudness range: {loud_range:.3f} dB -> {'consistent-ish' if loud_range < 3.0 else 'varies'}")

# Plot for daceability of album #

        plt.figure()
        plt.plot(df["danceability"].values, marker="o", color = "lightpink")
        plt.title(f"Danceability across tracks: {ALBUM_NAME}")
        plt.xlabel("Track index")
        plt.ylabel("Danceability")
        plt.show()

# Plot for loudness of album #

        plt.figure()
        plt.plot(df["loudness"].values, marker="o", color = "pink")
        plt.title(f"Loudness across tracks: {ALBUM_NAME}")
        plt.xlabel("Track index")
        plt.ylabel("Loudness (dB)")
        plt.show()

    finally:
        conn.close()

if __name__ == "__main__":
    main()

def connect(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def fetch_popularity_data(conn):
    """
    Get album popularity and artist popularity using SQL joins
    """

    sql = """
    SELECT
        a.album_name AS album_name,
        ar.name AS artist_name,
        a.album_popularity AS album_popularity,
        ar.artist_popularity AS artist_popularity
    FROM albums_data a
    JOIN artist_data ar
        ON a.artist_id = ar.id
    WHERE a.album_popularity IS NOT NULL
    AND ar.artist_popularity IS NOT NULL
    """
    df = pd.read_sql_query(sql, conn)
    return df


def analyze_relationship(df):
    
    print("\nSample Data:")
    print(df.head())
    print("\nNumber of albums analysed:", len(df))


# Correlation calculation #

    correlation = df["album_popularity"].corr(df["artist_popularity"])

    print("\nCorrelation between album popularity and artist popularity:")
    print(round(correlation, 3))

 # Interpretation of the correlation #

    print("\nInterpretation:")

    if correlation > 0.7:
        print("There is a strong positive relationship.")
        print("Popular artists tend to have popular albums.")

    elif correlation > 0.4:
        print("There is a moderate positive relationship.")
        print("More popular artists often have more popular albums.")

    elif correlation > 0.2:
        print("There is a weak positive relationship.")

    else:
        print("There is little or no relationship detected.")

def main():

    conn = connect(DB_PATH)
    df = fetch_popularity_data(conn)
    analyze_relationship(df)

# Visualization #

    plt.figure(figsize=(8,6))
    plt.scatter(df["artist_popularity"], df["album_popularity"], alpha=0.6, color = "forestgreen")
    plt.xlabel("Artist Popularity")
    plt.ylabel("Album Popularity")
    plt.title("Relationship between Album and Artist Popularity")
    plt.grid(True)
    plt.show()

    conn.close()

if __name__ == "__main__":
    main()
