from datetime import date

from .models import DailyReport, Episode


def _duration(seconds: int | None) -> str:
    if seconds is None:
        return "鏃堕暱鏈煡"
    return f"绾?{max(1, round(seconds / 60))} 鍒嗛挓"


def build_daily_report(items: list[tuple[Episode, float, tuple[str, ...]]], day: date) -> DailyReport:
    title = f"鎾闆疯揪鏃ユ姤锝渰day.isoformat()}"
    brief = [title, f"浠婃棩绮鹃€?{len(items)} 鏈燂細"]
    full = [f"# {title}", "", "鍏堢湅鎽樿锛屽啀鍐冲畾鎶婅€虫湹鍊熺粰璋併€?, ""]
    index: dict[str, str] = {}
    for number, (episode, score, reasons) in enumerate(items, 1):
        key = str(number)
        index[key] = episode.id
        brief.append(f"{number}. {episode.title}锝渰episode.podcast_name}锝渰score:.2f}")
        full.extend([
            f"## {number}. {episode.title}", "",
            f"- 鑺傜洰锛歿episode.podcast_name}",
            f"- 棰嗗煙锛歿', '.join(episode.domains)}",
            f"- 璇█锛歿episode.language}锝渰_duration(episode.duration_seconds)}",
            f"- 鍏ラ€夌悊鐢憋細{'锛?.join(reasons)}",
            f"- 鍐呭閫熻锛歿episode.description or '鑺傜洰鏈彁渚涚畝浠嬶紝寤鸿鎸夋爣棰樺垽鏂€?}",
            f"- 鍘熷閾炬帴锛歿episode.url}",
            f"- 灏忓畤瀹欙細{episode.xiaoyuzhou_url or '鏆傛湭鍖归厤'}", "",
        ])
    brief.append("鍥炲鈥滄繁鎸?1鈥濇垨鈥滄繁鎸?2銆?鈥濈户缁鐞嗐€?)
    return DailyReport("\n".join(brief), "\n".join(full), index)

