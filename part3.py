import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

DB_PATH = "spotify_database.db"

def connect_db():
    """Connect to the SQLite database and set row_factory for name-based access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# --- 1. ALBUM FEATURE INVESTIGATION ---
# Requirement: Pick an album and investigate if features like danceability are consistent [cite: 58, 59]
def analyze_album_consistency(album_name="The Divine Feminine"):
    conn = connect_db()
    query = """
    SELECT a.track_name, f.danceability, f.loudness
    FROM albums_data a
    JOIN features_data f ON a.track_id = f.id
    WHERE a.album_name = ?
    ORDER BY a.track_number ASC
    """
    df = pd.read_sql_query(query, conn, params=(album_name,))
    
    print(f"\n--- Consistency Analysis for Album: {album_name} ---")
    # Using describe() to see standard deviation and range for consistency [cite: 59]
    print(df.describe())
    
    # Visualizing feature trends across tracks
    df.set_index('track_name')[['danceability', 'loudness']].plot(kind='line', marker='o', subplots=True)
    plt.tight_layout()
    plt.show()
    conn.close()

# --- 2. TOP 10% FEATURE FILTERING ---
# Requirement: Filter top 10% tracks on a feature and identify top artists [cite: 60, 61]
def top_10_percent_analysis(feature='danceability'):
    conn = connect_db()
    # Calculate the 10% threshold dynamically [cite: 60]
    total_count = conn.execute("SELECT COUNT(*) FROM features_data").fetchone()[0]
    top_n = total_count // 10
    
    query = f"""
    SELECT a.artist_0, a.artist_1, a.artist_2, a.artist_3
    FROM features_data f
    JOIN albums_data a ON f.id = a.track_id
    ORDER BY f.{feature} DESC LIMIT {top_n}
    """
    df = pd.read_sql_query(query, conn)
    
    # Flattening multi-column artists into a single series to count occurrences [cite: 61]
    artists_series = df.melt()['value'].dropna()
    print(f"\n--- Top Artists in the Top 10% for {feature} ---")
    print(artists_series.value_counts().head(10))
    conn.close()

# --- 3. ALBUM VS ARTIST POPULARITY ---
# Requirement: Investigate relationship between album and artist popularity [cite: 62]
def album_artist_correlation():
    conn = connect_db()
    query = """
    SELECT a.album_popularity, ar.artist_popularity
    FROM albums_data a
    JOIN artist_data ar ON a.artist_id = ar.id
    WHERE a.album_popularity IS NOT NULL AND ar.artist_popularity IS NOT NULL
    """
    df = pd.read_sql_query(query, conn)
    correlation = df.corr().iloc[0, 1]
    
    print(f"\n--- Correlation Analysis ---")
    print(f"Correlation coefficient: {correlation:.3f}")
    
    # Scatter plot to visualize the relationship [cite: 62]
    plt.scatter(df['artist_popularity'], df['album_popularity'], alpha=0.5, color='forestgreen')
    plt.title(f"Album vs Artist Popularity (Corr: {correlation:.3f})")
    plt.xlabel("Artist Popularity")
    plt.ylabel("Album Popularity")
    plt.show()
    conn.close()

# --- 4. TIME WINDOWS (ERAS) ---
# Requirement: Divide time in eras (70s, 80s, etc.) and add column to albums_data [cite: 63, 64]
def categorize_eras():
    conn = connect_db()
    albums = pd.read_sql_query("SELECT * FROM albums_data", conn)
    # Using datetime for robust year extraction [cite: 64]
    albums['release_date_dt'] = pd.to_datetime(albums['release_date'], errors='coerce')
    
    def get_era(dt):
        if pd.isna(dt): return "Unknown"
        return f"{(dt.year // 10) * 10}s"
    
    albums['era'] = albums['release_date_dt'].apply(get_era)
    # Updating the database with the new information [cite: 63]
    # The assignment asks to add the column to `albums_data`, so we overwrite the table
    # with the same columns plus `era`.
    if 'release_date_dt' in albums.columns:
        albums = albums.drop(columns=['release_date_dt'])
    albums.to_sql('albums_data', conn, if_exists='replace', index=False)
    print("\n--- Column 'era' added to table 'albums_data' ---")
    conn.close()

# --- 5 & 6. EXPLICIT CONTENT ANALYSIS ---
# Requirement: Are explicit tracks more popular? Which artists have the highest proportion? [cite: 65, 66]
def analyze_explicit_content():
    conn = connect_db()
    
    # Task 5: Average popularity comparison [cite: 65]
    pop_query = "SELECT explicit, AVG(track_popularity) as avg_popularity FROM tracks_data GROUP BY explicit"
    print("\n--- Explicit vs Non-Explicit Popularity ---")
    print(pd.read_sql_query(pop_query, conn))
    
    # Task 6: Proportion per artist (multiplying by 1.0 to avoid integer division) [cite: 66]
    prop_query = """
    SELECT ar.name, 
           SUM(CASE WHEN t.explicit = 'true' THEN 1 ELSE 0 END) * 1.0 / COUNT(t.id) as explicit_ratio
    FROM artist_data ar
    JOIN albums_data al ON ar.id = al.artist_id
    JOIN tracks_data t ON al.track_id = t.id
    GROUP BY ar.id
    HAVING COUNT(t.id) > 5
    ORDER BY explicit_ratio DESC
    LIMIT 10
    """
    print("\n--- Artists with Highest Proportion of Explicit Tracks ---")
    print(pd.read_sql_query(prop_query, conn))
    conn.close()

# --- 7. COLLABORATION ANALYSIS ---
# Requirement: Are collaborations more popular? Add column and investigate 
def analyze_collaborations():
    conn = connect_db()
    # Identifying collaborations based on the presence of multiple artists 
    query = """
    SELECT t.track_popularity, 
           CASE WHEN (a.artist_1 IS NOT NULL AND a.artist_1 != '') THEN 'Collab' ELSE 'Solo' END as collab_status
    FROM tracks_data t
    JOIN albums_data a ON t.id = a.track_id
    """
    df = pd.read_sql_query(query, conn)
    
    # Statistical comparison
    summary = df.groupby('collab_status')['track_popularity'].mean()
    print("\n--- Collaboration Popularity Analysis ---")
    print(summary)
    
    # Visualization 
    df.boxplot(column='track_popularity', by='collab_status')
    plt.title("Popularity Comparison: Solo vs Collaboration")
    plt.suptitle("") # Clear automatic title
    plt.show()
    conn.close()

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    analyze_album_consistency("The Divine Feminine")
    top_10_percent_analysis('danceability')
    album_artist_correlation()
    categorize_eras()
    analyze_explicit_content()
    analyze_collaborations()
