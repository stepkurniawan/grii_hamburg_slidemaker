from enum import StrEnum
import re
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator

from grii_slide_maker.models.bible import BibleReference


class SongNumber(BaseModel):
    value: str = Field(min_length=1)

    @model_validator(mode="before")
    @classmethod
    def parse_song_number(cls, value: Any) -> Any:
        if isinstance(value, cls):
            return value
        if isinstance(value, int):
            value = str(value)
        if isinstance(value, str):
            song_number = value.strip()
            if not song_number.isdigit():
                raise ValueError("Song number must contain digits only")
            return {"value": song_number}
        return value

    def __str__(self) -> str:
        return self.value


class SongSelection(BaseModel):
    worship_songs: list[SongNumber] = Field(min_length=4, max_length=4)
    holy_communion_song: SongNumber | None = None

    @model_validator(mode="before")
    @classmethod
    def parse_song_selection(cls, value: Any) -> Any:
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            songs: list[str] = []
            holy_communion_song = None
            for song in [song.strip() for song in value.split(",") if song.strip()]:
                # Match "HC" followed by whitespace and one or more digits (e.g., "HC 123")
                holy_communion_match = re.fullmatch(r"HC\s+(\d+)", song, re.IGNORECASE)
                if holy_communion_match:
                    holy_communion_song = holy_communion_match.group(1)
                    continue
                songs.append(song)
            return {"worship_songs": songs, "holy_communion_song": holy_communion_song}
        return value


class Pastor(BaseModel):
    title_id: str = Field(min_length=1)
    title_de_or_en: str = Field(default="Rev.", min_length=1)
    name: str = Field(min_length=1)

    @model_validator(mode="before")
    @classmethod
    def parse_pastor(cls, value: Any) -> Any:
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            parts = value.strip().split(maxsplit=1)
            if len(parts) < 2:
                raise ValueError("Pastor must include a title and full name, for example 'Pdt. Billy Kristanto'")
            return {"title_id": parts[0], "name": parts[1]}
        return value

    @field_validator("title_id", "title_de_or_en", "name")
    @classmethod
    def clean_text(cls, value: str) -> str:
        cleaned = " ".join(value.strip().split())
        if not cleaned:
            raise ValueError("Value cannot be empty")
        return cleaned


class OfferingPurpose(StrEnum):
    P_PENGINJILAN = "P_PENGINJILAN"
    P_SEKOLAH = "P_SEKOLAH"
    P_MANDAT = "P_MANDAT"
    P_PEMBANGUNAN = "P_PEMBANGUNAN"
    P_DIAKONIA = "P_DIAKONIA"


class OrderOfMass(BaseModel):
    songs: SongSelection
    pastor: Pastor
    bible_references: list[BibleReference] = Field(min_length=1)

    @model_validator(mode="before")
    @classmethod
    def parse_streamlit_form(cls, value: Any) -> Any:
        if not isinstance(value, dict):
            return value

        if {"song_numbers", "pastor_name", "bible_verses"} <= value.keys():
            holy_communion_song = value.get("holy_communion_song_number")
            song_selection = SongSelection.model_validate(value["song_numbers"])
            if holy_communion_song not in (None, ""):
                song_selection.holy_communion_song = SongNumber.model_validate(holy_communion_song)

            pastor = Pastor.model_validate(value["pastor_name"])
            pastor.title_de_or_en = value.get("pastor_title") or "Rev."

            raw_bible_verses = value.get("bible_verses") or ""
            bible_references = [
                BibleReference.model_validate(reference.strip())
                for reference in raw_bible_verses.split(",")
                if reference.strip()
            ]

            return {
                "songs": song_selection,
                "pastor": pastor,
                "bible_references": bible_references,
            }

        return value
