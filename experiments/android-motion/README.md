# Android Motion Lab (experimental)

A real sensor bridge, not yet a verified Just Dance Now controller. Pair an original Nintendo Switch Joy-Con with **Windows**. This tool reads its accelerometer/gyroscope through SDL2 and writes values into a running Android Emulator's virtual sensors over the authenticated loopback console. Android does not need to pair with the Joy-Con.

**Implemented:** separate Joy-Con enumeration, explicit device selection, motion sensor enable/read, authenticated persistent emulator connection, signed axis rotations, delivered-rate display, stop on disconnect/stale sensor, best-effort neutral values on exit. This tool emits no keyboard/mouse mappings. Close the main JoyBridge mapper while testing.

**Not verified:** Windows Bluetooth capture, Android guest sensor delivery, app installation/login, Just Dance Now motion/scoring, grip orientation, latency, or multiplayer. No Android SDK/emulator, KVM, Bluetooth hardware or Joy-Con is present in the development workspace. Automated tests use a mock console, not a running Android instance. Do not interpret a successful build or an `OK` from the emulator as evidence of game compatibility.

## Windows setup

1. Install [Android Studio](https://developer.android.com/studio) and its Android Emulator through the normal installer. Enable the virtualization support requested by Android Studio. Android/SDK components are not included in our download.
2. In Device Manager, create a phone AVD with a **Google Play** system image compatible with your PC. Start it. Confirm the phone boots and Play Store works. A Play image is only a candidate, not a guarantee the game is available or works.
3. Use Play Store inside the AVD to look for Ubisoft's **Just Dance Now**, not the separate console Controller app. If unavailable/incompatible, record that result; don't use random APK mirrors or conceal emulator identity. Sign in yourself as needed. No credentials are handled by this bridge.
4. Pair one original Joy-Con in Windows Bluetooth settings (hold its physical SYNC button until its LEDs chase). Keep it in your right hand using its wrist strap for the dance test.
5. Download and extract the artifact from the repository's **Build Android motion lab** Actions workflow. Run `Start-Motion-Bridge.cmd`. It queries emulator sensors, lists Joy-Cons, asks for an index, then streams. The executable is unsigned. First-time Android setup and physical pairing are not one-click operations.
6. Before opening a game, inspect accelerometer and gyroscope events in an Android sensor viewer you trust, or your own SensorManager test app. A stationary controller should show about 9.81 m/s² total acceleration and near-zero angular velocity. Confirm axes with deliberate rotations in each direction. Console readback alone does not prove app-level delivery.
7. Only after the sensor test passes, open https://justdancenow.com/ in your PC browser. Use the official Android app to join that room. Test a song through the normal service. Record whether actual movement changes scoring compared with a stationary controller, and whether pairing, room join and reconnect succeed.

Press **Ctrl+C** to stop. A disconnected/stale controller stops the bridge instead of silently switching players. Reconnect and relaunch explicitly. If the console connection is lost, resetting virtual sensors may be impossible; restart the AVD before continuing. Force-killing the process also bypasses cleanup.

## Command-line controls

```powershell
.\JoyBridge-Motion-Lab.exe --check
.\JoyBridge-Motion-Lab.exe --list
.\JoyBridge-Motion-Lab.exe --device 0 --port 5554 --hz 60
.\JoyBridge-Motion-Lab.exe --device 0 --axes=x,z,-y
```

The index is from the current `--list` output, not a persistent player ID. Identity axes are deliberately **uncalibrated**, not an assertion that the grip matches a phone. `--axes` accepts only proper signed rotations; apply the same mapping to acceleration and angular velocity. Negative-leading mappings require `--axes=-x,-y,z`. Full arbitrary grip calibration and gyro-bias calibration are future work. Do not subtract gravity from accelerometer data.

Acceleration is in m/s² including gravity; angular velocity is in rad/s. SDL and Android use these units. This prototype only overrides acceleration and gyroscope, **not** gravity, linear-acceleration or rotation-vector sensors. Apps using fused sensors might therefore behave incorrectly. Verify which sensors the target app actually consumes before expanding the bridge.

Default console port: 5554. Other instances generally use another even port, e.g. 5556. Find the actual serial/port using Android SDK `adb devices`. `--token-file` overrides the usual `%USERPROFILE%\.emulator_console_auth_token`. Keep authentication enabled. The bridge only connects to 127.0.0.1 and does not expose a network server.

60 Hz is a requested maximum, not a guarantee. Two acknowledged console writes per sample add overhead and are not atomic; actual delivered rate is printed every two seconds. No historical samples are queued or replayed. This is a feasibility transport; a measured higher-performance gRPC transport may follow.

## Run from source

Python 3.11+ on Windows x64, no pip dependencies for the bridge itself:

```powershell
python scripts/fetch_sdl.py
python experiments/android-motion/bridge.py --dll vendor/SDL2-2.32.10/x86_64-w64-mingw32/bin/SDL2.dll --list
python experiments/android-motion/bridge.py --dll vendor/SDL2-2.32.10/x86_64-w64-mingw32/bin/SDL2.dll --device 0
python -m unittest discover -s experiments/android-motion -v
```

CI uses PyInstaller to make a standalone Windows executable with SDL2 bundled. Packaging does not install or bundle Android, Google Play, Ubisoft apps, songs or accounts. The standard JoyBridge installer remains separate.

## Acceptance gates and evidence to collect

| Gate | Pass condition | Current evidence |
| --- | --- | --- |
| Transport | Authenticate; reject KO; preserve command boundaries | Mock-console tests pass |
| Data validation | Reject NaN/Inf, invalid/reflected axes; detect either stale sensor | Unit tests pass |
| Windows executable | Package and execute help on Windows | See Actions run |
| Real motion | Both sensors update; units/axes checked; disconnect stops stream | Not tested |
| Android | SensorManager receives changing sensor events at measured rate | Not tested |
| Just Dance Now | Official app installs, joins room, completes song; motion affects scoring | Not tested |
| Reliability | Several songs, reconnect, sustained rate and thermal/resource observation | Not tested |
| Multiplayer | Separate Joy-Con -> separate AVD -> separate player session | Not tested |

One AVD has one phone sensor set. Two Joy-Cons cannot be independent dancers inside a single app instance merely by combining their data. A future two-player experiment needs two isolated instances/ports, controller assignments and successful separate room sessions. Resource requirements and game behavior must be measured. No claimed player limit or support guarantee yet.

If installation fails, stop at the compatibility gate. If only raw-sensor delivery works but scoring does not, investigate required sensor types, orientation, timing and app behavior before choosing a direct controller-client integration. Do not fabricate score packets.

## Primary references (checked 2026-10-21)

- [Android emulator console: authentication and sensor set/get](https://developer.android.com/studio/run/emulator-console)
- [Android motion sensors and units](https://developer.android.com/develop/sensors-and-location/sensors/sensors_motion)
- [Android virtual sensor controls](https://developer.android.com/studio/run/emulator-extended-controls)
- [SDL sensor units and coordinates](https://wiki.libsdl.org/SDL2/SDL_SensorType)
- [SDL timestamped controller sensors](https://wiki.libsdl.org/SDL2/SDL_GameControllerGetSensorDataWithTimestamp)
- [Just Dance Now official FAQ](https://justdancenow.com/FAQ)
- [JoyDance legacy controller integration](https://github.com/redphx/joydance): precedent for older Just Dance titles, not proof of Just Dance Now support.
