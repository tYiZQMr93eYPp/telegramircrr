from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TorrentMeta(BaseModel):
    model_config = ConfigDict(extra="ignore")

    poster: str | None = None
    genres: str | None = None


class TorrentAttributes(BaseModel):
    model_config = ConfigDict(extra="ignore")

    meta: TorrentMeta = Field(default_factory=TorrentMeta)
    name: str | None = None
    release_year: int | None = None
    category: str | None = None
    type: str | None = None
    resolution: str | None = None
    description: str | None = None
    size: int | None = None
    folder: str | None = None
    freeleech: str | None = None
    double_upload: bool | None = None
    refundable: bool | None = None
    internal: bool | None = None
    featured: bool | None = None
    personal_release: bool | None = None
    uploader: str | None = None
    seeders: int | None = None
    leechers: int | None = None
    times_completed: int | None = None
    tmdb_id: int | None = None
    imdb_id: int | None = None
    tvdb_id: int | None = None
    mal_id: int | None = None
    igdb_id: int | None = None
    isbn13: str | None = None
    asin: str | None = None
    category_id: int | None = None
    type_id: int | None = None
    resolution_id: int | None = None
    created_at: datetime | None = None
    details_link: str | None = None
    download_link: str | None = None
    magnet_link: str | None = None


class Torrent(BaseModel):
    """A torrent resource returned by the UNIT3D `/api/torrents/filter` endpoint."""

    model_config = ConfigDict(extra="ignore")

    type: str | None = None
    id: str
    attributes: TorrentAttributes = Field(default_factory=TorrentAttributes)

    @field_validator("id", mode="before")
    @classmethod
    def _stringify_id(cls, value: object) -> str:
        if value is None:
            raise ValueError("torrent id is required")
        return str(value)
