import json
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from .config import load_config
from .models import Preferences, Subscription
from .report import build_daily_report
from .rss import parse_feed
from .scoring import rank_episodes
from .store import StateStore


def local_day(config: dict, now: datetime):
    timezone = config.get("delivery", {}).get("timezone", "Asia/Shanghai")
    return now.astimezone(ZoneInfo(timezone)).date()


def _subscription(item: dict) -> Subscription:
    return Subscription(
        id=item["id"], name=item["name"], rss_url=item["rss_url"],
        language=item.get("language", "zh"), domains=tuple(item.get("domains", [])),
        quality=float(item.get("quality", 0.6)), xiaoyuzhou_url=item.get("xiaoyuzhou_url"),
        active=bool(item.get("active", True)),
    )


def _preferences(config: dict) -> Preferences:
    item = config["preferences"]
    return Preferences(
        domain_weights={key: float(value) for key, value in item["domain_weights"].items()},
        keywords=tuple(item.get("keywords", [])),
        excluded_keywords=tuple(item.get("excluded_keywords", [])),
        min_score=float(item.get("min_score", 0.55)),
        daily_min=int(item.get("daily_min", 5)), daily_max=int(item.get("daily_max", 8)),
    )


def fetch_bytes(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "xiaoyuzhou-codex/0.1"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def collect(config: dict) -> tuple[list, list[dict]]:
    episodes, failures = [], []
    for raw in config.get("subscriptions", []):
        subscription = _subscription(raw)
        if not subscription.active:
            continue
        try:
            episodes.extend(parse_feed(fetch_bytes(subscription.rss_url), subscription))
        except Exception as exc:
            failures.append({"id": subscription.id, "error": str(exc)})
    return episodes, failures


def generate_daily(config: dict, state_path: Path, now: datetime | None = None, *, persist: bool = True):
    now = now or datetime.now(UTC)
    episodes, failures = collect(config)
    ranked = rank_episodes(episodes, _preferences(config), now=now)
    day = local_day(config, now)
    report = build_daily_report([(item.episode, item.score, item.reasons) for item in ranked], day)
    if persist:
        StateStore(state_path).save_report_index(day.isoformat(), report.index)
    return report, failures


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")

