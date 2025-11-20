"""
Database Schemas for the streaming app

Each Pydantic model becomes a MongoDB collection with the lowercase class name.
Example: MediaItem -> "mediaitem" collection, Channel -> "channel" collection
"""
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl

class AudioTrack(BaseModel):
    label: str = Field(..., description="Track label, e.g., Original, Audiodescrição")
    url: HttpUrl = Field(..., description="Audio stream/file URL")
    language: Optional[str] = Field(None, description="ISO language code, e.g., pt-BR")
    channels: Optional[str] = Field(None, description="Channel layout, e.g., stereo, 5.1")

class Season(BaseModel):
    number: int
    episodes: int

class MediaItem(BaseModel):
    id: str = Field(..., description="Stable ID for the item")
    title: str
    type: str = Field(..., description="novela|serie|filme|programa")
    synopsis: str
    cast: List[str] = []
    seasons: List[Season] = []
    banner: HttpUrl
    thumb: HttpUrl
    video_url: Optional[HttpUrl] = None
    audio_tracks: List[AudioTrack] = []

class Channel(BaseModel):
    id: str
    name: str
    thumb: HttpUrl
    stream_url: HttpUrl
    alt_audio_url: Optional[HttpUrl] = None
    language: Optional[str] = "pt-BR"
