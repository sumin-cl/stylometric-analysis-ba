import pandas as pd
df_b = pd.read_csv('corpus_b_clean.csv')
# Falls 'date' ein String ist, extrahieren wir das Jahr
print(pd.to_datetime(df_b['date']).dt.year.value_counts())