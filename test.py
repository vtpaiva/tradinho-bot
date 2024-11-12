import pandas as pd

df = pd.read_csv('headlines.csv')

df['texto_concatenado'] = df.groupby('fortnight')['title'].transform(lambda x: ' '.join(x))
df = df.drop_duplicates(subset=['fortnight'], keep='first')

df = df.drop(columns=['title'], axis=1)
df.rename(columns={'texto_concatenado': 'title'}, inplace=True)

order = ['date','fortnight','fortnight_day','section','title','diff']

df = df[order]

df.to_csv('new_headlines.csv', index=False)