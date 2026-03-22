import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Spotify Analytics", layout="wide")

# db connection
@st.cache_resource
def get_db():
    return sqlite3.connect('spotify_database.db', check_same_thread=False)

@st.cache_data(show_spinner=False)
def get_artists():
    conn = get_db()
    query = """
    SELECT
        artist_0 as name,
        AVG(album_popularity) as artist_popularity,
        COUNT(DISTINCT album_name) as album_count
    FROM albums_data
    WHERE artist_0 IS NOT NULL AND artist_0 != ''
    GROUP BY artist_0
    """
    return pd.read_sql_query(query, conn)

@st.cache_data(show_spinner=False)
def get_all_feature_data():
    conn = get_db()
    query = """
    SELECT f.danceability, f.energy, f.valence, f.acousticness,
           f.loudness, f.tempo, f.speechiness,
           t.track_popularity, a.artist_0, a.release_date
    FROM features_data f
    JOIN tracks_data t ON f.id = t.id
    JOIN albums_data a ON f.id = a.track_id
    WHERE a.release_date IS NOT NULL
    LIMIT 3000
    """
    return pd.read_sql_query(query, conn)

@st.cache_data(show_spinner=False)
def get_year_bounds():
    conn = get_db()
    years_df = pd.read_sql_query(
        "SELECT DISTINCT release_date FROM albums_data WHERE release_date IS NOT NULL LIMIT 2000",
        conn
    )
    years_df['year'] = pd.to_datetime(years_df['release_date'], errors='coerce').dt.year
    years = years_df['year'].dropna().astype(int)
    return int(years.min()), int(years.max())

@st.cache_data(show_spinner=False)
def get_yearly_trend_data():
    conn = get_db()
    query = """
    SELECT
        f.danceability,
        f.energy,
        f.valence,
        f.acousticness,
        f.loudness,
        f.tempo,
        f.speechiness,
        t.track_popularity,
        a.release_date
    FROM features_data f
    JOIN tracks_data t ON f.id = t.id
    JOIN albums_data a ON f.id = a.track_id
    WHERE a.release_date IS NOT NULL
    LIMIT 5000
    """
    df = pd.read_sql_query(query, conn)
    df['year'] = pd.to_datetime(df['release_date'], errors='coerce').dt.year
    df = df.dropna(subset=['year'])
    df['year'] = df['year'].astype(int)
    return df

SPOTIFY_GREEN = '#1DB954'
SPOTIFY_GREEN_LIGHT = '#1ED760'
DARK_GREY = '#535353'
LIGHT_GREY = '#B3B3B3'
ALMOST_BLACK = '#191414'

st.sidebar.header("Navigation")
current_page = st.sidebar.radio("Select Page",
    ["Home", "Feature Analysis", "Artist Analysis", "Artist Search", "Compare Artists", "Genre Explorer"])

