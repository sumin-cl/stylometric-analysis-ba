import pandas as pd
import re

def stratified_sample(path_a, output_path):
    df_a = pd.read_csv(path_a)
    df_a['date'] = pd.to_datetime(df_a['date'])
    df_a['year'] = df_a['date'].dt.year

    # 1. Zielzahlen definieren (Mapping B -> A)
    targets = {2021: 430, 2020: 393}
    
    # 2. Hype-Keywords für 2020-2021
    keywords = [
        "BERT", "GPT-2", "GPT-3", "Transformer", "RoBERTa", 
        "T5", "GAN", "Attention", "Pytorch", "Tensorflow", "CNN", "LSTM"
    ]
    pattern = '|'.join(keywords)

    final_frames = []

    for year, n in targets.items():
        year_data = df_a[df_a['year'] == year].copy()
        
        # Identifiziere "Hype"-Posts im Jahr
        year_data['is_hype'] = year_data['text'].str.contains(pattern, case=False, na=False)
        hype_posts = year_data[year_data['is_hype']]
        normal_posts = year_data[~year_data['is_hype']]

        print(f"Jahr {year}: {len(hype_posts)} Hype-Posts gefunden.")

        # Wir nehmen so viele Hype-Posts wie möglich (bis zum Limit n)
        if len(hype_posts) >= n:
            sampled_year = hype_posts.sample(n=n, random_state=42)
        else:
            # Fülle mit normalen Posts auf
            needed = n - len(hype_posts)
            fill_posts = normal_posts.sample(n=needed, random_state=42)
            sampled_year = pd.concat([hype_posts, fill_posts])
        
        final_frames.append(sampled_year)
        print(f"-> {len(sampled_year)} Posts für {year} extrahiert.")

    # 3. Finalisieren
    df_final = pd.concat(final_frames)
    df_final = df_final.drop(columns=['year', 'is_hype'])
    df_final.to_csv(output_path, index=False)
    print(f"\nErfolg: {len(df_final)} Posts in {output_path} gespeichert.")

if __name__ == "__main__":
    stratified_sample('corpus_a_clean.csv', 'corpus_a_mirrored.csv')