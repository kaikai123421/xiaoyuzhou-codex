import json
import os
import tempfile
import unittest
from datetime import UTC, datetime
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from xiaoyuzhou_codex.cli import _config, build_parser, main, read_evidence, report_date


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

    def test_config_uses_environment_for_feishu_credentials(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "config.json").write_text(json.dumps({"feishu": {}}), encoding="utf-8")
            (root / "private.json").write_text(json.dumps({"feishu": {"receive_id": "oc_test"}}), encoding="utf-8")
            previous = {key: os.environ.get(key) for key in ("FEISHU_APP_ID", "FEISHU_APP_SECRET")}
            os.environ["FEISHU_APP_ID"] = "env-id"
            os.environ["FEISHU_APP_SECRET"] = "env-secret"
            try:
                config = _config(SimpleNamespace(config=str(root / "config.json"), private_config=str(root / "private.json")))
            finally:
                for key, value in previous.items():
                    if value is None:
                        os.environ.pop(key, None)
                    else:
                        os.environ[key] = value
        self.assertEqual(config["feishu"], {"app_id": "env-id", "app_secret": "env-secret", "receive_id": "oc_test"})

    def test_config_uses_environment_for_qq_mail_delivery(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "config.json").write_text(json.dumps({}), encoding="utf-8")
            previous = {key: os.environ.get(key) for key in ("QQ_SMTP_USERNAME", "QQ_SMTP_AUTH_CODE", "QQ_SMTP_TO")}
            os.environ["QQ_SMTP_USERNAME"] = "sender@qq.com"
            os.environ["QQ_SMTP_AUTH_CODE"] = "auth-code"
            os.environ["QQ_SMTP_TO"] = "reader@qq.com"
            try:
                config = _config(SimpleNamespace(config=str(root / "config.json"), private_config=str(root / "private.json")))
            finally:
                for key, value in previous.items():
                    if value is None:
                        os.environ.pop(key, None)
                    else:
                        os.environ[key] = value
        self.assertEqual(config["email"], {"username": "sender@qq.com", "auth_code": "auth-code", "recipient": "reader@qq.com"})

    def test_process_commands_reads_and_replies_by_email(self):
        class FakeMail:
            def __init__(self):
                self.sent = []

            def list_unseen_messages(self):
                return [{"id": "email-1", "text": "喜欢 3"}]

            def send_text(self, *args):
                self.sent.append(args)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = root / "config.json"
            state = root / "state.json"
            config.write_text(json.dumps({"email": {"recipient": "reader@qq.com"}}), encoding="utf-8")
            fake_mail = FakeMail()
            with patch("xiaoyuzhou_codex.cli._email_client", return_value=fake_mail):
                self.assertEqual(main(["--config", str(config), "--state", str(state), "process-commands"]), 0)
        self.assertEqual(fake_mail.sent[0][0], "reader@qq.com")


if __name__ == "__main__":
    unittest.main()
