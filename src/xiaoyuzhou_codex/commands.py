import re

from .models import ParsedCommand


_ACTIONS = {"娣辨寲": "deep_dive", "鍠滄": "like", "璺宠繃": "skip", "涓嶅枩娆?: "dislike"}


def parse_command(text: str) -> ParsedCommand:
    match = re.fullmatch(r"\s*(娣辨寲|鍠滄|璺宠繃|涓嶅枩娆?\s+([0-9,锛屻€乗s]+)(?:\s+(.+))?\s*", text)
    if not match:
        raise ValueError("鏃犳硶璇嗗埆鎸囦护锛涚ず渚嬶細娣辨寲 2銆?")
    numbers = tuple(dict.fromkeys(int(value) for value in re.findall(r"\d+", match.group(2))))
    if not numbers or any(value < 1 for value in numbers):
        raise ValueError("鍗曢泦缂栧彿蹇呴』鏄鏁存暟")
    return ParsedCommand(_ACTIONS[match.group(1)], numbers, match.group(3))


