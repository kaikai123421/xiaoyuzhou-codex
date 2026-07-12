import json
import time
import urllib.parse

from .http import JsonTransport


class FeishuClient:
    BASE_URL = "https://open.feishu.cn/open-apis"

    def __init__(self, app_id: str, app_secret: str, *, transport=None):
        self.app_id = app_id
        self.app_secret = app_secret
        self.transport = transport or JsonTransport()
        self._token: str | None = None
        self._token_expires = 0.0

    def _tenant_token(self) -> str:
        if self._token and time.time() < self._token_expires:
            return self._token
        result = self.transport.request(
            "POST", f"{self.BASE_URL}/auth/v3/tenant_access_token/internal",
            payload={"app_id": self.app_id, "app_secret": self.app_secret},
        )
        if result.get("code") != 0:
            raise RuntimeError(f"飞书鉴权失败：{result.get('msg', result.get('code'))}")
        self._token = result["tenant_access_token"]
        self._token_expires = time.time() + max(60, int(result.get("expire", 7200)) - 60)
        return self._token

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._tenant_token()}"}

    def send_text(self, receive_id: str, text: str, *, receive_id_type: str = "chat_id") -> str:
        query = urllib.parse.urlencode({"receive_id_type": receive_id_type})
        result = self.transport.request(
            "POST", f"{self.BASE_URL}/im/v1/messages?{query}", headers=self._headers(),
            payload={"receive_id": receive_id, "msg_type": "text", "content": json.dumps({"text": text}, ensure_ascii=False)},
        )
        if result.get("code") != 0:
            raise RuntimeError(f"飞书发送失败：{result.get('msg', result.get('code'))}")
        return result["data"]["message_id"]

    def list_messages(self, container_id: str, *, page_size: int = 50) -> list[dict]:
        query = urllib.parse.urlencode({"container_id_type": "chat", "container_id": container_id, "sort_type": "ByCreateTimeDesc", "page_size": page_size})
        result = self.transport.request("GET", f"{self.BASE_URL}/im/v1/messages?{query}", headers=self._headers())
        if result.get("code") != 0:
            raise RuntimeError(f"飞书读取消息失败：{result.get('msg', result.get('code'))}")
        messages = []
        for item in result.get("data", {}).get("items", []):
            content = json.loads(item.get("body", {}).get("content", "{}"))
            messages.append({"id": item.get("message_id"), "text": content.get("text", ""), "raw": item})
        return messages

