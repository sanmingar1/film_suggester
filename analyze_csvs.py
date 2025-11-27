import pandas as pd
import os

files = [
    'data/movies_metadata.csv',
    'data/keywords.csv', 
    'data/credits.csv',
    'data/links.csv',
    'data/links_small.csv'
]

for f in files:
    if os.path.exists(f):
        try:
            df = pd.read_csv(f, nrows=2)
            print(f'\n{"="*60}')
            print(f'Archivo: {f}')
            print(f'Columnas: {list(df.columns)}')
            print(f'Total filas: {len(pd.read_csv(f))}')
            print(f'Ejemplo primer registro:')
            print(df.head(1))
        except Exception as e:
            print(f'{f}: Error - {e}')
