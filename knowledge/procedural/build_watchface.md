---
generated_by: "OpenAI Codex (GPT-6; exact variant not exposed)"
timestamp: "2026-11-05T22:11:41-06:00"
---
# Build and native QA
`python3 execution/generate_digits.py` regenerates the numeral header.
`make test` checks host geometry and actual Clay Save/Cancel/reload.
`make build` clean-builds production after removingRALLY_*environment keys.
`make verify` confirms app identity/platform and current binary.
Root-only native install: fixture after clean, then `python3 execution/capture_native.py --monitor PORT`.
Capture asserts exact numeral pixels, palette colors, per-panel ink centering, date/AMPM presence and battery bars over22cases.
Rebuild production after fixture captures; never archive fixture PBWs.