# home page
if current_page == "Home":
    st.title("Spotify Dataset Analysis")
    st.write("Analysis of Spotify music data including artists, albums, tracks, and audio features")

    db = get_db()
    artists_df = get_artists()
    albums_df = pd.read_sql_query("SELECT album_name, album_popularity FROM albums_data LIMIT 3000", db)
    total_tracks = pd.read_sql_query("SELECT COUNT(*) as count FROM tracks_data", db).iloc[0]['count']
    features_df = pd.read_sql_query(
        "SELECT danceability, energy, valence, acousticness, loudness, tempo FROM features_data LIMIT 3000",
        db
    )

    st.subheader("Dataset Overview")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Artists", f"{len(artists_df):,}")
    c2.metric("Unique Albums", f"{albums_df['album_name'].nunique():,}")
    c3.metric("Total Tracks", f"{total_tracks:,}")
    c4.metric("Avg Artist Popularity", f"{artists_df['artist_popularity'].mean():.1f}")

    st.markdown("---")

    st.subheader("Audio Feature Distribution")
    fig, axes = plt.subplots(2, 2, figsize=(14, 8))
    feature_list = ['danceability', 'energy', 'valence', 'acousticness']
    chart_colors = [SPOTIFY_GREEN, SPOTIFY_GREEN_LIGHT, DARK_GREY, LIGHT_GREY]

    for i, feature_name in enumerate(feature_list):
        row = i // 2
        col = i % 2
        axes[row, col].hist(features_df[feature_name], bins=30,
                           color=chart_colors[i], edgecolor=ALMOST_BLACK, alpha=0.8)
        axes[row, col].set_title(f'{feature_name.capitalize()} Distribution',
                                fontsize=11, weight='bold')
        axes[row, col].set_xlabel(feature_name.capitalize())
        axes[row, col].set_ylabel('Frequency')
        axes[row, col].grid(axis='y', alpha=0.3, color=DARK_GREY)

    plt.tight_layout()
    st.pyplot(fig)

    st.subheader("Statistical Summary")
    stats = {
        'Feature': ['Artist Popularity', 'Album Popularity', 'Danceability', 'Energy',
                    'Valence', 'Acousticness', 'Loudness', 'Tempo'],
        'Mean': [
            f"{artists_df['artist_popularity'].mean():.2f}",
            f"{albums_df['album_popularity'].mean():.2f}",
            f"{features_df['danceability'].mean():.3f}",
            f"{features_df['energy'].mean():.3f}",
            f"{features_df['valence'].mean():.3f}",
            f"{features_df['acousticness'].mean():.3f}",
            f"{features_df['loudness'].mean():.2f}",
            f"{features_df['tempo'].mean():.2f}"
        ],
        'Median': [
            f"{artists_df['artist_popularity'].median():.2f}",
            f"{albums_df['album_popularity'].median():.2f}",
            f"{features_df['danceability'].median():.3f}",
            f"{features_df['energy'].median():.3f}",
            f"{features_df['valence'].median():.3f}",
            f"{features_df['acousticness'].median():.3f}",
            f"{features_df['loudness'].median():.2f}",
            f"{features_df['tempo'].median():.2f}"
        ],
        'Std Dev': [
            f"{artists_df['artist_popularity'].std():.2f}",
            f"{albums_df['album_popularity'].std():.2f}",
            f"{features_df['danceability'].std():.3f}",
            f"{features_df['energy'].std():.3f}",
            f"{features_df['valence'].std():.3f}",
            f"{features_df['acousticness'].std():.3f}",
            f"{features_df['loudness'].std():.2f}",
            f"{features_df['tempo'].std():.2f}"
        ]
    }
    st.dataframe(pd.DataFrame(stats), use_container_width=True)

