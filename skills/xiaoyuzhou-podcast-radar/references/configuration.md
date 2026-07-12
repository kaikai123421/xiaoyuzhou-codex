# Configuration

Copy `config/config.example.json` to ignored `config/config.json`. Store Feishu credentials and transcription keys only in ignored `private/config.json`, based on `config/private.example.json`.

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

Feishu requires an app ID, app secret, and destination chat ID. Grant only message read/send and document permissions required for the selected destination.


