# Compatibility and validation

## Current truth

| Component | Status |
| --- | --- |
| C application | Cross-compiles with MinGW for Windows x64 |
| NSIS setup | Cross-built executable installer |
| SDL2 runtime | Bundled by build script; version/hash pinned |
| Keyboard/mouse mapping | Implemented, not hardware-validated here |
| Automatic Bluetooth pairing | Best-effort implementation; not verified on a Windows adapter |
| Motion/gyro | Not implemented |
| Independent multiplayer | Not implemented; all prototype devices share output |
| Virtual Xbox/DS4 | Not implemented |
| App-specific profiles/plugins | Not implemented |
| Linux/macOS runtime | Not implemented |
| Original Joy-Cons | Intended target, pending physical tests |
| Joy-Con 2 and third-party controllers | Unsupported/unverified |
| Comparative latency or accuracy | Not measured |

## Hardware matrix to collect

Record OS build, CPU/architecture, SDL version, app commit, Bluetooth adapter/chipset/driver, Joy-Con generation/side/count, battery indication, output backend, app/game/version, other active input tools and distance/interference conditions. Never publish serials or Bluetooth addresses by default.

Test original L and R individually and paired; two pairs; later four single units and eight-device target. Verify face-label conventions, SL/SR/Capture capabilities, sticks, press/release, sleep/reconnect, neutralization, battery reporting, sensor orientation and rumble ownership.

## Existing prototype test procedure

1. Install as standard Windows user. Launch from shortcut and attempt a second instance.
2. Test Bluetooth unavailable/off, no devices discoverable, one discoverable controller and a selected pair. Check fallback settings path.
3. Verify every supported button against physical label. A paired controller may be counted once.
4. Test WASD in Notepad, pointer movement, clicks and long-held actions.
5. Map two physical actions to E; release one and ensure E stays down until both release.
6. Disconnect during held input; pause using F8/F9; foreground the mapper; suspend/resume; close it. Confirm release and pause state.
7. Save, relaunch and inspect changed bindings/settings. Test invalid numeric ranges.
8. Test a normal keyboard/mouse-compatible game without another remapper running.
9. Uninstall. Check installed files/shortcuts and retained user-profile behaviour.

The current cleanup handles ordinary transitions, but there is no separate watchdog guaranteeing cleanup after a crash or forced termination. SendInput failures and profile-save return codes are current engineering gaps. Hardware reports should include these cases rather than treating them as passed.

## Future profile evidence

Use four statuses: maintainer-tested, community-reported, experimental, unsupported. A maintainer-tested report must include versioned recipe, hardware manifest, date, test actions, failures and any game settings. Community success is useful evidence, not a guarantee for every adapter or future update.

Some games block remappers or synthetic inputs. A profile must state its observed compatibility without promising anti-cheat bypass or universal acceptance. Multiple installed remappers and Steam Input can contend for the same physical device; detect and explain conflicts rather than automatically modifying other tools.
