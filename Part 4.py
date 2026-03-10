import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def outliers_popularity():
    conn = sqlite3.connect('spotify_database.db')
    df = pd.read_sql_query("SELECT id, name, artist_popularity, followers FROM artist_data", conn)
    conn.close()

    Q1 = df['artist_popularity'].quantile(0.25)
    Q3 = df['artist_popularity'].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR

    outliers = df[(df['artist_popularity'] < lower) | (df['artist_popularity'] > upper)]

    print("Outlier artist:\n" , outliers[['name', 'artist_popularity', 'followers']].to_string(index=False))
    return outliers




def outliers_features():
    conn = sqlite3.connect('spotify_database.db')
    df = pd.read_sql_query("""SELECT danceability, energy, loudness,
                            speechiness, acousticness, instrumentalness, liveness, 
                            valence, tempo FROM features_data""", conn)
    conn.close()
    cols = df.columns.tolist()

    for x in cols:
        Q1 = df[x].quantile(0.25)
        Q3 = df[x].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR

        outliers = df[(df[x] < lower) | (df[x] > upper)]
        if len(outliers) > 0:
            print(f"{x}: {len(outliers)} outliers")

        #Adress outliers by transforming the data
        df_clean = df[df[x] > 0].copy()
        df_clean[x] = np.log(df_clean[x])

def outliers_track_data():
    conn = sqlite3.connect('spotify_database.db')
    df = pd.read_sql_query("SELECT track_popularity FROM tracks_data", conn)
    conn.close()

    Q1 = df['track_popularity'].quantile(0.25)
    Q3 = df['track_popularity'].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR

    outliers = df[(df['track_popularity'] < lower) | (df['track_popularity'] > upper)]

    print(f"Track popularity: {len(outliers)} outliers")
    return outliers



outliers_popularity()
outliers_features()
outliers_track_data()