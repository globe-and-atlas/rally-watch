---
generated_by: "OpenAI Codex (GPT-6; exact variant not exposed)"
timestamp: "2026-11-05T22:35:07-06:00"
---
# Publish a GIF-first watchface release
- `python3 execution/build_store_media.py`: six exact native palettes;3s first/2.5s later frames;15.5s GIF;four stills;80/144icons.
- `python3 execution/publish.py`: validates a dry-run plan; `--publish` uses signed-in Pebble SDK to create/publish the authorized release.
- Production clean/build strips RALLY_ / TERM_ / LEDGER_ fixture flags before SDK's publish build.
- A publication receipt prevents accidental duplicate uploads. Inspect existing state before retrying an ambiguous result.
- Archive exact SDK-published PBW, not a later rebuild. Store metadata timestamps can change bundle bytes.
- Update both store-release.json and build.json to the exact publishedSHA256; otherwise old local-build hashes become stale.
- `python3 execution/verify_public.py`: publicHTML version/gallery order, exact GIF/PBW bytes andfourPNG RGBmatches.
- Public PBW redirect uses the previously verified RePebble R2storage host; signed query strings are not logged.
- Bounded30s HTTPrequests, transient-only retries andgallerydeduplication have failure-path tests.
- Fresh independent review checks local media and downloaded public proof before completion.
