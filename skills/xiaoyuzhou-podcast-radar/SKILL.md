---
name: xiaoyuzhou-podcast-radar
description: Use when users ask to discover high-quality Chinese or English podcasts, generate a Chinese podcast digest, track Xiaoyuzhou subscriptions or RSS feeds, deep-dive a numbered episode, or update podcast interests and recommendation feedback.
---

# 灏忓畤瀹欐挱瀹㈤浄杈?
## Overview

Operate an RSS-first podcast radar while preserving Xiaoyuzhou as the listening entry point. Keep discovery, evidence quality, delivery, and feedback explicit; never describe show notes as if the full episode was heard.

## Choose the operation

| User intent | Operation |
|---|---|
| 鈥滄壘楂樿川閲忔挱瀹⑩€?| Run discovery and propose scored sources |
| 鈥滅敓鎴愪粖澶╃殑鎾鏃ユ姤鈥?| Run the daily pipeline |
| 鈥滄繁鎸?2銆?鈥?| Resolve today's stable episode numbers, then deep-dive |
| 鈥滃枩娆?璺宠繃/涓嶅枩娆⑩€?| Record feedback and adjust future weights |
| 鈥滄鏌ヨ闃呮簮鈥?| Validate RSS sources without sending a digest |

## Run safely

1. Read `config/config.json` and `private/config.json`; never print or commit secrets.
2. Validate sources with `python skills/xiaoyuzhou-podcast-radar/scripts/run.py check-sources`.
3. For a daily run, collect only the configured recent window, deduplicate, score, and keep 5鈥? items only when they meet the threshold.
4. Translate English titles and summaries into Chinese while retaining original names and URLs.
5. Send the brief to Feishu and archive the full Markdown using the available Feishu document capability. If no Feishu capability or credentials exist, save the report locally and state the exact missing requirement.
6. Persist the date-to-number index before accepting deep-dive commands. Never infer a number from another day.
7. For deep dives, prefer publisher transcripts, then reliable captions, then permitted audio transcription. Label the evidence source. If only show notes are available, produce a show-notes analysis and say that the full audio was not verified.
8. Record `like`, `skip`, `dislike`, and `deep_dive` feedback without deleting history or sources.

## Output contracts

For the daily digest include: stable number, domain, Chinese title, original title for English items, podcast, guest when known, duration, short summary, recommendation reason, score explanation, original URL, and Xiaoyuzhou URL when matched.

For a deep dive include: executive summary, structure, major claims, evidence and examples, limited verbatim quotes, counterarguments, credibility notes, actions, follow-up questions, WeChat article angles, and knowledge links. Mark medical, psychological, and investment content as informational rather than professional advice.

## Failure rules

- Continue when one feed fails; list failed sources at the end.
- Prefer fewer items over padding a weak digest.
- Make retries idempotent: do not resend a digest or recreate a deep-dive document for the same run key.
- Ask for clarification when a requested number is absent or the report date is ambiguous.
- Never bypass access controls, transcribe inaccessible paid audio, or fabricate timestamps, guests, quotes, or claims.
- Never delete a subscription, report, transcript, or feedback record without explicit user confirmation.

## Resources

Read [configuration.md](references/configuration.md) when setting up sources or delivery. Read [automation-prompts.md](references/automation-prompts.md) when creating the daily and hourly scheduled tasks. Use `scripts/run.py --help` for the deterministic command interface.

The bundled runner delegates to the tested project package; do not duplicate pipeline logic inside the skill.

