# Roadmap and release gates

**Planning estimates, not delivery promises.** Assumes one experienced systems/desktop engineer working full time, access to multiple original Joy-Cons, two or more Bluetooth adapters, Windows test machines and regular testers. For a beginner or part-time team these estimates are substantially longer. Driver development and platform approvals can dominate the schedule.

| Milestone | Scope | Rough effort | Exit gate |
| --- | --- | --- | --- |
| M0: reproducible prototype | Repository, clear status, pinned dependencies, repeatable installer, hardware checklist | 1–2 engineer-weeks including hardware validation | Install/uninstall, buttons, key release and connection tests on Windows |
| M1: motion foundation | Core separation, sensor recorder, timestamps, calibration, grip transform, gyro mouse, clutch | 3–5 engineer-weeks | Replay tests plus both-hand hardware verification and a usable aim demo |
| M2: profiles and rigs | Stable identity, deliberate pair/single roles, layers, app switching, pointer ownership | 3–5 engineer-weeks | Two pairs reconnect without cross-control; profile-switch release tests |
| M3: multiplayer outputs | Backend evaluation, independent virtual slots, rumble return, conflict detection | 4–8+ engineer-weeks | Named games verified with two players; driver distribution/maintenance decision resolved |
| M4: creator integrations | OBS adapter, Blender add-on, editor recipe, MIDI/OSC foundation | 4–6 engineer-weeks | Three reproducible creative workflows with acknowledgements and recovery |
| M5: public beta quality | Accessible onboarding, compatibility catalogue, signing/update/rollback design, broad tests | 3–5 engineer-weeks | Hardware matrix, regression suite, support process and reproducible release |
| M6: other platforms | Linux then macOS adapters, packaging and permission flows | 4–8+ engineer-weeks per platform | Platform-specific tests; supported outputs stated explicitly |
| Research track | IR, NFC, advanced haptic patterns, accessory experiments | Unbounded spikes with stop criteria | Demonstrated value and isolated backend before any support claim |

M1–M5 may overlap with a larger team, but this is a several-month product, not a weekend feature patch. Four-to-eight-week development spikes can produce useful prototypes; they do not imply release-quality parity with mature remappers. Reserve ongoing maintenance capacity for Windows, SDL, game and app changes.

## First implementation sprint

1. Run the existing installer on Windows and record failures before adding UI features.
2. Fix lifecycle/output correctness: check SendInput results, settings writes, hotkey conflicts, scan errors and focus changes. Add regression tests around shared bindings and disconnects.
3. Separate device, mapping and output state from the Win32 window procedure.
4. Add sensor capability discovery and a local recorder with timestamps and units.
5. Add calibration replay tests, then guarded right-hand gyro-mouse output with a held clutch.
6. Demonstrate it in one known compatible game or controlled test scene; keep output paused by default.

## Quantitative quality gates

These are proposed acceptance criteria, **not current measurements**:

- At least 20 reconnect cycles per tested setup with no unintended role swap.
- At least 30-minute active sessions with no stuck keys or unbounded motion after pause/disconnect.
- Correct neutralization after profile change, suspend and lost device; test process crash separately.
- Publish measured p50/p95 sensor receipt, engine processing and output queue timings for the benchmark hardware. Set performance budgets from observed baselines.
- Replays at multiple sample rates produce equivalent integrated motion within a stated numerical tolerance.
- Gesture evaluation includes at least ordinary gameplay/editor motions as negative samples and reports false positives.
- Fresh Windows user install, upgrade and uninstall retain/remove only documented files; no silently installed drivers.
- Every “tested” profile has a named app version and reproduction procedure.

## Release policy

Keep v0.1 experimental. Do not put planned features in release download descriptions. CI artifacts are unsigned build outputs, not stable releases. A public beta needs Windows execution tests and controller hardware evidence. Add code signing through a legitimate signing process when ready; do not tell users to turn off SmartScreen or endpoint security.

## Decisions to delay

Do not yet choose a custom kernel driver, subscription pricing, cloud profile marketplace, gesture ML stack or permanent UI toolkit. First validate connection reliability, motion quality and two everyday workflows. Re-evaluate the JoyBridge name before public marketing; this working name is not a trademark-availability conclusion.
