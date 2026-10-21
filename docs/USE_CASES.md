# Game and app recipe catalogue

**Design recipes only. These are not installed profiles or verified compatibility claims.** Exact games/app versions, shortcuts and output backends must be validated before a recipe is labelled supported. Start with 3–5 excellent recipes, not a hundred untested ones.

## Gaming

| Recipe | Suggested controls | Integration and reality check |
| --- | --- | --- |
| Precision shooter | Left stick movement, right gyro aim, held clutch/recenter, ZR fire, ZL aim layer | Keyboard/mouse route first; validate game settings, synthetic-input acceptance and scoped gain |
| Flick-stick shooter | Right stick selects quick heading, gyro handles pitch/fine aim | Per-game turn calibration; not suitable for every game/user |
| Analog movement + gyro | Left stick analog movement, right gyro mouse | Mixed gamepad+mouse only when game supports it; may change UI prompts or reject mixed input |
| Gamepad-only camera | Gyro converted into virtual right stick | Requires virtual backend; game stick curves constrain feel |
| Racing wheel | Held grip enables roll steering; stick controls throttle/brake | Virtual analog axes required for smooth control; ZL/ZR are digital, not pedals |
| Flight/space | Tilt pitch/roll, stick thrust/yaw, button to capture neutral | Limit range and support recenter; no real force feedback |
| Platformer | Sideways single Joy-Con, stick move, two main actions, shift layer | Small button count; inspect the game's minimum controls |
| Local co-op | Two independently assigned pairs | Two gamepad slots or native device selection; never shared WASD |
| Strategy/management | Gyro or stick pointer, layer for groups/zoom/pause | Foreground keyboard/mouse; precise selection may be better with a normal mouse |
| Emulator motion | Raw gyro/accel via supported SDL or DSU route | Emulator must explicitly support protocol and source selection [S13] |
| Rhythm/drumming | Gated downstroke gesture triggers a hit, haptic beat cue | Prototype instrument; timing/jitter must be measured; not a physical drum sensor |
| Accessible single-hand | Reassign all essential actions to one hand with layers and toggles | Co-design with users; test reach/fatigue and provide an easy escape action |

## Productivity and creative work

| Recipe | Concrete design | Output path | Priority |
| --- | --- | --- | --- |
| Video-editing left hand | Stick scrubs coarse/fine, roll adjusts selected parameter, buttons mark in/out, undo, cut | Verified app shortcuts first; documented adapter where available | First creator demo |
| Blender orbit hand | Hold grip to orbit using gyro, stick pan/zoom, buttons change view/tool | Blender add-on consumes motion and calls appropriate context-aware operators | First creator demo |
| Blender two hands | One hand navigates viewport; other controls selected transform/tool | Two distinct input roles; orientation + sticks, not spatial hand tracking | After single-hand add-on |
| OBS control | Buttons select scenes/mute, held roll adjusts selected source gain, haptic acknowledges completion | Authenticated obs-websocket API [S12]; explicit arm for start/stop broadcast | Early integration |
| Slides | Next/previous, black-screen, timer cue, relative air-pointer mode | Foreground shortcuts; optional app integration for timer/state | Early |
| Browser and reading | Tilt while held for smooth scroll, buttons tabs/back/forward, stick zoom layer | Keyboard/mouse; accidental gestures disabled by default | Early |
| CAD / 3D viewer | Gyro orbit, stick pan, held modifier zoom, saved standard views | Per-app adapter/shortcut mapping; not claimed as a SpaceMouse driver | Later |
| Painting/photo editing | Left hand tool/brush-size/zoom/undo while right uses mouse or stylus | Shortcut profiles or documented app commands | Early profile |
| Timeline color grading | Roll acts as jog dial; modifier switches exposure/contrast parameter | App adapter or configured shortcuts; haptic detents are app-generated feedback | Later |
| Music instrument | Tilt sends MIDI CC; gated hits send notes; buttons choose banks/octave | MIDI output; receiving DAW must map controls; velocity is estimated | Later |
| Live visuals | Gyro controls camera/shader, buttons switch scenes, acceleration drives effects | OSC to a compatible tool such as a configured creative-coding patch | Later |
| Audio editing | Roll scrub, buttons markers and punch-in, stick track/parameter navigation | MIDI/shortcuts; confirm destructive edits and recording transitions | Later |
| IDE companion | Buttons navigate errors/bookmarks, stick scroll, layer for debug controls | Shortcut profile or editor extension; no arbitrary shell execution by default | Later |
| Meetings | Push-to-talk, hand raise, slide control, local timer vibration | Verified app shortcuts/API; never assume a mute state without acknowledgement | Later |
| Accessibility navigation | One-hand pointer, dwell/hold options, tremor-aware filtering, clear pause | Desktop output; user-specific settings and usability testing | Core design principle |
| Teaching sensors | Display gravity/rotation traces, compare motion with plots, export chosen samples | Local API and visualizer | Developer demo |
| Exercise/party experiments | Deliberate movement triggers game actions | Relative activity/gesture estimates only; no medical measurements or calorie accuracy claims | Experimental |
| Couch media remote | Playback/volume, scroll, app switch, long-press safety layer | Media keys and foreground navigation | Early profile |

Example apps are integration candidates, not endorsements or promises of current support. Before implementing a named adapter, verify that app's current API, licensing and platform support.

## Unusual but worthwhile experiments

**Air dial with haptic notches:** hold a button, twist the wrist to adjust one visible parameter, release to clutch. Notches acknowledge actual value changes so they remain synchronized if the app rejects a command.

**Two-person shared rig:** one person handles movement and the other camera/actions. Useful for collaborative play and some accessibility setups. Merge only the intended inputs, and make ownership visible.

**Motion scrub plus precision modifier:** large roll moves through a long timeline; holding a shoulder button reduces gain for frame-level selection. A stick or button can supply the final precise step.

**Gesture teaching lab:** record examples locally, show the trace and explain why a gesture triggered. Turn this into a debugging tool before a broad custom-gesture feature.

**Short-range IR experiments:** explore a right-Joy-Con proximity/marker detector with a separate raw-HID research adapter. Do not advertise a webcam, accurate room tracking, or standard support until proven. Infrared and full-rate IMU workloads may interact through the protocol; measure rather than assume.

**Tag-to-activity research:** test whether supported NFC tags can select a local activity profile. Keep this optional and read-only; protocol capability, permissions and limitations require research. Do not promise arbitrary tag compatibility.

## Golden demos and release checks

1. **Gyro aim demo:** connect one pair; explain clutch; calibrate; play a keyboard/mouse-compatible test scene; disconnect and verify neutral output. Log the exact game/version and gain assumptions.
2. **Editor demo:** use a normal mouse in the right hand and a Joy-Con in the left for ten minutes of scrubbing/markers/undo. Confirm no unintended edits during ordinary hand movement.
3. **OBS demo:** scene/mute commands acknowledged by OBS before a vibration cue. A disconnected API connection produces a visible error and no false success vibration.
4. **Two-player demo:** independently identify two pairs, assign slots, verify all buttons and rejoin after one controller sleeps.
5. **Blender demo:** orbit/pan/zoom a model with an explicit clutch; undo any data-changing operation; closing the add-on releases the input route.

These five reproducible recordings, with test manifests, are more valuable than an unqualified “supports every game” headline.
