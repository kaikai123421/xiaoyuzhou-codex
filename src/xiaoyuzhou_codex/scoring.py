import re
from datetime import UTC, datetime, timedelta

from .models import Episode, Preferences, RankedEpisode


def _dedupe_key(episode: Episode) -> str:
    normalized = re.sub(r"\W+", "", episode.title.casefold())
    return normalized or episode.id


def rank_episodes(
    episodes: list[Episode], preferences: Preferences, *, now: datetime | None = None
) -> list[RankedEpisode]:
    now = now or datetime.now(UTC)
    cutoff = now - timedelta(hours=24)
    seen: set[str] = set()
    ranked: list[RankedEpisode] = []
    for episode in sorted(episodes, key=lambda item: (item.quality, item.published_at), reverse=True):
        key = _dedupe_key(episode)
        if key in seen or episode.published_at < cutoff:
            continue
        seen.add(key)
        haystack = f"{episode.title} {episode.description}".casefold()
        if any(word.casefold() in haystack for word in preferences.excluded_keywords):
            continue
        domain = max((preferences.domain_weights.get(item, 0.0) for item in episode.domains), default=0.0)
        keyword_hits = sum(1 for word in preferences.keywords if word.casefold() in haystack)
        score = min(1.0, episode.quality * 0.45 + domain * 0.35 + min(keyword_hits, 2) * 0.1 + 0.1)
        reasons = []
        if domain >= 0.8:
            reasons.append("AI/绉戞妧楂樺尮閰? if "ai-tech" in episode.domains else "閲嶇偣棰嗗煙楂樺尮閰?)
        if keyword_hits:
            reasons.append("鍛戒腑鍏虫敞鍏抽敭璇?)
        if episode.quality >= 0.8:
            reasons.append("鑺傜洰鍘嗗彶璐ㄩ噺杈冮珮")
        if score >= preferences.min_score:
            ranked.append(RankedEpisode(episode, round(score, 3), tuple(reasons or ["缁煎悎璇勫垎鍏ラ€?])))
    ranked.sort(key=lambda item: (item.score, item.episode.published_at), reverse=True)
    return ranked[: preferences.daily_max]

