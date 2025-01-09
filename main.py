from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
# import matplotlib.pyplot as plt

# from data_preprocessing import pipe_prepocessing
app = FastAPI()

# Count of songs per year
df = pd.read_csv("csv/spotify_tracks.csv")

# Add CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite's default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

############################################
############## DATA ANALYSIS ###############
############################################

@app.get("/")
def get_spotify_data():
    return df.to_dict(orient="records")

# Count of songs per year
@app.get("/songs-by-year")
def read_root():
    countByYear = df.groupby(['year']).size().to_dict()
    test = df.head().to_dict()

    return {"message": "Bienvenue sur FastAPI !", "songsByYear": countByYear}

# Name and artists with parameter year
@app.get("/year/{year}")
def songs_by_year(year: int):
    filtered = df[df['year'] == year]
    songs = filtered[['name', 'artists']].to_dict(orient='records')

    return {"year": year, "songs": songs}

# Count songs per artist per year
@app.get("/artist/{year}")
def song_per_artist(year: int):
    filtered = df[df['year'] == year]
    songsPerArtist = filtered.groupby(['artists']).size().sort_values(ascending=False).to_dict()

    return {"year": year, "songsPerArtist": songsPerArtist}

# Acousticness per year
@app.get("/acousticness-per-year")
def acousticness():
    average = df.groupby('year')['acousticness'].mean().sort_values(ascending=False).to_dict()

    return {"average_acousticness": average}

# Danceability per year
@app.get("/danceability-per-year")
def danceability():
    average = df.groupby('year')['danceability'].mean().sort_values(ascending=False).to_dict()

    return {"average_danceability": average}

# Positivness depending on the mode
@app.get("/positivness-mode")
def positivness():
    positivness = df.groupby('mode')['valence'].mean().sort_values(ascending=False).to_dict()
    mode = df.groupby(['mode']).size().to_dict()
    sum = df.describe()

    return {"sum": sum, "positivness": positivness, "mode": mode}

# Analyse et visualisation du taux de danceability et valence
@app.get("/danceability-and-valence")
def danceability_and_valence():
    grouped = df.groupby(['danceability', 'valence']).size().reset_index(name='count')
    result = grouped.to_dict(orient='records')
    return {"data": result}

# Analyse et visualisation de la popularité en fonction du tempo
@app.get("/popularity-vs-tempo")
def popularity_vs_tempo():
    grouped = df.groupby('tempo')['popularity'].mean().reset_index()
    result = grouped.to_dict(orient='records')
    return {"data": result}

# Analyse et visualisation de l'acousticness par année
@app.get("/acousticness-per-year")
def acousticness_per_year():
    grouped = df.groupby('year')['acousticness'].mean().reset_index()
    result = grouped.to_dict(orient='records')
    return {"data": result}

# Analyse et visualisation de la popularité par langue
@app.get("/popularity-per-language")
def popularity_per_language():
    grouped = df.groupby('language')['popularity'].mean().reset_index()
    result = grouped.to_dict(orient='records')
    return {"data": result}

#Popularity per language 2
@app.get("/popularity-per-language-2")
def popularity_per_language_2():
    grouped = pd.crosstab(df['popularity'], df['language'])
    result = grouped.to_dict(orient='records')
    return {"data": result}

# Most danceable songs
#@app.get("/ten-most-danceable")
#def ten_most_danceable():
#    grouped = df.sort_values(by='danceability',ascending=False)
#    result = grouped.to_dict(orient='records')
#    return {"data": result}

#Tracks by authors

#Popularity per language 2
@app.get("/tracks-per-author")
def tracks_per_author():
    grouped = df.groupby(['artist_name', 'year']).size().reset_index(name='track_count')
    #grouped = pd.crosstab(df['artist_name'], df['year'])
    grouped = grouped.head(50)
    result = grouped.to_dict(orient='records')
    return {"data": result}

# Analyse et visualisation de la danceability en fonction de la valence
@app.get("/danceability-vs-valence")
def danceability_vs_valence():
    grouped = df.groupby('valence')['danceability'].mean().reset_index()
    result = grouped.to_dict(orient='records')
    return {"data": result}

# Top 10 songs with the highest danceability
@app.get("/top-10-party-tracks")
def top_10_party_tracks():
    party_tracks = df[(df['danceability'] > 0.8) & (df['energy'] > 0.7) & (df['loudness'] > -5)]
    top_party = party_tracks.nlargest(10, 'popularity')[['name', 'artists', 'danceability', 'energy', 'popularity']].to_dict(orient='records')
    return {"top_10_party_tracks": top_party}

# Top 10 songs with most danceability
# @app.get("/10danceableSongs")
# def danceableSongs():
#     top10 = df[['name', 'artists', 'danceability', 'year']].sort_values(by='danceability', ascending=False).head(10).to_dict(orient='records')
#     return {"top10": top10}

# Top 10 songs with the highest duration
@app.get("/top-10-longest-tracks")
def top_10_longest_tracks():
    longest_tracks = df.nlargest(10, 'duration_ms')[['name', 'artists', 'duration_ms']].to_dict(orient='records')
    return {"top_10_longest_tracks": longest_tracks}

# Top 10 songs with the highest acousticness and lowest energy
@app.get("/top-10-relaxing-tracks")
def top_10_relaxing_tracks():
    relaxing_tracks = df[(df['acousticness'] > 0.8) & (df['energy'] < 0.4)]
    top_relaxing = relaxing_tracks.nlargest(10, 'acousticness')[['name', 'artists', 'acousticness', 'energy']].to_dict(orient='records')
    return {"top_10_relaxing_tracks": top_relaxing}

# Top 10 songs with the highest popularity
@app.get("/top-10-popular-tracks")
def top_10_popular_tracks():
    top_tracks = df.nlargest(10, 'popularity')[['name', 'artists', 'popularity']].to_dict(orient='records')
    return {"top_10_popular_tracks": top_tracks}


############################################
############## CRUD OPERATIONS #############
############################################

@app.post("/items/")
def create_item(item: dict):
    return {"message": "Item créé avec succès", "item": item}

@app.put("/items/{item_id}")
def update_item(item_id: int, item: dict):
    return {"message": "Item mis à jour avec succès", "item_id": item_id, "item": item}

@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    return {"message": "Item {item_id} supprimé avec succès"}
