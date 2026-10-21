# JoyBridge product blueprint

Decision date: 21 October 2026. **This document is a proposal, not a list of shipped features.** Sources are indexed in [SOURCES.md](SOURCES.md). The implementation remains the v0.1 Windows prototype.

## The product worth building

Make a pair of inexpensive, familiar Joy-Cons into a reliable motion controller for games, a useful second hand for creative work, and a flexible accessibility input. The product promise should be: **connect, choose an activity, calibrate once, and understand exactly what each movement does.**

Do not lead with “more features than reWASD.” reWASD already documents gyro, tilt, flick stick, virtual-controller mappings, device grouping, profiles and app detection [S01–S04]. JoyShockMapper already demonstrates sophisticated gyro controls and motion helpers [S05–S06]. Our opportunity is a more approachable, well-tested Joy-Con experience, especially for two independent hands and creative applications. Comparative performance claims must wait for measurements on identical hardware and tasks.

## Five experiences that justify switching

### 1. Motion Studio

A live 3D controller and signal view shows both hands, gyro bias, actual sample timing, clipping, selected axes, output values, and calibration status. A guided wizard asks the user to rest the controllers, hold them naturally, rotate left/right and up/down, and test a target. It detects orientation mistakes and explains the correction. Separate stored calibrations per physical unit, not one calibration shared by all controllers.

Users select a goal: aim, point, steer, scrub, orbit, gesture or send raw motion. Simple controls come first; a detailed curve editor and sensor trace are optional. A profile carries its grip, output mode, gain units, application sensitivity assumptions, tested version and known issues. Save before/after calibration traces locally so a user can diagnose drift without guessing at sliders.

### 2. Hands and Players

A visual assignment board represents each physical Joy-Con. Press a button to identify it; a short requested vibration confirms the match. Drag left/right devices into a pair, use a single sideways controller, combine two devices for shared accessibility control, or assign a dedicated hand to an application integration. Device identity and player role survive reconnects where the OS exposes a stable identity. Ambiguous devices require re-identification rather than silently stealing a player's slot.

Start by validating two physical Joy-Cons. Then four (two pairs), then an **eight-physical-device engineering target**, subject to Bluetooth adapter quality and scheduling. Eight physical inputs do not mean eight Xbox player slots: classic XInput exposes four [S10]. Capacity should be a tested matrix, never a universal claim.

### 3. Creator Deck

A left Joy-Con beside a normal mouse becomes a small shortcut/parameter controller. The stick handles coarse navigation, tilt controls a selected parameter, and held modifiers expose clear layers. A quick press can undo; holding a button changes the active tool layer. Haptic ticks can mark discrete steps, mode changes or app acknowledgements.

Prioritize three polished workflows: video editing, Blender navigation, and OBS scene/audio control. Add MIDI/OSC for musicians and creative coders afterward. Named commands via application APIs are preferable to focus-sensitive keystrokes when supported. A gesture must never silently start a broadcast or close an unsaved document; consequential actions get an explicit arm/confirm mapping.

### 4. Compatibility profiles people can trust

The catalogue should distinguish **maintainer tested**, **community reported**, **experimental**, and **blocked/unsupported**. Every tested entry includes app/game version, Windows version, Joy-Con generation, Bluetooth adapter, output backend, concurrent remappers, date and test procedure. Offer a profile diff, a preview of emitted actions, and a rollback. Data-only presets may be imported directly after review; executable plugins require a separate explicit install path.

The catalogue's usefulness is a defensible advantage. A count of untested configs is not. Local profiles and all basic mapping should work without an account or network connection.

### 5. An open motion interface

Expose selected controller events through a versioned local API, with optional MIDI, OSC and DSU outputs. Plugins can build camera controls, music instruments, educational demos or accessible interaction without rewriting Bluetooth code. Maintain timestamps, units and physical-device identity across the boundary. Bind local endpoints to loopback by default; remote sharing is a separate opt-in mode. Never ship an unauthenticated arbitrary-command endpoint.

## Hardware inventory and limits

Nintendo lists sticks, buttons, accelerometers and gyroscopes in both original Joy-Cons, HD Rumble, and IR/NFC on the right controller [S07]. These are capabilities of the hardware, not proof that the prototype or a generic PC driver exposes them.

