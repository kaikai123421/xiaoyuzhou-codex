# Configuration

Copy `config/config.example.json` to ignored `config/config.json`. Store QQ 邮箱授权码 and transcription keys only in ignored `private/config.json`, based on `config/private.example.json`.

Subscription fields:

- `id`: stable local identifier.
- `name`: display name.
- `rss_url`: public feed URL.
- `xiaoyuzhou_url`: optional listening entry.
- `language`: `zh` or `en`.
- `domains`: one or more configured domain keys.
- `quality`: editorial prior from 0 to 1.
- `active`: retain disabled sources without deleting them.

Keep AI/technology and business/investing weights highest by default. Treat feedback as a gradual adjustment; do not let one click permanently hide an entire domain.

QQ 邮箱使用 `smtp.qq.com:465` 发送、`imap.qq.com:993` 读取回复。使用授权码而非登录密码；将用户名、授权码和收件地址存于本机环境变量或忽略的私有配置。
