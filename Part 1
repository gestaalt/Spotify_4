import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

# Load the data
df = pd.read_csv('artist_data.csv')


# Display columns and data types
print('Columns:', df.columns.tolist())
print('Data types:')
print(df.dtypes)

# Count unique artists by 'name'
unique_artists = df['name'].nunique() if 'name' in df.columns else None
print('Unique artists:', unique_artists)

# Top 10 by popularity
if 'artist_popularity' in df.columns and 'name' in df.columns:
    top_popularity = df.groupby('name')['artist_popularity'].max().sort_values(ascending=False).head(10)
    print('Top 10 artists by popularity:')
    print(top_popularity)
else:
    top_popularity = None

# Top 10 by followers
if 'followers' in df.columns and 'name' in df.columns:
    top_followers = df.groupby('name')['followers'].max().sort_values(ascending=False).head(10)
    print('Top 10 artists by followers:')
    print(top_followers)
else:
    top_followers = None

# Plotting
fig, axs = plt.subplots(1, 2, figsize=(18, 7))
if top_popularity is not None:
    top_popularity[::-1].plot(kind='barh', ax=axs[0], color='skyblue')
    axs[0].set_title('Top 10 Artists by Popularity')
    axs[0].set_xlabel('Popularity')
    axs[0].set_ylabel('Artist')
    axs[0].grid(axis='x', linestyle='--', alpha=0.7)
