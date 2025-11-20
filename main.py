import os
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import db, create_document, get_documents
from schemas import MediaItem, Channel

app = FastAPI(title="Globoplay Inspired Streaming API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CreateMediaItem(BaseModel):
    item: MediaItem

class CreateChannel(BaseModel):
    channel: Channel

@app.get("/")
def root():
    return {"status": "ok", "service": "streaming-api"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set",
        "database_name": "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Connected"
            response["collections"] = db.list_collection_names()[:10]
        else:
            response["database"] = "❌ Not Connected"
    except Exception as e:
        response["database"] = f"⚠️ {str(e)[:80]}"
    return response

# Seed demo content if collections are empty
@app.post("/seed")
def seed_demo():
    try:
        if db is None:
            raise HTTPException(status_code=500, detail="Database not configured")
        collections = db.list_collection_names()
        if "mediaitem" not in collections:
            demo_items: List[dict] = [
                {
                    "id": "novela-1",
                    "title": "Amor em Vermelho",
                    "type": "novela",
                    "synopsis": "Uma história de paixão e segredos.",
                    "cast": ["Ana Souza", "Carlos Lima"],
                    "seasons": [{"number": 1, "episodes": 20}],
                    "banner": "https://images.unsplash.com/photo-1517604931442-7e0c8ed2963f?q=80&w=1600&auto=format&fit=crop",
                    "thumb": "https://images.unsplash.com/photo-1512428559087-560fa5ceab42?q=80&w=600&auto=format&fit=crop",
                    "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
                    "audio_tracks": [
                        {"label": "Original", "url": "https://www2.cs.uic.edu/~i101/SoundFiles/StarWars60.wav", "language": "pt-BR", "channels": "stereo"},
                        {"label": "Audiodescrição", "url": "https://www2.cs.uic.edu/~i101/SoundFiles/ImperialMarch60.wav", "language": "pt-BR", "channels": "stereo"}
                    ]
                },
                {
                    "id": "serie-1",
                    "title": "Código 5.1",
                    "type": "serie",
                    "synopsis": "Suspense tecnológico com áudio imersivo.",
                    "cast": ["Marina Dias", "João Pedro"],
                    "seasons": [{"number": 1, "episodes": 8}],
                    "banner": "https://images.unsplash.com/photo-1526948128573-703ee1aeb6fa?q=80&w=1600&auto=format&fit=crop",
                    "thumb": "https://images.unsplash.com/photo-1515378791036-0648a3ef77b2?q=80&w=600&auto=format&fit=crop",
                    "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
                    "audio_tracks": [
                        {"label": "Original 5.1", "url": "https://www2.cs.uic.edu/~i101/SoundFiles/CantinaBand60.wav", "language": "en", "channels": "5.1"}
                    ]
                },
            ]
            for d in demo_items:
                create_document("mediaitem", d)
        if "channel" not in collections:
            demo_channels = [
                {
                    "id": "globo",
                    "name": "Globo Ao Vivo",
                    "thumb": "https://images.unsplash.com/photo-1522770179533-24471fcdba45?q=80&w=600&auto=format&fit=crop",
                    "stream_url": "https://stream.mux.com/taW02VhFI02o02.m3u8",
                    "alt_audio_url": "https://www2.cs.uic.edu/~i101/SoundFiles/Front_Center.wav"
                },
                {
                    "id": "sportv",
                    "name": "SporTV",
                    "thumb": "https://images.unsplash.com/photo-1517649763962-0c623066013b?q=80&w=600&auto=format&fit=crop",
                    "stream_url": "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8"
                }
            ]
            for ch in demo_channels:
                create_document("channel", ch)
        return {"seeded": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/home")
def home():
    """Return grouped carousels for Home: novelas, series, filmes, programas, canais"""
    try:
        novelas = get_documents("mediaitem", {"type": "novela"}, limit=12)
        series = get_documents("mediaitem", {"type": "serie"}, limit=12)
        filmes = get_documents("mediaitem", {"type": "filme"}, limit=12)
        programas = get_documents("mediaitem", {"type": "programa"}, limit=12)
        canais = get_documents("channel", {}, limit=12)
        return {
            "novelas": novelas,
            "series": series,
            "filmes": filmes,
            "programas": programas,
            "canais": canais
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/item/{item_id}")
def item_detail(item_id: str):
    try:
        data = db["mediaitem"].find_one({"id": item_id}) if db else None
        if not data:
            raise HTTPException(status_code=404, detail="Item não encontrado")
        data["_id"] = str(data["_id"]) if "_id" in data else None
        return data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/channels")
def channels():
    try:
        return get_documents("channel", {}, limit=50)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
