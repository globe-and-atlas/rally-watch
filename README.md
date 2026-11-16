---
generated_by: "OpenAI Codex (GPT-6; exact variant not exposed)"
timestamp: "2026-11-05T22:11:41-06:00"
---
# Rally
A bold scoreboard watchface for PebbleTime2 / Emery200×228.

- Large tall hour and minute pairs in separate rounded panels.
- Six presets: Navy & orange, Red, Field green, Plum, Ice, Monochrome.
- Custom face/left-digit color, left-panel/right-digit color, right-panel color.
- Watch-default/12/24time, with AMPM above panels in12-hour mode.
- DateOff/word/ISO/US/EU.
- Real battery icon and percentage centered beneath the date.
- Minute-only updates.

## Build
`make test`, `make build`, `make verify`.
Production output: dist/Rally-0.1.0.pbw.

## Native QA
Root coordinates the single shared emulator. Fixture build from watchface uses `RALLY_FIXTURE=1` after `pebble clean`. Then root can run `python3 execution/capture_native.py --monitor PORT`.
Fixture defaults10:08 ThuNov05,82%; message overrides11000hour,11001minute,11004battery.

The source font is Bebas Neue under the bundled OFL license. Production build cleans fixtures before copying PBW. Live: [Rally](https://apps.repebble.com/dfe5a3d1e2e44b5ebec727a7).

## Public release
https://apps.repebble.com/dfe5a3d1e2e44b5ebec727a7

Version0.1.0. First preview: six-palette native GIF,15.5s loop with2.5–3s holds. Four still previews follow. PublicGIF andPBW bytes verified against local release files.


## Round-compatible release — 0.1.1

Rally includes native layouts for Pebble Time2 (Emery200×228), original Time Round (Chalk180×180), and Round2 (Gabbro260×260). The rectangular layout and existing settings identities are preserved.

Build: `python3 execution/build.py`, then `python3 execution/verify.py`. Local bundle: `dist/Rally-0.1.1.pbw`. Native round previews: `media/round/`. Repeatable fixture/capture instructions: [round compatibility QA](knowledge/procedural/round_compatibility.md).

This update is [publicly available](https://apps.repebble.com/dfe5a3d1e2e44b5ebec727a7) with round screenshots. Public PBW bytes and screenshot pixels verify; physical-watch validation remains separate.