if top_followers is not None:
    top_followers[::-1].plot(kind='barh', ax=axs[1], color='salmon')
    axs[1].set_title('Top 10 Artists by Followers')
    axs[1].set_xlabel('Followers')
    axs[1].set_ylabel('Artist')
    axs[1].grid(axis='x', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()

# --- Popularity vs Followers Analysis ---
print("\n--- Popularity vs Followers Analysis ---")

# Remove rows with missing or zero followers or popularity
df_valid = df[(df['followers'] > 0) & (df['artist_popularity'] > 0)]

# Correlation
correlation = df_valid['artist_popularity'].corr(np.log(df_valid['followers']))
print(f"Correlation between popularity and log(followers): {correlation:.3f}")


# Linear regression using scipy.stats.linregress
X = np.log(df_valid['followers'])
y = df_valid['artist_popularity']
slope, intercept, r_value, p_value, std_err = stats.linregress(X, y)
print(f"\nLinear regression results:")
print(f"Intercept: {intercept:.3f}")
print(f"Slope: {slope:.3f}")
print(f"R-squared: {r_value**2:.3f}")
print(f"p-value: {p_value:.3e}")
print(f"Standard error: {std_err:.3f}")


# Scatter plot with regression line
plt.figure(figsize=(10,6))
plt.scatter(X, y, alpha=0.3, label='Artists')
plt.plot(X, intercept + slope * X, color='red', label='Linear fit')
plt.xlabel('log(Followers)')
plt.ylabel('Popularity')
plt.title('Spotify Popularity vs log(Followers)')
plt.legend()
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()


# Identify overperformers and legacy artists
df_valid = df_valid.copy()
df_valid['pop_pred'] = intercept + slope * X
df_valid['residual'] = df_valid['artist_popularity'] - df_valid['pop_pred']

# Overperformers: high residuals (actual >> predicted)
overperformers = df_valid.nlargest(10, 'residual')[['name', 'artist_popularity', 'followers', 'residual']]
print("\nTop 10 Overperformers (high popularity, low followers):")
print(overperformers)

# Legacy artists: low residuals (actual << predicted)
legacy_artists = df_valid.nsmallest(10, 'residual')[['name', 'artist_popularity', 'followers', 'residual']]
print("\nTop 10 Legacy Artists (low popularity, high followers):")
print(legacy_artists)


# --- Genre Analysis Functions ---
def top_artists_by_genre(df, genre, popularity_col='artist_popularity', name_col='name', genres_col='artist_genres'):
    """
    Returns the top 10 artists within a given genre by popularity.
    """
    # Ensure genres_col is a list of genres
    def genre_in_row(genres):
        if isinstance(genres, str):
            try:
                genres_eval = eval(genres)
                if isinstance(genres_eval, list):
                    return genre in [g.lower() for g in genres_eval]
            except:
                return False
        elif isinstance(genres, list):
            return genre in [g.lower() for g in genres]
        return False

    genre_mask = df[genres_col].apply(genre_in_row)
    filtered = df[genre_mask]
    if filtered.empty:
        print(f"No artists found for genre: {genre}")
        return None
    top10 = filtered.sort_values(by=popularity_col, ascending=False).head(10)
    print(f"Top 10 artists in genre '{genre}':")
    print(top10[[name_col, popularity_col, 'followers', genres_col]])
    return top10


print("\nNow let's look atthe top 10 artists within the genre: rap.")
top_artists_by_genre(df, 'rap')

# --- Number of Genres Analysis ---
print("\n--- Number of Genres Analysis ---")
def count_genres(genres):
    if isinstance(genres, str):
        try:
            genres_eval = eval(genres)
            if isinstance(genres_eval, list):
                return len([g for g in genres_eval if g and g != 'NA'])
        except:
            return 0
    elif isinstance(genres, list):
        return len([g for g in genres if g and g != 'NA'])
    return 0

df['num_genres'] = df['artist_genres'].apply(count_genres)
print(df[['name', 'num_genres']].head())

# Visualization: Number of genres vs popularity and followers
plt.figure(figsize=(12,5))
plt.subplot(1,2,1)
plt.scatter(df['num_genres'], df['artist_popularity'], alpha=0.3)
plt.xlabel('Number of Genres')
plt.ylabel('Popularity')
plt.title('Popularity vs Number of Genres')
plt.grid(True, linestyle='--', alpha=0.5)

plt.subplot(1,2,2)
plt.scatter(df['num_genres'], df['followers'], alpha=0.3, color='orange')
plt.xlabel('Number of Genres')
plt.ylabel('Followers')
plt.title('Followers vs Number of Genres')
plt.grid(True, linestyle='--', alpha=0.5)

plt.tight_layout()
plt.show()


# --- Mac Miller Genre Analysis ---
print("\n--- Mac Miller Genre Analysis ---")
# Find Mac Miller row
mac = df[df['name'].str.lower() == 'mac miller']
if not mac.empty:
    # Count genres
    def count_genres(genres):
        if isinstance(genres, str):
            try:
                genres_eval = eval(genres)
                if isinstance(genres_eval, list):
                    return len([g for g in genres_eval if g and g != 'NA'])
            except:
                return 0
        elif isinstance(genres, list):
            return len([g for g in genres if g and g != 'NA'])
        return 0
    mac['num_genres'] = mac['artist_genres'].apply(count_genres)
    print(mac[['name', 'artist_popularity', 'followers', 'artist_genres', 'num_genres']])
    # Visualize
    plt.figure(figsize=(4, 6))
    plt.bar('Mac Miller', mac['num_genres'].values[0], color='teal')
    plt.ylabel('Number of Genres')
    plt.title('Number of Genres for Mac Miller')
    plt.tight_layout()
    plt.show()
else:
    print("Mac Miller not found in dataset.")

# Correlation for all artists
if df['num_genres'].max() > 0:
    corr_pop = df['num_genres'].corr(df['artist_popularity'])
    corr_fol = df['num_genres'].corr(df['followers'])
    print(f"Correlation between number of genres and popularity: {corr_pop:.3f}")
    print(f"Correlation between number of genres and followers: {corr_fol:.3f}")

# --- Follower Intensity Analysis ---
print("\n--- Follower Intensity Analysis ---")
# Follower intensity = followers / popularity
df_intensity = df[(df['followers'] > 0) & (df['artist_popularity'] > 0)].copy()
df_intensity['follower_intensity'] = df_intensity['followers'] / df_intensity['artist_popularity']

# Top 10 artists with highest follower intensity
top_intensity = df_intensity.sort_values('follower_intensity', ascending=False).head(10)
print("Top 10 artists with the most 'insane' followers:")
print(top_intensity[['name', 'followers', 'artist_popularity', 'follower_intensity']])

# Visualize with a bar plot
import matplotlib.pyplot as plt
plt.figure(figsize=(12,6))
plt.bar(top_intensity['name'], top_intensity['follower_intensity'], color='purple')
plt.xticks(rotation=45, ha='right')
plt.ylabel('Follower Intensity (followers / popularity)')
plt.title('Top 10 Artists with Most "Insane" Followers')
plt.tight_layout()
plt.show()

