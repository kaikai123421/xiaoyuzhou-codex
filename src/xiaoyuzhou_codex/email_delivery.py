import imaplib
import smtplib
from email import message_from_bytes
from email.message import EmailMessage


class QQMailClient:
    def __init__(self, username: str, auth_code: str, *, smtp_factory=smtplib.SMTP_SSL, imap_factory=imaplib.IMAP4_SSL):
        self.username = username
        self.auth_code = auth_code
        self.smtp_factory = smtp_factory
        self.imap_factory = imap_factory

    def send_text(self, recipient: str, subject: str, text: str) -> None:
        message = EmailMessage()
        message["From"] = self.username
        message["To"] = recipient
        message["Subject"] = subject
        message.set_content(text, charset="utf-8")
        with self.smtp_factory("smtp.qq.com", 465) as smtp:
            smtp.login(self.username, self.auth_code)
            smtp.send_message(message)

    def list_unseen_messages(self) -> list[dict[str, str]]:
        messages: list[dict[str, str]] = []
        with self.imap_factory("imap.qq.com", 993) as imap:
            imap.login(self.username, self.auth_code)
            imap.select("INBOX")
            status, data = imap.search(None, "UNSEEN")
            if status != "OK":
                raise RuntimeError("QQ 邮箱收件查询失败")
            for message_id in data[0].split():
                status, payload = imap.fetch(message_id, "(RFC822)")
                if status != "OK" or not payload:
                    continue
                raw = next((item[1] for item in payload if isinstance(item, tuple) and len(item) > 1), b"")
                message = message_from_bytes(raw)
                messages.append({"id": message_id.decode(), "text": self._body_text(message)})
        return messages

    @staticmethod
    def _body_text(message) -> str:
        parts = message.walk() if message.is_multipart() else [message]
        for part in parts:
            if part.get_content_type() != "text/plain" or part.get_content_disposition() == "attachment":
                continue
            payload = part.get_payload(decode=True) or b""
            return payload.decode(part.get_content_charset() or "utf-8", errors="replace").strip()
        return ""
