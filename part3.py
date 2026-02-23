import sqlite3
import pandas as pd
from datetime import datetime

# connect to the SQLite database
conn = sqlite3.connect('spotify_database.db')

# inspect table names and columns
print("Tables in database:")
df_tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table'", conn)
print(df_tables, "\n")

for table in df_tables['name']:
    cols = pd.read_sql_query(f"PRAGMA table_info({table});", conn)
    print(f"Columns in {table}:")
    print(cols[['name','type']])
    print()

# Task 1: choose an interesting feature
feature = 'danceability'

# compute the threshold for the top 10% of tracks on this feature
count_query = f"SELECT COUNT(*) FROM features_data"
total_tracks = conn.execute(count_query).fetchone()[0]
print(f"Total tracks in features_data: {total_tracks}")
top_n = max(1, total_tracks // 10)
print(f"Selecting top {top_n} tracks ({top_n/total_tracks:.1%}) based on '{feature}'\n")

# get the top track ids for that feature
top_ids_query = (
    f"SELECT id, {feature} FROM features_data "
    f"ORDER BY {feature} DESC LIMIT {top_n}"
)
top_features = pd.read_sql_query(top_ids_query, conn)

# join with tracks_data and albums_data to add artist information
join_query = (
    "SELECT f.id as track_id, f." + feature + ", "
    "t.track_popularity, t.explicit, a.artist_0, a.artist_1, a.artist_2, a.artist_3 "
    "FROM features_data f "
    "JOIN tracks_data t ON f.id = t.id "
    "JOIN albums_data a ON f.id = a.track_id "
    f"WHERE f.id IN ({','.join('?' for _ in range(len(top_features)))})"
)

params = list(top_features['id'])
joined = pd.read_sql_query(join_query, conn, params=params)

# which artists appear most in this set?
# we'll count appearances in any of the artist columns
artist_cols = [c for c in joined.columns if c.startswith('artist_')]

artists_long = (
    joined[artist_cols]
    .apply(lambda row: [x for x in row.values if x], axis=1)
    .explode()
    .reset_index(drop=True)
    .dropna()
    .astype(str)
)

artist_counts = artists_long.value_counts().rename_axis('artist').reset_index(name='count')

print("Top artists among the 10% highest-danceability tracks:")
print(artist_counts.head(20))

print("\nArtists that stand out (highest counts):")
print(artist_counts.head(5))

# Task 2: divide time window in eras such as 70s, 80s, 90s, etc.
# load albums_data into DataFrame to work with release_date
albums = pd.read_sql_query("SELECT * FROM albums_data", conn)

# parse release_date into datetime (pandas is more forgiving)
albums['parsed_date'] = pd.to_datetime(albums['release_date'], errors='coerce', utc=True)

# helper to map year to era after parsing

def year_to_era(ts):
    if pd.isna(ts):
        return None
    year = ts.year
    decade = (year // 10) * 10
    return f"{decade}s"

albums['era'] = albums['parsed_date'].apply(year_to_era)

print("\nSample of albums_data with new 'era' column:")
print(albums[['release_date','era']].drop_duplicates().head(10))

# Optionally, write the updated albums table back into the database or to a csv
# Here we create a new table so as not to modify the original
albums.to_sql('albums_with_era', conn, if_exists='replace', index=False)
print("\nCreated new table 'albums_with_era' in the database with era information.")

conn.close()
