import email.utils
import hashlib
import re
import xml.etree.ElementTree as ET
from datetime import UTC, datetime

from .models import Episode, Subscription


def _text(element: ET.Element, *names: str) -> str:
    for name in names:
        found = element.find(name)
        if found is not None and found.text:
            return found.text.strip()
    return ""


def _duration_seconds(value: str) -> int | None:
    if not value:
        return None
    if value.isdigit():
        return int(value)
    parts = value.split(":")
    if not all(part.isdigit() for part in parts) or len(parts) not in (2, 3):
        return None
    numbers = [int(part) for part in parts]
    if len(numbers) == 2:
        return numbers[0] * 60 + numbers[1]
    return numbers[0] * 3600 + numbers[1] * 60 + numbers[2]


def _published(value: str) -> datetime:
    parsed = email.utils.parsedate_to_datetime(value) if value else None
    if parsed is None:
        return datetime.now(UTC)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _clean_html(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", value)).strip()


def parse_feed(data: bytes, subscription: Subscription) -> list[Episode]:
    root = ET.fromstring(data)
    channel = root.find("channel")
    items = channel.findall("item") if channel is not None else []
    episodes: list[Episode] = []
    for item in items:
        title = _text(item, "title") or "鏈懡鍚嶅崟闆?
        link = _text(item, "link")
        guid = _text(item, "guid") or link or hashlib.sha256(title.encode()).hexdigest()
        enclosure = item.find("enclosure")
        audio_url = enclosure.get("url") if enclosure is not None else None
        duration = _text(item, "{http://www.itunes.com/dtds/podcast-1.0.dtd}duration", "duration")
        transcript = item.find("{https://podcastindex.org/namespace/1.0}transcript")
        episodes.append(Episode(
            id=guid,
            subscription_id=subscription.id,
            podcast_name=subscription.name,
            title=title,
            description=_clean_html(_text(item, "description", "{http://purl.org/rss/1.0/modules/content/}encoded")),
            published_at=_published(_text(item, "pubDate")),
            url=link or guid,
            audio_url=audio_url,
            transcript_url=transcript.get("url") if transcript is not None else None,
            xiaoyuzhou_url=subscription.xiaoyuzhou_url,
            language=subscription.language,
            domains=subscription.domains,
            quality=subscription.quality,
            duration_seconds=_duration_seconds(duration),
        ))
    return episodes