# feature analysis page
elif current_page == "Feature Analysis":
    st.title("Audio Feature Analysis")

    selected_feature = st.sidebar.selectbox("Select Audio Feature",
        ['danceability', 'energy', 'valence', 'acousticness', 'loudness', 'tempo', 'speechiness'])

    year_min, year_max = get_year_bounds()
    selected_years = st.sidebar.slider("Filter by Year Range", year_min, year_max, (year_min, year_max))

    all_features = get_all_feature_data()
    feature_data = all_features[[selected_feature, 'track_popularity', 'artist_0', 'release_date']].copy()
    feature_data = feature_data[feature_data[selected_feature].notna()]

    feature_data['year'] = pd.to_datetime(feature_data['release_date'], errors='coerce').dt.year
    feature_data = feature_data.dropna(subset=['year'])
    feature_data = feature_data[
        (feature_data['year'] >= selected_years[0]) &
        (feature_data['year'] <= selected_years[1])
    ]

    metric1, metric2, metric3 = st.columns(3)
    metric1.metric("Mean Value", f"{feature_data[selected_feature].mean():.3f}")
    metric2.metric("Median Value", f"{feature_data[selected_feature].median():.3f}")
    metric3.metric("Standard Deviation", f"{feature_data[selected_feature].std():.3f}")

    chart1, chart2 = st.columns(2)

    with chart1:
        st.subheader(f"{selected_feature.capitalize()} Distribution")
        fig1, ax1 = plt.subplots(figsize=(8, 5))
        ax1.hist(feature_data[selected_feature], bins=50, color=SPOTIFY_GREEN,
                edgecolor=ALMOST_BLACK, alpha=0.8)
        ax1.set_xlabel(selected_feature.capitalize(), fontsize=11)
        ax1.set_ylabel('Count', fontsize=11)
        ax1.grid(axis='y', alpha=0.3, color=DARK_GREY)
        plt.tight_layout()
        st.pyplot(fig1)

    with chart2:
        st.subheader(f"{selected_feature.capitalize()} vs Track Popularity")
        fig2, ax2 = plt.subplots(figsize=(8, 5))
        ax2.scatter(feature_data[selected_feature], feature_data['track_popularity'],
                   alpha=0.15, s=8, color=DARK_GREY)
        ax2.set_xlabel(selected_feature.capitalize(), fontsize=11)
        ax2.set_ylabel('Track Popularity', fontsize=11)

        correlation = feature_data[selected_feature].corr(feature_data['track_popularity'])
        ax2.text(0.05, 0.95, f'Correlation: {correlation:.3f}',
                transform=ax2.transAxes, fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor=LIGHT_GREY, alpha=0.7))
        ax2.grid(alpha=0.2, color=DARK_GREY)
        plt.tight_layout()
        st.pyplot(fig2)

    st.subheader(f"Artists with Highest Average {selected_feature.capitalize()}")
    artist_averages = feature_data.groupby('artist_0')[selected_feature].mean().nlargest(12)

    fig3, ax3 = plt.subplots(figsize=(10, 6))
    ax3.barh(range(len(artist_averages)), artist_averages.values, color=SPOTIFY_GREEN_LIGHT)
    ax3.set_yticks(range(len(artist_averages)))
    ax3.set_yticklabels(artist_averages.index, fontsize=9)
    ax3.set_xlabel(f'Average {selected_feature.capitalize()}', fontsize=11)
    ax3.grid(axis='x', alpha=0.3, color=DARK_GREY)
    plt.tight_layout()
    st.pyplot(fig3)

# artist analysis page
elif current_page == "Artist Analysis":
    st.title("Artist Analysis")

    artists_df = get_artists()

    st.subheader("Artist Statistics Overview")

    stat1, stat2, stat3 = st.columns(3)
    stat1.metric("Total Artists", f"{len(artists_df):,}")
    stat2.metric("Avg Popularity", f"{artists_df['artist_popularity'].mean():.1f}")
    stat3.metric("Total Albums", f"{artists_df['album_count'].sum():.0f}")

    left_chart, right_chart = st.columns(2)

    with left_chart:
        st.subheader("Most Popular Artists")
        top_popular = artists_df.nlargest(15, 'artist_popularity')[['name', 'artist_popularity']]

        fig_pop, ax_pop = plt.subplots(figsize=(8, 6))
        ax_pop.barh(range(len(top_popular)), top_popular['artist_popularity'].values,
                   color=SPOTIFY_GREEN)
        ax_pop.set_yticks(range(len(top_popular)))
        ax_pop.set_yticklabels(top_popular['name'].values, fontsize=9)
        ax_pop.set_xlabel('Popularity Score', fontsize=11)
        ax_pop.grid(axis='x', alpha=0.3, color=DARK_GREY)
        plt.tight_layout()
        st.pyplot(fig_pop)

    with right_chart:
        st.subheader("Most Prolific Artists")
        top_albums = artists_df.nlargest(15, 'album_count')[['name', 'album_count']]

        fig_alb, ax_alb = plt.subplots(figsize=(8, 6))
        ax_alb.barh(range(len(top_albums)), top_albums['album_count'].values,
                   color=SPOTIFY_GREEN_LIGHT)
        ax_alb.set_yticks(range(len(top_albums)))
        ax_alb.set_yticklabels(top_albums['name'].values, fontsize=9)
        ax_alb.set_xlabel('Album Count', fontsize=11)
        ax_alb.grid(axis='x', alpha=0.3, color=DARK_GREY)
        plt.tight_layout()
        st.pyplot(fig_alb)

    st.subheader("Artist Popularity Distribution")
    fig_dist, ax_dist = plt.subplots(figsize=(12, 5))
    ax_dist.hist(artists_df['artist_popularity'], bins=40, color=DARK_GREY,
                edgecolor=ALMOST_BLACK, alpha=0.8)
    ax_dist.set_xlabel('Popularity Score', fontsize=11)
    ax_dist.set_ylabel('Number of Artists', fontsize=11)
    ax_dist.grid(axis='y', alpha=0.3, color=DARK_GREY)
    plt.tight_layout()
    st.pyplot(fig_dist)

