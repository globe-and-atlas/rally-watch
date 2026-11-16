---
generated_by: "OpenAI Codex (GPT-6; exact variant not exposed)"
timestamp: "2026-11-05T22:08:43-06:00"
---
# Build watchface
Generate masks with `python3 execution/generate_digits.py`.
Run `make test`, `make build`, `make verify`.
Fixture from watchface: `pebble clean`, `RALLY_FIXTURE=1 pebble build`.
Root installs fixture and invokes `python3 execution/capture_native.py --monitor PORT`.
Production stripsRALLY_*flags and cleans previous objects; never publish fixtures.
