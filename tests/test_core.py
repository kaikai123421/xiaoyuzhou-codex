import json
import tempfile
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path

from xiaoyuzhou_codex.commands import parse_command
from xiaoyuzhou_codex.engine import local_day
from xiaoyuzhou_codex.models import Episode, Preferences, Subscription
from xiaoyuzhou_codex.report import build_daily_report
from xiaoyuzhou_codex.rss import parse_feed
from xiaoyuzhou_codex.scoring import rank_episodes
from xiaoyuzhou_codex.store import StateStore


RSS = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel><title>AI Frontiers</title>
<item><guid>ep-1</guid><title>AI agents in business</title>
<link>https://example.com/ep-1</link><description>Practical agent workflows for founders.</description>
<pubDate>Sun, 12 Jul 2026 00:30:00 GMT</pubDate><duration>01:02:03</duration></item>
</channel></rss>"""


class RssTests(unittest.TestCase):
    def test_parses_english_feed_and_duration(self):
        subscription = Subscription(
            id="ai-frontiers", name="AI Frontiers", rss_url="https://example.com/rss",
            language="en", domains=("ai-tech",), quality=0.9,
            xiaoyuzhou_url="https://www.xiaoyuzhoufm.com/podcast/example",
        )
        episodes = parse_feed(RSS.encode(), subscription)
        self.assertEqual(len(episodes), 1)
        self.assertEqual(episodes[0].duration_seconds, 3723)
        self.assertEqual(episodes[0].language, "en")
        self.assertEqual(episodes[0].xiaoyuzhou_url, subscription.xiaoyuzhou_url)

    def test_daily_date_uses_configured_timezone(self):
        now = datetime(2026, 7, 11, 17, tzinfo=UTC)
        config = {"delivery": {"timezone": "Asia/Shanghai"}}
        self.assertEqual(local_day(config, now).isoformat(), "2026-07-12")


class ScoringTests(unittest.TestCase):
    def test_filters_old_duplicate_and_low_score_episodes(self):
        now = datetime(2026, 7, 12, 8, tzinfo=UTC)
        prefs = Preferences(
            domain_weights={"ai-tech": 1.0, "health-science": 0.5},
            keywords=("agent",), excluded_keywords=("celebrity gossip",),
            min_score=0.55, daily_min=1, daily_max=5,
        )
        recent = Episode(
            id="same", subscription_id="s1", podcast_name="P1", title="AI agent playbook",
            description="Practical business systems", published_at=now - timedelta(hours=1),
            url="https://a/1", audio_url=None, transcript_url=None,
            xiaoyuzhou_url=None, language="en", domains=("ai-tech",), quality=0.9,
        )
        duplicate = Episode(**{**recent.__dict__, "id": "different-guid", "subscription_id": "s2", "url": "https://b/1"})
        old = Episode(**{**recent.__dict__, "id": "old", "published_at": now - timedelta(days=3)})
        ranked = rank_episodes([old, duplicate, recent], prefs, now=now)
        self.assertEqual(len(ranked), 1)
        self.assertEqual(ranked[0].episode.title, "AI agent playbook")
        self.assertTrue(ranked[0].reasons)


class CommandTests(unittest.TestCase):
    def test_parses_multiple_deep_dive_ids(self):
        command = parse_command("娣辨寲 2銆?")
        self.assertEqual(command.action, "deep_dive")
        self.assertEqual(command.episode_numbers, (2, 5))

    def test_parses_negative_feedback_reason(self):
        command = parse_command("涓嶅枩娆?6 鍐呭澶硾")
        self.assertEqual(command.action, "dislike")
        self.assertEqual(command.episode_numbers, (6,))
        self.assertEqual(command.reason, "鍐呭澶硾")


class StoreAndReportTests(unittest.TestCase):
    def test_idempotent_message_processing(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = StateStore(Path(tmp) / "state.json")
            self.assertTrue(store.claim_message("m-1"))
            self.assertFalse(store.claim_message("m-1"))

    def test_report_has_stable_numbers_and_chinese_sections(self):
        now = datetime(2026, 7, 12, 8, tzinfo=UTC)
        episode = Episode(
            id="ep-1", subscription_id="p1", podcast_name="AI Frontiers",
            title="AI agents in business", description="Agent workflows",
            published_at=now, url="https://example.com/ep-1", audio_url=None,
            transcript_url=None, xiaoyuzhou_url="https://www.xiaoyuzhoufm.com/episode/1",
            language="en", domains=("ai-tech",), quality=0.9,
        )
        report = build_daily_report([(episode, 0.88, ("AI/绉戞妧楂樺尮閰?,))], now.date())
        self.assertIn("1. AI agents in business", report.full_markdown)
        self.assertIn("鍥炲鈥滄繁鎸?1鈥?, report.brief_text)
        self.assertEqual(report.index["1"], "ep-1")
        json.dumps(report.index)


if __name__ == "__main__":
    unittest.main()

