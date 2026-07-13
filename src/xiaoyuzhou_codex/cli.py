import argparse
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from .commands import parse_command
from .config import load_config
from .deep_dive import build_deep_dive_prompt
from .email_delivery import QQMailClient
from .engine import collect, generate_daily
from .feishu import FeishuClient
from .store import StateStore


def report_date(config: dict, now: datetime | None = None) -> str:
    now = now or datetime.now(UTC)
    timezone = config.get("delivery", {}).get("timezone", "Asia/Shanghai")
    return now.astimezone(ZoneInfo(timezone)).date().isoformat()


def read_evidence(path: str) -> str:
    return sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="xyz-codex", description="小宇宙播客雷达")
    parser.add_argument("--config", default="config/config.json")
    parser.add_argument("--private-config", default="private/config.json")
    parser.add_argument("--state", default="private/state.json")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("check-sources")
    daily = commands.add_parser("daily")
    daily.add_argument("--dry-run", action="store_true", help="只预览，不写状态或发送飞书")
    commands.add_parser("process-commands")
    deep = commands.add_parser("deep-dive")
    deep.add_argument("--title", default="待深挖单集")
    deep.add_argument("--transcript", default="-")
    deep.add_argument("--evidence-type", choices=("transcript", "captions", "audio-transcription", "show-notes"), default="transcript")
    commands.add_parser("discover")
    return parser


def _config(args) -> dict:
    private = Path(args.private_config)
    config = load_config(Path(args.config), private if private.exists() else None)
    feishu = config.setdefault("feishu", {})
    for key, variable in (("app_id", "FEISHU_APP_ID"), ("app_secret", "FEISHU_APP_SECRET")):
        if not feishu.get(key) and os.environ.get(variable):
            feishu[key] = os.environ[variable]
    email = config.setdefault("email", {})
    for key, variable in (("username", "QQ_SMTP_USERNAME"), ("auth_code", "QQ_SMTP_AUTH_CODE"), ("recipient", "QQ_SMTP_TO")):
        if not email.get(key) and os.environ.get(variable):
            email[key] = os.environ[variable]
    return config


def _client(config: dict) -> FeishuClient:
    feishu = config.get("feishu", {})
    missing = [key for key in ("app_id", "app_secret", "receive_id") if not feishu.get(key)]
    if missing:
        raise RuntimeError(f"飞书配置缺失：{', '.join(missing)}")
    return FeishuClient(feishu["app_id"], feishu["app_secret"])


def _email_client(config: dict) -> QQMailClient:
    email = config.get("email", {})
    missing = [key for key in ("username", "auth_code", "recipient") if not email.get(key)]
    if missing:
        raise RuntimeError(f"邮箱配置缺失：{', '.join(missing)}")
    return QQMailClient(email["username"], email["auth_code"])


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    config = _config(args)
    state = StateStore(Path(args.state))
    if args.command == "check-sources":
        episodes, failures = collect(config)
        print(json.dumps({"episodes": len(episodes), "failures": failures}, ensure_ascii=False, indent=2))
        return 1 if failures else 0
    if args.command == "daily":
        report, failures = generate_daily(config, Path(args.state), persist=not args.dry_run)
        print(report.full_markdown)
        if not args.dry_run and config.get("email", {}).get("recipient"):
            _email_client(config).send_text(config["email"]["recipient"], f"播客日报｜{report_date(config)}", report.brief_text)
        elif not args.dry_run and config.get("feishu", {}).get("receive_id"):
            _client(config).send_text(config["feishu"]["receive_id"], report.brief_text)
        return 1 if failures and not report.index else 0
    if args.command == "process-commands":
        email = config.get("email", {})
        email_client = _email_client(config) if email.get("recipient") else None
        client = None if email_client else _client(config)
        today = report_date(config)
        index = state.get_report_index(today)
        messages = email_client.list_unseen_messages() if email_client else client.list_messages(config["feishu"]["receive_id"])
        for message in reversed(messages):
            if not message["text"] or not state.claim_message(message["id"]):
                continue
            try:
                command = parse_command(message["text"])
            except ValueError:
                continue
            selected = [index.get(str(number)) for number in command.episode_numbers]
            state.add_feedback({"action": command.action, "episodes": selected, "reason": command.reason, "message_id": message["id"]})
            reply = f"已记录：{message['text']}。深挖任务将在本轮生成。"
            if email_client:
                email_client.send_text(email["recipient"], "播客雷达｜已收到你的指令", reply)
            else:
                client.send_text(config["feishu"]["receive_id"], reply)
        return 0
    if args.command == "deep-dive":
        transcript = read_evidence(args.transcript)
        print(build_deep_dive_prompt(args.title, transcript, evidence_type=args.evidence_type))
        return 0
    if args.command == "discover":
        print(json.dumps(config.get("discovery_candidates", []), ensure_ascii=False, indent=2))
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
