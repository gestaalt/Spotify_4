import sqlite3
import pandas as pd

# connect to the SQLite database
def explicit_popularity():
    conn = sqlite3.connect('spotify_database.db')
    cur = conn.cursor()
    cur.execute("SELECT AVG(track_popularity) FROM tracks_data WHERE explicit = 'true'")
    avg_true = cur.fetchone()[0]
    cur.execute("SELECT AVG(track_popularity) FROM tracks_data WHERE explicit = 'false'")
    avg_false = cur.fetchone()[0]
    conn.close()
    if avg_true> avg_false:
        return "On average explicit tracks are more popular"
    else:
        return "On average non-explicit tracks are more popular"



def highest_proportion():
    conn = sqlite3.connect('spotify_database.db')
    cur = conn.cursor()
    cur.execute("""SELECT artist_data.id, artist_data.name, 
                COUNT(tracks_data.id) FILTER (WHERE tracks_data.explicit = 'true') / COUNT(tracks_data.id) AS explicit_ratio
                FROM artist_data
                JOIN albums_data ON artist_data.id=albums_data.artist_id
                JOIN tracks_data ON albums_data.track_id=tracks_data.id
                GROUP BY artist_data.id
                HAVING explicit_ratio = (
                    SELECT MAX(sub_ratio) FROM (
                        SELECT COUNT(tracks_data.id) FILTER (WHERE tracks_data.explicit = 'true') / COUNT(tracks_data.id) AS sub_ratio
                        FROM artist_data
                        JOIN albums_data ON artist_data.id=albums_data.artist_id
                        JOIN tracks_data ON albums_data.track_id=tracks_data.id
                        GROUP BY artist_data.id
                        )
                    )
                """)
    results = cur.fetchall()
    conn.close()
    return [name for _, name, _ in results]

print(explicit_popularity())
print(highest_proportion())

