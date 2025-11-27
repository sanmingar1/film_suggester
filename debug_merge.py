"""
Debug merge logic
"""
import pandas as pd
import os

DATA_DIR = 'data'

print("Loading metadata head...")
df_meta = pd.read_csv(os.path.join(DATA_DIR, 'movies_metadata.csv'), low_memory=False)
# Clean ID
df_meta = df_meta[pd.to_numeric(df_meta['id'], errors='coerce').notnull()]
df_meta['id'] = df_meta['id'].astype(int).astype(str)
print(f"Metadata IDs example: {df_meta['id'].head().tolist()}")

print("\nLoading links...")
links_df = pd.read_csv(os.path.join(DATA_DIR, 'links.csv'))
links_df = links_df.dropna(subset=['tmdbId'])
links_df['tmdbId'] = links_df['tmdbId'].astype(int).astype(str)
links_df['movieId'] = links_df['movieId'].astype(str)
print(f"Links TMDB IDs example: {links_df['tmdbId'].head().tolist()}")

print("\nLoading ratings small...")
ratings_df = pd.read_csv(os.path.join(DATA_DIR, 'ratings_small.csv'))
ratings_df['movieId'] = ratings_df['movieId'].astype(str)

print("\nAggregating ratings...")
ratings_agg = ratings_df.groupby('movieId')['rating'].agg(['mean', 'count']).reset_index()
ratings_agg.columns = ['movieId', 'ml_rating', 'ml_count']

print("\nMerging ratings + links...")
ratings_final = pd.merge(ratings_agg, links_df[['movieId', 'tmdbId']], on='movieId', how='inner')
print(f"Ratings with TMDB ID: {len(ratings_final)}")
print(ratings_final.head())

print("\nMerging with metadata...")
merged = pd.merge(df_meta.head(100), ratings_final, left_on='id', right_on='tmdbId', how='left')

print("\nCheck Toy Story (ID 862):")
toy_story = merged[merged['id'] == '862']
if not toy_story.empty:
    print(toy_story[['title', 'ml_rating', 'ml_count']])
else:
    print("Toy Story not found in head(100) or merge failed")
