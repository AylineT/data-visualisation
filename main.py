from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
from typing import Dict, List

app = FastAPI()

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Chargement des données
df = pd.read_csv("csv/spotify_tracks.csv")

@app.get("/songs-by-year")
async def get_songs_by_year():
    try:
        yearly_counts = df['year'].value_counts().sort_index()
        return {"songsByYear": yearly_counts.to_dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/artist/{year}")
async def get_artist_songs(year: str):
    try:
        if not year.isdigit():
            raise HTTPException(status_code=400, detail="Year must be a number")
        year_df = df[df['year'] == int(year)]
        if year_df.empty:
            raise HTTPException(status_code=404, detail=f"No data found for year {year}")
        # Nettoyer les noms d'artistes avant le comptage
        year_df['artist_name'] = year_df['artist_name'].apply(lambda x: x.strip("[]'\"").split(",")[0].strip())
        artist_counts = year_df['artist_name'].value_counts()
        return {"songsPerArtist": artist_counts.head(10).to_dict()}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/acousticness-per-year")
async def get_acousticness_by_year():
    try:
        yearly_acousticness = df.groupby('year')['acousticness'].mean().sort_index()
        return {"average_acousticness": yearly_acousticness.to_dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/danceability-per-year")
async def get_danceability_by_year():
    try:
        yearly_danceability = df.groupby('year')['danceability'].mean().sort_index()
        return {"average_danceability": yearly_danceability.to_dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/danceability-and-valence")
async def get_danceability_and_valence():
    try:
        # Filtrer les valeurs aberrantes
        filtered_df = df[
            (df['danceability'] >= 0) & 
            (df['danceability'] <= 1) & 
            (df['valence'] >= 0) & 
            (df['valence'] <= 1)
        ]

        # Créer une grille 20x20 pour la heatmap
        x_bins = np.linspace(0, 1, 21)
        y_bins = np.linspace(0, 1, 21)
        
        # Calculer la densité des points
        heatmap, x_edges, y_edges = np.histogram2d(
            filtered_df['danceability'],
            filtered_df['valence'],
            bins=[x_bins, y_bins]
        )
        
        # Créer les points pour la heatmap
        data = []
        for i in range(len(x_edges)-1):
            for j in range(len(y_edges)-1):
                if heatmap[i][j] > 0:  # Ne garder que les cellules non vides
                    data.append({
                        "x": float(x_edges[i]),
                        "y": float(y_edges[j]),
                        "density": float(heatmap[i][j])
                    })
        
        return {
            "data": data,
            "maxDensity": float(heatmap.max())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/popularity-vs-tempo")
async def get_popularity_by_tempo():
    try:
        # Calculer la moyenne de popularité par tranche de tempo
        tempo_bins = pd.cut(df['tempo'], bins=50)  # Diviser en 50 tranches
        tempo_stats = df.groupby(tempo_bins).agg({
            'tempo': 'mean',
            'popularity': 'mean'
        }).dropna()

        # Appliquer une moyenne mobile pour lisser la courbe
        tempo_stats['popularity'] = tempo_stats['popularity'].rolling(window=3, center=True).mean()

        data = [
            {
                "tempo": float(row.tempo),
                "popularity": float(row.popularity)
            }
            for _, row in tempo_stats.iterrows() if not pd.isna(row.popularity)
        ]
        
        return {"data": sorted(data, key=lambda x: x["tempo"])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/top-10-popular")
async def get_top_10_popular():
    try:
        top_tracks = df.nlargest(10, 'popularity')[
            ['track_name', 'artist_name', 'popularity', 'artwork_url']
        ].to_dict('records')
        return [
            {
                "name": track['track_name'],
                "artists": track['artist_name'],
                "popularity": int(track['popularity']),
                "artwork_url": track['artwork_url']
            }
            for track in top_tracks
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/top-10-dance")
async def get_top_10_dance():
    try:
        dance_score = df['danceability'] * 0.6 + df['energy'] * 0.4
        top_tracks = df.loc[dance_score.nlargest(10).index][
            ['track_name', 'artist_name', 'danceability', 'energy', 'artwork_url']
        ].to_dict('records')
        return [
            {
                "name": track['track_name'],
                "artists": track['artist_name'],
                "danceability": float(track['danceability']),
                "artwork_url": track['artwork_url']
            }
            for track in top_tracks
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/top-10-relaxing")
async def get_top_10_relaxing():
    try:
        relax_score = (1 - df['energy']) * 0.5 + df['acousticness'] * 0.5
        top_tracks = df.loc[relax_score.nlargest(10).index][
            ['track_name', 'artist_name', 'acousticness', 'energy', 'artwork_url']
        ].to_dict('records')
        return [
            {
                "name": track['track_name'],
                "artists": track['artist_name'],
                "acousticness": float(track['acousticness']),
                "energy": float(track['energy']),
                "artwork_url": track['artwork_url']
            }
            for track in top_tracks
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/top-10-longest")
async def get_top_10_longest():
    try:
        top_tracks = df.nlargest(10, 'duration_ms')[
            ['track_name', 'artist_name', 'duration_ms', 'artwork_url']
        ].to_dict('records')
        return [
            {
                "name": track['track_name'],
                "artists": track['artist_name'],
                "duration_ms": int(track['duration_ms']),
                "artwork_url": track['artwork_url']
            }
            for track in top_tracks
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/popularity-per-language")
async def get_popularity_by_language():
    try:
        language_stats = df.groupby('language')['popularity'].mean().sort_values(ascending=False)
        return {"popularity_per_language": language_stats.to_dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
