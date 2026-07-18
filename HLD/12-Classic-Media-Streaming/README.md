# 12. Classic HLD — Media & Streaming

Upload → process → store → deliver near the user. Interviewers probe **bandwidth, latency, and cost** — not CRUD.

| # | Problem | Crux | Diff |
|---|---------|------|------|
| 01 | [YouTube / Netflix](01_youtube_netflix.md) | CDN + transcoder pipeline | 🔴 |
| 02 | [Image / File Hosting](02_image_file_hosting.md) | Blob storage + edge delivery | 🟡 |
| 03 | [Google Drive / Dropbox](03_google_drive_dropbox.md) | Sync + chunk dedup + conflict | 🔴 |
| 04 | [Live Streaming](04_live_streaming.md) | Real-time ingest + fan-out | 🔴 |

**How to use:** Clarify → estimate bandwidth → draw ingest vs playback paths → deep-dive the crux → name CDN/storage trade-offs out loud.
