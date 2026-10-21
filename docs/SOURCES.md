# Research sources

Checked 21 October 2026. Primary/vendor/project documentation was used where possible. This is a bounded technical comparison, not an exhaustive audit of every competitor feature or every game. Product opportunities and estimates are our proposals, not claims made by these sources.

| ID | Source | What it establishes |
| --- | --- | --- |
| S01 | [reWASD gyroscope](https://help.rewasd.com/how-to-remap/gyroscope.html) | Existing gyro/tilt and virtual-gyro behaviour, calibration, grouped-source caveat |
| S02 | [reWASD advanced sticks](https://www.help.rewasd.com/basic-functions/advanced-stick-settings.html) | Existing flick-stick implementation and per-game tuning |
| S03 | [reWASD advanced mapping](https://www.rewasd.com/advanced-controller-mapping) | Virtual controllers and documented four-device grouping |
| S04 | [reWASD workspace](https://help.rewasd.com/interface/workspace.html) | Profiles/configuration and active-process workflow |
| S05 | [JoyShockMapper](https://github.com/JibbSmart/JoyShockMapper/blob/master/README.md) | Existing gyro-oriented mapping reference; calibration and flick-stick ecosystem |
| S06 | [GamepadMotionHelpers](https://github.com/JibbSmart/GamepadMotionHelpers) | Candidate sensor fusion/calibration helper independent of device input |
| S07 | [Nintendo Joy-Con specifications](https://www.nintendo.com/sg/hardware/switch/modal/specs/joy-con.html?width=960) | Buttons, sensors, right-side IR/NFC, HD Rumble and charging |
| S08 | [SDL sensor types](https://wiki.libsdl.org/SDL3/SDL_SensorType) and [sensor reads](https://wiki.libsdl.org/SDL3/SDL_GetGamepadSensorData) | Sensor units/axes and per-hand sensor types/API |
| S09 | [Microsoft SendInput](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-sendinput) | Desktop injection semantics and integrity-level constraints |
| S10 | [Microsoft XInput](https://learn.microsoft.com/en-us/windows/win32/xinput/getting-started-with-xinput) | Four-controller XInput limit and controller interface |
| S11 | [ViGEm end of life](https://docs.nefarius.at/projects/ViGEm/End-of-Life/) and [archived repository](https://github.com/nefarius/ViGEmBus) | Maintenance/retirement risk for a common virtual-gamepad dependency |
| S12 | [OBS WebSocket project](https://github.com/obsproject/obs-websocket) and [protocol](https://github.com/obsproject/obs-websocket/blob/master/docs/generated/protocol.md) | Supported route for named OBS commands and events; negotiate version/capabilities |
| S13 | [Cemuhook/DSU protocol reference](https://github.com/v1993/cemuhook-protocol) | Motion-consumer protocol candidate; implementation requires exact format/units tests |
| S14 | [Linux uinput documentation](https://docs.kernel.org/input/uinput.html) | Userspace virtual input facility |
| S15 | [libei documentation](https://libinput.pages.freedesktop.org/libei/) | Wayland-oriented input-emulation path and portal integration |
| S16 | [Nintendo Switch reverse-engineering research](https://github.com/dekuNukem/Nintendo_Switch_Reverse_Engineering) | Specialist HID/calibration/IR/NFC research; not a support guarantee |
| S17 | [Microsoft Bluetooth discovery](https://learn.microsoft.com/en-us/windows/win32/api/bluetoothapis/nf-bluetoothapis-bluetoothfindfirstdevice) and [service state](https://learn.microsoft.com/en-us/windows/win32/api/bluetoothapis/nf-bluetoothapis-bluetoothsetservicestate) | APIs used by the current prototype's best-effort pairing attempt |
| S18 | [SDL2 Joy-Con combination](https://wiki.libsdl.org/SDL2/SDL_HINT_JOYSTICK_HIDAPI_COMBINE_JOY_CONS) | SDL-controlled combination used by prototype; distinct from deliberate rig routing |
| S19 | [SDL releases](https://libsdl.org/release/) | Official source of the pinned SDL2 development archive |
| S20 | [Blender Operator API](https://docs.staging.blender.org/api/current/bpy.types.Operator.html) | Candidate modal/operator integration concepts; current production-version validation still required |

No game/application named in USE_CASES is certified by this research. None of the sources establishes that JoyBridge is faster, more accurate, easier, or more capable than competing software. Those are outcomes to test.