elif current_page == "Artist Search":
    st.title("Artist Search")

    artists_df = get_artists()
    top_200_artists = artists_df.nlargest(200, 'artist_popularity')

    user_search = st.sidebar.text_input("Search for Artist (top 200)", "")

    if user_search:
        search_results = top_200_artists[
            top_200_artists['name'].str.contains(user_search, case=False, na=False)
        ]

        if len(search_results) > 0:
            chosen_artist = st.sidebar.selectbox("Select from Results", search_results['name'].tolist())
            artist_info = artists_df[artists_df['name'] == chosen_artist].iloc[0]

            st.subheader(f"Profile: {chosen_artist}")

            info1, info2 = st.columns(2)
            info1.metric("Popularity Score", f"{artist_info['artist_popularity']:.0f}")
            info2.metric("Number of Albums", f"{artist_info['album_count']:.0f}")

            db = get_db()
            track_query = """
            SELECT t.track_popularity, f.danceability, f.energy, f.valence,
                   f.acousticness, f.loudness, f.tempo
            FROM tracks_data t
            JOIN features_data f ON t.id = f.id
            JOIN albums_data a ON t.id = a.track_id
            WHERE a.artist_0 = ?
            LIMIT 100
            """
            tracks_df = pd.read_sql_query(track_query, db, params=[chosen_artist])

            if len(tracks_df) > 0:
                st.subheader("Audio Characteristics")
                audio_chart1, audio_chart2 = st.columns(2)

                with audio_chart1:
                    audio_features = ['danceability', 'energy', 'valence', 'acousticness']
                    feature_means = tracks_df[audio_features].mean()

                    fig_audio, ax_audio = plt.subplots(figsize=(8, 5))
                    bar_colors = [SPOTIFY_GREEN, SPOTIFY_GREEN_LIGHT, DARK_GREY, LIGHT_GREY]
                    ax_audio.bar(range(len(feature_means)), feature_means.values, color=bar_colors)
                    ax_audio.set_xticks(range(len(feature_means)))
                    ax_audio.set_xticklabels([f.capitalize() for f in audio_features],
                                            rotation=45, ha='right')
                    ax_audio.set_ylim(0, 1)
                    ax_audio.set_ylabel('Average Score', fontsize=11)
                    ax_audio.grid(axis='y', alpha=0.3, color=DARK_GREY)
                    plt.tight_layout()
                    st.pyplot(fig_audio)

                with audio_chart2:
                    fig_pop_dist, ax_pop_dist = plt.subplots(figsize=(8, 5))
                    ax_pop_dist.hist(tracks_df['track_popularity'], bins=20,
                                    color=SPOTIFY_GREEN, edgecolor=ALMOST_BLACK, alpha=0.8)
                    ax_pop_dist.set_xlabel('Popularity Score', fontsize=11)
                    ax_pop_dist.set_ylabel('Number of Tracks', fontsize=11)
                    ax_pop_dist.set_title('Track Popularity Distribution', fontsize=12, weight='bold')
                    ax_pop_dist.grid(axis='y', alpha=0.3, color=DARK_GREY)
                    plt.tight_layout()
                    st.pyplot(fig_pop_dist)

                st.subheader("Detailed Statistics")
                artist_stats = pd.DataFrame({
                    'Metric': ['Avg Popularity', 'Danceability', 'Energy', 'Valence',
                              'Acousticness', 'Loudness (dB)', 'Tempo (BPM)'],
                    'Value': [
                        f"{tracks_df['track_popularity'].mean():.2f}",
                        f"{tracks_df['danceability'].mean():.3f}",
                        f"{tracks_df['energy'].mean():.3f}",
                        f"{tracks_df['valence'].mean():.3f}",
                        f"{tracks_df['acousticness'].mean():.3f}",
                        f"{tracks_df['loudness'].mean():.2f}",
                        f"{tracks_df['tempo'].mean():.1f}"
                    ]
                })
                st.dataframe(artist_stats, use_container_width=True)
            else:
                st.info("No track data available for this artist")
        else:
            st.info("No artists found matching your search")
    else:
        st.info("Enter an artist name in the sidebar to search")
        st.subheader("Top 20 Most Popular Artists")
        top_20_display = top_200_artists[['name', 'artist_popularity', 'album_count']].head(20)
        top_20_display.columns = ['Artist Name', 'Popularity', 'Album Count']
        st.dataframe(top_20_display, use_container_width=True)

