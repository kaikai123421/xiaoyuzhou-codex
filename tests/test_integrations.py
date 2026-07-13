import json
import tempfile
import unittest
from email.message import EmailMessage
from pathlib import Path

from xiaoyuzhou_codex.config import load_config
from xiaoyuzhou_codex.deep_dive import TranscriptResolver, build_deep_dive_prompt
from xiaoyuzhou_codex.email_delivery import QQMailClient
from xiaoyuzhou_codex.feishu import FeishuClient


class FakeTransport:
    def __init__(self):
        self.calls = []

    def request(self, method, url, *, headers=None, payload=None):
        self.calls.append((method, url, headers or {}, payload))
        if url.endswith("/auth/v3/tenant_access_token/internal"):
            return {"code": 0, "tenant_access_token": "tenant-token", "expire": 7200}
        if "/im/v1/messages" in url and method == "POST":
            return {"code": 0, "data": {"message_id": "m-created"}}
        if "/im/v1/messages" in url and method == "GET":
            return {"code": 0, "data": {"items": [{"message_id": "m-1", "body": {"content": json.dumps({"text": "深挖 2"})}}]}}
        raise AssertionError((method, url))


class ConfigTests(unittest.TestCase):
    def test_loads_public_and_private_config_without_secrets_in_public_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "config.json").write_text(json.dumps({"delivery": {"timezone": "Asia/Shanghai"}}), encoding="utf-8")
            (root / "private.json").write_text(json.dumps({"feishu": {"app_id": "id", "app_secret": "secret", "receive_id": "chat"}}), encoding="utf-8")
            config = load_config(root / "config.json", root / "private.json")
            self.assertEqual(config["feishu"]["receive_id"], "chat")
            self.assertNotIn("app_secret", json.loads((root / "config.json").read_text(encoding="utf-8")))


class FeishuTests(unittest.TestCase):
    def test_sends_text_and_lists_messages(self):
        transport = FakeTransport()
        client = FeishuClient("id", "secret", transport=transport)
        self.assertEqual(client.send_text("chat", "日报"), "m-created")
        messages = client.list_messages("chat")
        self.assertEqual(messages[0]["text"], "深挖 2")
        self.assertTrue(any(call[2].get("Authorization") == "Bearer tenant-token" for call in transport.calls))


class FakeSmtp:
    def __init__(self):
        self.logged_in = None
        self.messages = []

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def login(self, username, password):
        self.logged_in = (username, password)

    def send_message(self, message):
        self.messages.append(message)


class EmailTests(unittest.TestCase):
    def test_sends_utf8_digest_through_qq_smtp(self):
        smtp = FakeSmtp()
        client = QQMailClient("sender@qq.com", "auth-code", smtp_factory=lambda *_: smtp)
        client.send_text("reader@qq.com", "播客日报", "今天的精选内容")
        self.assertEqual(smtp.logged_in, ("sender@qq.com", "auth-code"))
        self.assertEqual(smtp.messages[0]["To"], "reader@qq.com")
        self.assertEqual(smtp.messages[0]["Subject"], "播客日报")
        self.assertIn("今天的精选内容", smtp.messages[0].get_content())

    def test_reads_unseen_email_commands_from_qq_imap(self):
        message = EmailMessage()
        message.set_content("深挖 2、5", charset="utf-8")

        class FakeImap:
            def __init__(self):
                self.stored = []

            def __enter__(self):
                return self

            def __exit__(self, *_):
                return False

            def login(self, *_):
                return "OK", []

            def select(self, *_):
                return "OK", []

            def search(self, *_):
                return "OK", [b"42"]

            def fetch(self, *_):
                return "OK", [(b"42", message.as_bytes())]

            def store(self, *args):
                self.stored.append(args)
                return "OK", []

        imap = FakeImap()
        client = QQMailClient("sender@qq.com", "auth-code", smtp_factory=lambda *_: FakeSmtp(), imap_factory=lambda *_: imap)
        messages = client.list_unseen_messages()
        self.assertEqual(messages, [{"id": "42", "text": "深挖 2、5"}])
        self.assertEqual(imap.stored, [])


class DeepDiveTests(unittest.TestCase):
    def test_prefers_publisher_transcript_over_audio_transcription(self):
        calls = []
        resolver = TranscriptResolver(
            fetch_text=lambda url: calls.append(("text", url)) or "official transcript",
            transcribe_audio=lambda url: calls.append(("audio", url)) or "audio transcript",
        )
        result = resolver.resolve("https://example.com/transcript", "https://example.com/audio.mp3")
        self.assertEqual(result, "official transcript")
        self.assertEqual(calls, [("text", "https://example.com/transcript")])

    def test_deep_dive_prompt_requires_critical_and_wechat_sections(self):
        prompt = build_deep_dive_prompt("Episode", "transcript")
        self.assertIn("值得质疑之处", prompt)
        self.assertIn("公众号选题价值", prompt)
        self.assertIn("不得编造", prompt)

    def test_show_notes_prompt_disclaims_full_audio_review(self):
        prompt = build_deep_dive_prompt("Episode", "notes", evidence_type="show-notes")
        self.assertIn("未核验完整音频", prompt)
        self.assertIn("节目简介与节目笔记", prompt)


if __name__ == "__main__":
    unittest.main()
