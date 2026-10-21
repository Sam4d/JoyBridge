# Multiple Joy-Cons, players and applications

**Proposed architecture. v0.1 merges every opened controller into one keyboard/mouse stream.** It must not be advertised as independent multiplayer support.

## Supported configurations to build

| Configuration | Example | Output requirement |
| --- | --- | --- |
| One L or R | One-handed navigation, presenter, sideways platformer | Remap orientation/buttons and provide missing functions via layers |
| One L+R pair | Conventional gamepad with right-hand gyro | Logical paired controller plus chosen output backend |
| Two independent hands | Left editing shortcuts, right pointer | One shared pointer owner; distinct buttons/parameters |
| Two pairs | Two-player local co-op | Two independent virtual gamepad slots or game-native device support |
| Four single Joy-Cons | Party game with simple controls | Four supported player inputs; game must support required bindings |
| Mixed devices | Mouse for aim, left Joy-Con for movement | Clear input ownership and no competing mapper |
| Shared control | Two people operate one character | Explicit merge policy, accessibility configuration |
| Creator + game | One pair plays, another hand controls OBS | Game output plus separate OBS API connection |
| Two different games at once | Separate windows/emulators | Application-specific device selection/background input support; not universally achievable |
| Eight physical Joy-Cons | Four pairs in a tested setup | Radio/bandwidth testing and output-backend capacity; engineering target only |

Classic XInput has four user indices [S10]. A physical Joy-Con, a logical pair, and a virtual player slot are different objects. Other APIs may support different counts; actual games can impose lower limits. Bluetooth capacity must be measured on named adapters. Do not promise that adding a second Bluetooth adapter automatically balances or isolates devices.

## Assignment model

Maintain three explicit layers:

1. **Physical device:** side, supported generation, backend identity, serial/address when available, connection epoch, capabilities, calibration, battery, name/color if exposed.
2. **Logical rig:** a set of assigned devices with explicit roles such as left-actions, right-aim, auxiliary-dial. Pairing is a user choice, not arrival order.
3. **Output route:** desktop input, virtual-player slot, local motion stream or named app connection. Each rig/profile chooses its destinations and ownership policy.

Assign devices with an identify action: display currently pressed buttons and optionally vibrate the selected unit. Local identifiers stay local. Redact serials/addresses in exported diagnostic bundles. Stable identity is not guaranteed by every backend; unresolved identity requires user re-assignment.

Device lifecycle: discovered → selected → connecting → connected → calibrated/ready → active → disconnected. On disconnect, neutralize only that device's contributions, cancel its pending gestures and release output tokens. Preserve the rig so reconnection can restore it safely. Never route a new device into another player's vacant slot just because it appeared first.

## Output arbitration

For keyboard buttons, maintain contribution sets keyed by source/binding. A key remains down until the last contributor releases. On profile change or app-focus transition, release old contributions before starting the new profile. Keep joystick axes, mouse pointer ownership and app parameters separate.

The system desktop usually has one pointer and foreground keyboard focus. Two mouse-output rigs cannot independently click different ordinary windows. Offer explicit pointer-owner switching. Applications with a dedicated API or raw-device-aware input can receive independent data through their own contracts; that is a distinct integration, not a universal background-keyboard trick.

For virtual gamepads, map each rig to an output slot and return rumble to that rig. Some games listen to all controllers, ignore slot-selection expectations or stop when unfocused. A virtual controller is not inherently bound to one process. Test each claimed simultaneous-game setup and record the game settings required.

For app adapters, connection identity is explicit, such as a selected OBS instance or MIDI port. Background operation may be possible because the app receives commands through its API. Do not silently send keyboard fallbacks to whichever application happens to be foreground.

## Presets and app switching

Allow one rig to use different profiles as the foreground app changes, plus an explicit profile lock. Match executable path/identity using a user-approved rule, not a broad substring. Show a preview when a new match is first created. Avoid ambiguous matches between a game launcher, game executable and emulator.

Separate device setup from activity profiles: a user should not reassign hands for every game. Profiles reference roles; rigs bind roles to physical devices. Exportable profiles should not contain local Bluetooth addresses or absolute user-specific paths.

## Pairing improvements

The prototype scans known names and enables HID services; it does not provide verified universal pairing. The product flow must show radios, discoverable devices, exact target selection, attempt state and Windows error information. Pair one or a selected group without forgetting unrelated devices. Removing an old pairing is an explicit recovery step, not an automatic first action. Physical SYNC remains necessary for initial discovery.

## Acceptance scenarios

- Two pairs connect in reversed order without swapping players.
- Disconnect one hand while holding a shared key: the other contributor remains active.
- Disconnect a rig while its stick is deflected: its virtual axes return to neutral.
- Reconnect preserves assignment or asks for identification when ambiguous.
- App switch releases modifiers and cancels half-completed gestures/macros.
- Both rigs never compete for the desktop pointer without an explicit policy.
- Capacity tests record per-device packet gaps and p95 engine delay with 2, 4, then 8 physical devices.
- Failure of an OBS/MIDI plugin never stalls acquisition or another player's input.
