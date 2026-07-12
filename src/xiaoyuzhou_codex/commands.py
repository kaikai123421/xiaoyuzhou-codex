import re

from .models import ParsedCommand


_ACTIONS = {"深挖": "deep_dive", "喜欢": "like", "跳过": "skip", "不喜欢": "dislike"}


def parse_command(text: str) -> ParsedCommand:
    match = re.fullmatch(r"\s*(深挖|喜欢|跳过|不喜欢)\s+([0-9,，、\s]+)(?:\s+(.+))?\s*", text)
    if not match:
        raise ValueError("无法识别指令；示例：深挖 2、5")
    numbers = tuple(dict.fromkeys(int(value) for value in re.findall(r"\d+", match.group(2))))
    if not numbers or any(value < 1 for value in numbers):
        raise ValueError("单集编号必须是正整数")
    return ParsedCommand(_ACTIONS[match.group(1)], numbers, match.group(3))

