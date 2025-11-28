import pandas as pd
df = pd.read_csv('data/links.csv')
print(f"Total links: {len(df)}")
df = df.dropna(subset=['tmdbId'])
df['tmdbId'] = df['tmdbId'].astype(int).astype(str)
duplicates = df[df.duplicated(subset=['tmdbId'], keep=False)]
print(f"Duplicate TMDB IDs: {len(duplicates)}")
if len(duplicates) > 0:
    print(duplicates.sort_values('tmdbId').head())
