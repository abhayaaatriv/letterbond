import pandas as pd
import requests
import os
import json
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

OMDB_API_KEY = "87e50e19"
CACHE_FILE = "omdb_cache.json"

# Load cache if it exists
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r") as f:
        omdb_cache = json.load(f)
else:
    omdb_cache = {}

def save_cache():
    with open(CACHE_FILE, "w") as f:
        json.dump(omdb_cache, f)

def load_ratings(file_path):
    df = pd.read_csv(file_path)
    df = df[['Name', 'Year', 'Rating']]
    df['Name'] = df['Name'].str.lower().str.strip()
    return df

def get_metadata(title, year, api_key=OMDB_API_KEY):
    key = f"{title.strip().lower()}_{year}"
    if key in omdb_cache:
        return omdb_cache[key]

    url = f"http://www.omdbapi.com/?t={title}&y={year}&apikey={api_key}"
    try:
        res = requests.get(url, timeout=5)
        data = res.json()
        if data.get("Response") == "True":
            result = {
                "genre": data.get("Genre", ""),
                "director": data.get("Director", "")
            }
            omdb_cache[key] = result
            save_cache()
            return result
    except:
        pass

    return {"genre": "", "director": ""}

def create_profile(df):
    profile = []
    for _, row in df.iterrows():
        meta = get_metadata(row['Name'], row['Year'])
        profile.append(f"{meta['genre']} {meta['director']}")
    return " ".join(profile)

def compute_profile_similarity(profile1, profile2):
    vectorizer = CountVectorizer()
    vectors = vectorizer.fit_transform([profile1, profile2])
    return cosine_similarity(vectors)[0][1] * 100

def compute_rating_similarity(df1, df2):
    merged = pd.merge(df1, df2, on=['Name', 'Year'], suffixes=('_1', '_2'))
    if merged.empty:
        return 0.0
    merged['diff'] = abs(merged['Rating_1'] - merged['Rating_2'])
    merged['score'] = 1 - (merged['diff'] / 5.0)
    return merged['score'].mean() * 100

def compute_match_score(file1, file2):
    df1 = load_ratings(file1)
    df2 = load_ratings(file2)
    rating_score = compute_rating_similarity(df1, df2)
    profile1 = create_profile(df1)
    profile2 = create_profile(df2)
    genre_score = compute_profile_similarity(profile1, profile2)
    final_score = round((0.6 * rating_score + 0.4 * genre_score), 2)
    return final_score, round(rating_score, 2), round(genre_score, 2)