elif current_page == "Compare Artists":
    st.title("Compare Two Artists")

    artists_df = get_artists()
    artist_names = artists_df['name'].sort_values().tolist()

    col1, col2 = st.columns(2)
    with col1:
        artist1 = st.selectbox("Select First Artist", artist_names, key="artist1")
    with col2:
        artist2 = st.selectbox("Select Second Artist", artist_names, key="artist2")

    if artist1 and artist2 and artist1 != artist2:
        info1, info2 = st.columns(2)
        artist1_info = artists_df[artists_df['name'] == artist1].iloc[0]
        artist2_info = artists_df[artists_df['name'] == artist2].iloc[0]
        info1.metric("Popularity Score", f"{artist1_info['artist_popularity']:.0f}")
        info1.metric("Number of Albums", f"{artist1_info['album_count']:.0f}")
        info2.metric("Popularity Score", f"{artist2_info['artist_popularity']:.0f}")
        info2.metric("Number of Albums", f"{artist2_info['album_count']:.0f}")

        db = get_db()
        track_query = """
            SELECT t.track_popularity, f.danceability, f.energy, f.valence,
                   f.acousticness, f.loudness, f.tempo
            FROM tracks_data t
            JOIN features_data f ON t.id = f.id
            JOIN albums_data a ON t.id = a.track_id
            WHERE a.artist_0 = ?
            LIMIT 100
        """
        tracks1 = pd.read_sql_query(track_query, db, params=[artist1])
        tracks2 = pd.read_sql_query(track_query, db, params=[artist2])

        st.subheader("Audio Feature Comparison")
        features = ['danceability', 'energy', 'valence', 'acousticness', 'loudness', 'tempo']
        feature_means1 = tracks1[features].mean()
        feature_means2 = tracks2[features].mean()
        compare_df = pd.DataFrame({
            artist1: feature_means1,
            artist2: feature_means2
        }).reset_index().rename(columns={'index': 'Feature'})
        st.dataframe(compare_df, use_container_width=True)

        st.subheader("Popularity Distribution")
        chart1, chart2 = st.columns(2)
        with chart1:
            st.write(f"{artist1} Track Popularity")
            fig1, ax1 = plt.subplots(figsize=(7, 4))
            ax1.hist(tracks1['track_popularity'], bins=20, color=SPOTIFY_GREEN, edgecolor=ALMOST_BLACK, alpha=0.7)
            ax1.set_xlabel('Popularity Score')
            ax1.set_ylabel('Number of Tracks')
            ax1.set_title(f'{artist1} Track Popularity')
            st.pyplot(fig1)
        with chart2:
            st.write(f"{artist2} Track Popularity")
            fig2, ax2 = plt.subplots(figsize=(7, 4))
            ax2.hist(tracks2['track_popularity'], bins=20, color=SPOTIFY_GREEN_LIGHT, edgecolor=ALMOST_BLACK, alpha=0.7)
            ax2.set_xlabel('Popularity Score')
            ax2.set_ylabel('Number of Tracks')
            ax2.set_title(f'{artist2} Track Popularity')
            st.pyplot(fig2)
    else:
        st.info("Please select two different artists to compare.")