| Element | Useful product features | Limit or dependency |
| --- | --- | --- |
| Sticks and digital buttons | Remaps, holds, double-taps, chords, layers, radial menus, one-handed profiles | SL/SR/Capture need explicit adapter mapping and physical tests |
| Gyro | Relative mouse aim, air mouse, roll-to-dial, orientation telemetry | Bias, timestamps, grip orientation and clutching matter |
| Accelerometer | Gravity-aware orientation, gated shake/tap, motion activity estimates | Includes gravity; movement can corrupt naive tilt estimates |
| Two independent IMUs | Separate aim/navigation roles; independent instruments | Cannot accurately measure hand separation or absolute positions |
| HD Rumble | Mode confirmation, step ticks, notifications, app feedback | Ordinary rumble APIs may expose less than the hardware; rich waveforms require backend work |
| Player LEDs, colors, battery | Identification, slot assignment, low-battery status | Available fields and update granularity depend on backend/OS |
| Right IR camera | Short-range proximity/gesture experiments; marker research | Specialist HID path, lighting/geometry and bandwidth constraints; not a normal webcam |
| Right NFC | Optional research into supported tag-driven profile changes | Protocol support and tag types must be proven; not a general phone-style NFC reader |
| Rail accessories | Future Ring-Con/accessory experiments | Separate protocol/hardware work, not automatic controller support |

Original Joy-Cons do not provide analog trigger pressure. A tilt-driven synthetic throttle is possible; it does not turn ZL/ZR into pressure sensors. IMU-only tracking cannot provide stable room-scale position, reliable drawing coordinates in mid-air, or full-body VR tracking. Yaw can drift without an external reference. Software cannot repair a worn physical stick, guarantee anti-cheat compatibility, or create haptic game events without a source of those events.

## Competitive position

| Capability | Established reference | Proposed JoyBridge advantage | Evidence status |
| --- | --- | --- | --- |
| Gyro/tilt/flick stick | Already documented by reWASD/JSM | Easier setup, per-hand diagnostics, reproducible tuning | Opportunity, not proven advantage |
| Mapping/layers/profiles | Mature remapper category | Activity-oriented recipes and understandable output preview | Product hypothesis |
| Multiple inputs | reWASD documents groups of four [S03] | Physical-device identity, deliberate hand/player assignments, reconnect resilience | Requires new architecture and hardware tests |
| Multiple virtual gyro sources | reWASD documents first-controller rule in a grouped virtual-gyro configuration [S01] | Independently routed sensors for consumers that accept them | Consumer protocol/slot support required |
| Creative applications | Keyboard shortcuts are broadly possible | First-class app adapters, acknowledgement-aware haptics, parameter mapping | Proposed integrations |
| Cross-platform | SDL is portable; output stacks differ | Shared tested engine and honest platform-specific support | Roadmap only |
| Performance | No comparative benchmark gathered | Publish p50/p95 latency and drop/stall diagnostics | Must measure before claiming faster |

## User journeys

**First use:** identify hardware generation → show Bluetooth availability → explain physical SYNC → discover/select intended controller → connect → test buttons → calibrate gyro → choose activity → show controls → enable. Offer actionable failure messages at each stage instead of one generic pairing error.

**Daily use:** wake devices → reconnect to saved roles → preview selected app profile → explicitly resume output. New executable matches should not silently activate powerful actions. A single global pause must work even if a plugin fails.

**Two-player session:** identify each hand → assign two pairs → choose supported multiplayer output → open game's controller setup → verify Player 1 and Player 2 separately → test disconnect/rejoin. Do not equate both pairs typing WASD with multiplayer support.

**Creator workflow:** choose Blender/OBS/video-editor recipe → verify plugin/app version → map to named actions or visible keyboard fallback → test in a safe preview → save. Display whether an action requires app focus or works through its API in the background.

## Prioritization and sustainability

Keep basic pairing, remapping, motion calibration, local profiles, diagnostics and accessibility features available without a mandatory account. Consider donations/sponsorship or paid convenience such as profile sync and specialist creative packs only after retention is demonstrated. Do not introduce subscriptions just to recover ordinary controller functionality.

Build one exceptional gaming demo and one exceptional creator demo before expanding the catalogue. Recruit testers with different Bluetooth adapters and accessibility preferences. Ask whether the same people still use the app two weeks later, not merely whether they liked the demo.

Track connection success, time to first usable profile, reconnect recovery, false gesture activations, reproducible drift, releases with stuck-key regressions, and profile task completion. Targets are product goals, not measured results. Suggested initial gates: 20 reconnect cycles without role swaps, 30-minute sessions without stuck outputs, and repeatable calibration/test traces. Detailed gates are in [ROADMAP.md](ROADMAP.md).

Do not ship IR, NFC, cloud sync, a marketplace, AI gesture training and a custom Windows driver in the same first milestone. Their risk and maintenance cost would obscure the core experience.
