from datetime import date

from .models import DailyReport, Episode


def _duration(seconds: int | None) -> str:
    if seconds is None:
        return "时长未知"
    return f"约 {max(1, round(seconds / 60))} 分钟"


def build_daily_report(items: list[tuple[Episode, float, tuple[str, ...]]], day: date) -> DailyReport:
    title = f"播客雷达日报｜{day.isoformat()}"
    brief = [title, f"今日精选 {len(items)} 期："]
    full = [f"# {title}", "", "先看摘要，再决定把耳朵借给谁。", ""]
    index: dict[str, str] = {}
    for number, (episode, score, reasons) in enumerate(items, 1):
        key = str(number)
        index[key] = episode.id
        brief.append(f"{number}. {episode.title}｜{episode.podcast_name}｜{score:.2f}")
        full.extend([
            f"## {number}. {episode.title}", "",
            f"- 节目：{episode.podcast_name}",
            f"- 领域：{', '.join(episode.domains)}",
            f"- 语言：{episode.language}｜{_duration(episode.duration_seconds)}",
            f"- 入选理由：{'；'.join(reasons)}",
            f"- 内容速览：{episode.description or '节目未提供简介，建议按标题判断。'}",
            f"- 原始链接：{episode.url}",
            f"- 小宇宙：{episode.xiaoyuzhou_url or '暂未匹配'}", "",
        ])
    brief.append("回复“深挖 1”或“深挖 2、5”继续处理。")
    return DailyReport("\n".join(brief), "\n".join(full), index)