elif current_page == "Genre Explorer":
    st.title("Genre Explorer")
    st.write("Select a genre and see the top artists.")

    import ast

    fresh_conn = sqlite3.connect('spotify_database.db', check_same_thread=False)
    artists_raw = pd.read_sql_query(
        "SELECT name, artist_popularity, followers, artist_genres FROM artist_data", fresh_conn
    )
    fresh_conn.close()

    all_genres = []
    for val in artists_raw['artist_genres'].dropna():
        try:
            all_genres.extend(ast.literal_eval(val))
        except:
            pass
    genre_counts = pd.Series(all_genres).value_counts()
    top_genres = genre_counts.head(20).index.tolist()
    all_genre_list = genre_counts.index.tolist()

    selected_genres = st.pills("Select genres:", top_genres, selection_mode="multi") or []

    search_genre = st.text_input("Or search for any genre:", "")
    if search_genre:
        matches = [g for g in all_genre_list if search_genre.lower() in g.lower()]
        if matches:
            if matches[0] not in selected_genres:
                selected_genres = selected_genres + [matches[0]]
            st.caption(f"Added: **{matches[0]}**")
        else:
            st.warning(f"No genre found matching '{search_genre}'")

    top_n = st.pills("Show top:", [10, 20, 50], default=10, selection_mode="single") or 10

    if selected_genres:
        def has_any_genre(genre_str, genres):
            try:
                artist_genres = ast.literal_eval(genre_str)
                return any(g in artist_genres for g in genres)
            except:
                return False

        filtered = artists_raw[
            artists_raw['artist_genres'].apply(lambda x: has_any_genre(x, selected_genres))
        ].copy()

        filtered = filtered.nlargest(top_n, 'artist_popularity').reset_index(drop=True)
        filtered.index += 1

        st.subheader(f"Top {top_n} artists in: {', '.join(selected_genres)}")
        st.markdown("---")

        display_df = filtered[['name', 'artist_popularity', 'followers']].copy()
        display_df.columns = ['Artist', 'Popularity', 'Followers']
        display_df['Followers'] = display_df['Followers'].apply(
            lambda v: f"{int(v/1_000_000):.1f}M" if v >= 1_000_000
            else f"{int(v/1_000)}K" if v >= 1_000
            else str(int(v)) if pd.notna(v) else "N/A"
        )
        st.dataframe(display_df, use_container_width=True)

        st.markdown("---")
        st.subheader("Popularity per Followers")

        ratio_df = filtered.dropna(subset=['followers', 'artist_popularity']).copy()
        ratio_df = ratio_df[ratio_df['followers'] > 0]
        avg_followers = ratio_df['followers'].mean()
        if avg_followers >= 1_000_000:
            scale = 1_000_000
            scale_label = "per Million Followers"
        elif avg_followers >= 1_000:
            scale = 1_000
            scale_label = "per 1K Followers"
        else:
            scale = 1
            scale_label = "per Follower"

        ratio_df['ratio'] = ratio_df['artist_popularity'] / (ratio_df['followers'] / scale)
        ratio_df = ratio_df.sort_values('ratio', ascending=True)

        fig_g, ax_g = plt.subplots(figsize=(10, max(4, len(ratio_df) * 0.45)))
        ax_g.barh(range(len(ratio_df)), ratio_df['ratio'].values,
                  color=SPOTIFY_GREEN, edgecolor=ALMOST_BLACK, alpha=0.85)
        ax_g.set_yticks(range(len(ratio_df)))
        ax_g.set_yticklabels(ratio_df['name'].values, fontsize=9)
        ax_g.set_xlabel(f'Popularity Score {scale_label}', fontsize=11)
        ax_g.grid(axis='x', alpha=0.3, color=DARK_GREY)
        plt.tight_layout()
        st.pyplot(fig_g)
    else:
        st.info("Click on a genre above to get started.")

st.sidebar.markdown("---")
st.sidebar.caption("Spotify Data Analysis Dashboard")
