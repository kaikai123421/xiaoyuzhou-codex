import json
import os
import tempfile
from pathlib import Path


class StateStore:
    def __init__(self, path: Path):
        self.path = path

    def _read(self) -> dict:
        if not self.path.exists():
            return {"processed_messages": [], "reports": {}, "feedback": []}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _write(self, data: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(dir=self.path.parent, prefix="state-", suffix=".json")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(data, handle, ensure_ascii=False, indent=2)
            os.replace(temporary, self.path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)

    def claim_message(self, message_id: str) -> bool:
        data = self._read()
        if message_id in data["processed_messages"]:
            return False
        data["processed_messages"].append(message_id)
        self._write(data)
        return True

    def save_report_index(self, date: str, index: dict[str, str]) -> None:
        data = self._read()
        data["reports"][date] = index
        self._write(data)

    def get_report_index(self, date: str) -> dict[str, str]:
        return self._read()["reports"].get(date, {})

    def add_feedback(self, item: dict) -> None:
        data = self._read()
        data["feedback"].append(item)
        self._write(data)


