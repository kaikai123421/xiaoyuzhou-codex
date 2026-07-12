from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class Subscription:
    id: str
    name: str
    rss_url: str
    language: str
    domains: tuple[str, ...]
    quality: float
    xiaoyuzhou_url: str | None = None
    active: bool = True


@dataclass(frozen=True)
class Episode:
    id: str
    subscription_id: str
    podcast_name: str
    title: str
    description: str
    published_at: datetime
    url: str
    audio_url: str | None
    transcript_url: str | None
    xiaoyuzhou_url: str | None
    language: str
    domains: tuple[str, ...]
    quality: float
    duration_seconds: int | None = None
    guest: str | None = None


@dataclass(frozen=True)
class Preferences:
    domain_weights: dict[str, float] = field(default_factory=dict)
    keywords: tuple[str, ...] = ()
    excluded_keywords: tuple[str, ...] = ()
    min_score: float = 0.55
    daily_min: int = 5
    daily_max: int = 8


@dataclass(frozen=True)
class RankedEpisode:
    episode: Episode
    score: float
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class ParsedCommand:
    action: str
    episode_numbers: tuple[int, ...]
    reason: str | None = None


@dataclass(frozen=True)
class DailyReport:
    brief_text: str
    full_markdown: str
    index: dict[str, str]

