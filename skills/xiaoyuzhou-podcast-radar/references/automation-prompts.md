# Automation prompts

## Daily 08:00 Asia/Shanghai

Use `$xiaoyuzhou-podcast-radar` from this repository. Validate configured RSS feeds, collect the previous 24 hours, generate a Chinese digest of 5鈥? qualifying episodes, persist the stable number index, send the brief to the configured Feishu chat, and archive the full report. Continue past individual feed failures and report them. Do not pad a weak digest.

## Hourly command processor

Use `$xiaoyuzhou-podcast-radar` from this repository. Read new messages in the configured Feishu chat, accept `娣辨寲`, `鍠滄`, `璺宠繃`, and `涓嶅枩娆 commands, resolve numbers only against the applicable dated report, process each message idempotently, and reply with results or a precise recoverable error. For deep dives, label whether evidence came from a publisher transcript, captions, audio transcription, or show notes only.

## Weekly discovery

Use `$xiaoyuzhou-podcast-radar` from this repository. Find active, credible Chinese and English podcasts in configured domains, verify public RSS and Xiaoyuzhou availability, score the candidates, and propose additions. Never add or remove a subscription without user approval.


