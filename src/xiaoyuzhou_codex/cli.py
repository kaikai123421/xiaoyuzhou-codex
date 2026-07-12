import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from .commands import parse_command
from .config import load_config
from .deep_dive import build_deep_dive_prompt
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
    parser = argparse.ArgumentParser(prog="xyz-codex", description="灏忓畤瀹欐挱瀹㈤浄杈?)
    parser.add_argument("--config", default="config/config.json")
    parser.add_argument("--private-config", default="private/config.json")
    parser.add_argument("--state", default="private/state.json")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("check-sources")
    daily = commands.add_parser("daily")
    daily.add_argument("--dry-run", action="store_true", help="鍙瑙堬紝涓嶅啓鐘舵€佹垨鍙戦€侀涔?)
    commands.add_parser("process-commands")
    deep = commands.add_parser("deep-dive")
    deep.add_argument("--title", default="寰呮繁鎸栧崟闆?)
    deep.add_argument("--transcript", default="-")
    deep.add_argument("--evidence-type", choices=("transcript", "captions", "audio-transcription", "show-notes"), default="transcript")
    commands.add_parser("discover")
    return parser


def _config(args) -> dict:
    private = Path(args.private_config)
    return load_config(Path(args.config), private if private.exists() else None)


def _client(config: dict) -> FeishuClient:
    feishu = config.get("feishu", {})
    missing = [key for key in ("app_id", "app_secret", "receive_id") if not feishu.get(key)]
    if missing:
        raise RuntimeError(f"椋炰功閰嶇疆缂哄け锛歿', '.join(missing)}")
    return FeishuClient(feishu["app_id"], feishu["app_secret"])


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
        if not args.dry_run and config.get("feishu", {}).get("receive_id"):
            _client(config).send_text(config["feishu"]["receive_id"], report.brief_text)
        return 1 if failures and not report.index else 0
    if args.command == "process-commands":
        client = _client(config)
        today = report_date(config)
        index = state.get_report_index(today)
        for message in reversed(client.list_messages(config["feishu"]["receive_id"])):
            if not message["text"] or not state.claim_message(message["id"]):
                continue
            try:
                command = parse_command(message["text"])
            except ValueError:
                continue
            selected = [index.get(str(number)) for number in command.episode_numbers]
            state.add_feedback({"action": command.action, "episodes": selected, "reason": command.reason, "message_id": message["id"]})
            client.send_text(config["feishu"]["receive_id"], f"宸茶褰曪細{message['text']}銆傛繁鎸栦换鍔″皢鍦ㄦ湰杞敓鎴愩€?)
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

