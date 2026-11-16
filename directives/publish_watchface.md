---
generated_by: "OpenAI Codex (GPT-6; exact variant not exposed)"
timestamp: "2026-11-05T22:30:38-06:00"
---
# Publish watchface
User authorized public0.1.0 release with palette GIF first.
1. `python3 execution/build_store_media.py` validates exact native frames and timings.
2. Run tests and fresh release-media review.
3. `python3 execution/publish.py` dry-run; add `--publish` for the authorized public upload.
4. `python3 execution/verify_public.py` checks public gallery order and exact downloaded assets.
Archive exact SDK-published PBW; clean rebuild timestamps can alter bundle bytes.
Never print auth tokens. Publication receipt prevents blind duplicate upload; inspect ambiguous results before retrying.
