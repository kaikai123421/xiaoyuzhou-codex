import unittest
from datetime import UTC, datetime
from io import StringIO
from unittest.mock import patch

from xiaoyuzhou_codex.cli import build_parser, read_evidence, report_date


class CliTests(unittest.TestCase):
    def test_exposes_all_operational_commands(self):
        parser = build_parser()
        for command in ("check-sources", "daily", "process-commands", "deep-dive", "discover"):
            args = parser.parse_args([command])
            self.assertEqual(args.command, command)

    def test_report_date_uses_configured_timezone(self):
        now = datetime(2026, 7, 11, 17, tzinfo=UTC)
        self.assertEqual(report_date({"delivery": {"timezone": "Asia/Shanghai"}}, now), "2026-07-12")

    def test_daily_supports_side_effect_free_preview(self):
        args = build_parser().parse_args(["daily", "--dry-run"])
        self.assertTrue(args.dry_run)

    def test_deep_dive_requires_evidence_label(self):
        args = build_parser().parse_args(["deep-dive", "--evidence-type", "show-notes"])
        self.assertEqual(args.evidence_type, "show-notes")

    def test_stdin_evidence_reads_all_lines(self):
        with patch("sys.stdin", StringIO("line one\nline two\n")):
            self.assertEqual(read_evidence("-"), "line one\nline two\n")


if __name__ == "__main__":
    unittest.main()
