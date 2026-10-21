# JoyBridge

**Make your Joy-Cons useful across games, creative apps, and everyday work.**

JoyBridge is an independent Joy-Con project starting with a small Windows keyboard/mouse mapper. The next product direction is a motion-first, multi-controller platform with useful presets, visible diagnostics, and portable components.

> **Current status: experimental v0.1 prototype.** Motion, independent player slots, virtual Xbox output, and creative-app plugins are **planned, not implemented**. Windows hardware validation has not been completed. Nothing here establishes superiority over reWASD or JoyShockMapper.

## What runs today

- Original Switch Joy-Con detection using SDL2, with SDL's automatic pair combination.
- Editable keyboard/mouse bindings, Gaming and Desktop presets, saved per-user profile.
- Left-stick movement, right-stick mouse, trigger clicks, and pause/release hotkeys.
- Best-effort Bluetooth HID pairing attempt with a Windows Settings fallback.
- Windows x64 application and per-user NSIS installer, compiled from source.

The four-entry device array is **not four-player support**. All detected controllers currently contribute to the same desktop keyboard/mouse output. SYNC mode still requires the physical controller button. Joy-Con 2, third-party clones, motion, and SL/SR/Capture mappings are not supported/verified by this prototype.

## Product plan

Start with [the product blueprint](docs/PRODUCT_BLUEPRINT.md). It explains the opportunities, hardware limits, priorities, and why simply copying gyro/flick-stick features will not differentiate this project.

| Document | Purpose |
| --- | --- |
| [Product blueprint](docs/PRODUCT_BLUEPRINT.md) | Positioning, standout experiences, user journeys and business choices |
| [Motion design](docs/MOTION_DESIGN.md) | Gyro, tilt, gestures, calibration, sensor timing and physical limits |
| [Multiple controllers](docs/MULTI_CONTROLLER.md) | Pairing, player slots, one-handed setups and concurrent-app limits |
| [App and game recipes](docs/USE_CASES.md) | Concrete control schemes, output paths and acceptance checks |
| [Architecture](docs/ARCHITECTURE.md) | Portable engine, adapters, profiles, diagnostics and migration |
| [Roadmap](docs/ROADMAP.md) | Ordered milestones, engineering estimates and release gates |
| [Backlog](docs/BACKLOG.csv) | Prioritized implementation tasks with acceptance criteria |
| [Compatibility and testing](docs/COMPATIBILITY.md) | Truthful support labels and Windows hardware test matrix |
| [Research sources](docs/SOURCES.md) | Primary sources checked on 21 October 2026 |

Everything described as a proposal or milestone remains unimplemented until its acceptance checks pass.

## Build the Windows prototype

On Ubuntu 24.04 or another compatible Linux build host:

```sh
sudo apt-get update
sudo apt-get install gcc-mingw-w64-x86-64 nsis python3
python3 scripts/fetch_sdl.py
bash build.sh
python3 scripts/verify_build.py
```

Outputs: `JoyBridge-Setup.exe` and `dist/JoyBridge.exe`. The SDL download is version-pinned and SHA-256 checked. This build path cross-compiles for Windows x64; it does not make the application runnable on Linux. A native Windows development workflow is a future task.

The CI workflow repeats the cross-build and uploads an **unsigned experimental installer artifact**. An Actions build is not a Windows hardware test and does not automatically publish a stable release. No signed release is available yet.

## Try it on Windows

Install, turn on Bluetooth, hold the SYNC button on each Joy-Con until its LEDs chase, and click **Pair Joy-Cons**. If needed, use **Bluetooth settings → Add device → Bluetooth**. Choose a preset, save it, enable mapping and focus your game. F8 toggles mapping; F9 releases inputs and pauses. Read [Quick Start](resources/Quick-Start.txt) for details and limitations.

A combined pair can appear as one SDL device. Profiles are stored under `%LOCALAPPDATA%\JoyBridge\profile.ini`. The application must stay open. Mapping pauses while its own window is foreground.

## Contribute

See [CONTRIBUTING.md](CONTRIBUTING.md). The most valuable early contributions are reproducible Windows hardware reports, device lifecycle fixes, and an independently testable motion engine. Include your exact Joy-Con generation, Windows build, Bluetooth adapter, other remappers, and reproduction steps. Do not include personal device addresses or credentials in public reports.

Original source is MIT licensed; bundled SDL2 uses its own license. See [THIRD_PARTY.md](THIRD_PARTY.md). JoyBridge is not affiliated with Nintendo, reWASD, Valve, or the other applications named in the roadmap.
