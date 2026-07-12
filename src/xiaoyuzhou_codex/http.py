import json
import urllib.request


class JsonTransport:
    def request(self, method: str, url: str, *, headers=None, payload=None) -> dict:
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(url, data=data, method=method, headers=headers or {})
        if data is not None:
            request.add_header("Content-Type", "application/json; charset=utf-8")
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))

