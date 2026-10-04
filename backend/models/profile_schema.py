"""
profile_schema.py
-----------------
The project's DATA CONTRACT: a platform-independent schema for exported
profile metadata and posts, used by the file-driven exposure rubric.

Only SYNTHETIC or self-owned exported files are ever analysed. The schema
intentionally tolerates missing fields so that a minimal, privacy-friendly
export is still analysable.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class PrivacySettings(BaseModel):
    account_private: bool = False
    show_activity: bool = True
    allow_message_requests: bool = True


class SiteMeta(BaseModel):
    """Self-reported information about a linked website (no crawling)."""
    has_privacy_policy: bool = False
    third_party_scripts: List[str] = Field(default_factory=list)


class Profile(BaseModel):
    platform: str = "unknown"
    username: Optional[str] = None
    display_name: Optional[str] = None
    bio: Optional[str] = ""
    website: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    birthday: Optional[str] = None
    location: Optional[str] = None
    privacy: PrivacySettings = Field(default_factory=PrivacySettings)
    links: List[str] = Field(default_factory=list)
    site_meta: Optional[SiteMeta] = None
    handle_reused_elsewhere: bool = False

    model_config = {"extra": "allow"}


class Geo(BaseModel):
    lat: Optional[float] = None
    lon: Optional[float] = None

    model_config = {"extra": "allow"}


class Media(BaseModel):
    type: str = "none"
    has_faces: bool = False
    is_child_present: bool = False
    exif: Dict[str, Any] = Field(default_factory=dict)

    model_config = {"extra": "allow"}


class Post(BaseModel):
    id: str = "post"
    text: Optional[str] = ""
    created_at: Optional[str] = None
    hashtags: List[str] = Field(default_factory=list)
    mentions: List[str] = Field(default_factory=list)
    geo: Optional[Geo] = None
    media: Media = Field(default_factory=Media)

    model_config = {"extra": "allow"}


class AnalyzePayload(BaseModel):
    """Body of POST /api/analyze."""
    profile: Dict[str, Any]
    posts: List[Dict[str, Any]] = Field(default_factory=list)
    caps: Optional[Dict[str, int]] = None
