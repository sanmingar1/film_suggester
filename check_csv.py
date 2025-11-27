import pandas as pd
df = pd.read_csv('data/movies_clean.csv')
print("Columns:", df.columns.tolist())
if 'ml_rating' in df.columns:
    print("ml_rating exists!")
    print("Non-null count:", df['ml_rating'].count())
    print("Sample:", df[['title', 'ml_rating']].head())
else:
    print("ml_rating MISSING!")
