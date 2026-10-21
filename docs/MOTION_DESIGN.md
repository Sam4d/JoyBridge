# Motion design specification

**Proposed. Not implemented in v0.1.** The existing source never enables or reads the SDL motion sensors. Preserve that distinction in UI and release notes.

## Motion modes

| Mode | Behaviour | Typical use | Required controls |
| --- | --- | --- | --- |
| Relative gyro mouse | Rotation rate integrated over sample time becomes mouse deltas | PC aim and pointer | Gain, clutch, deadband, optional smoothing, inversion |
| Gravity-aware aim | Project calibrated rotation into a user/gravity-aligned frame | Changing grip/posture | Orientation estimate, confidence indicator, recenter |
| Gyro to virtual stick | Rotation rate becomes bounded stick deflection | Games accepting only controller camera input | Response curve, saturation, backend calibration |
| Tilt to axis | Orientation relative to a stored neutral pose becomes an axis | Steering, flight, parameter dial | Neutral, angular range, hysteresis, spring behaviour |
| Flick stick + gyro | Stick chooses heading changes; gyro supplies fine aim and vertical control | Compatible shooters | Per-game mouse-turn calibration and flick timing |
| Air mouse | Low gain pointer with a held motion-enable button | Couch desktop and presentations | Click stabilization, clutch, recenter and scroll layer |
| Roll dial | Twist becomes bounded or relative parameter changes | Timeline, brush size, volume | Clutch, step size, acceleration and limits |
| Gated gesture | Deliberate motion while armed emits a discrete action | Undo, next slide, tool switch | Confidence, cooldown, cancel and haptic feedback |
| Raw motion stream | Timestamped sensor data sent to a consumer | Emulators and developer tools | Coordinate/units mapping and consumer compatibility |

A mode selects an output contract. “Gyro support” alone does not mean a game accepts raw gyro data. Xbox-style output has no standard gyro field; mouse emulation and a motion protocol are separate paths. Motion-as-stick inherits the game's stick deadzone and acceleration and can feel less direct than mouse aim. Do not describe both as equivalent.

## Sensor pipeline

Use a dedicated acquisition loop, independent of GUI repainting. The prototype's 16 ms Windows timer must not determine sensor integration time. Prefer backend sensor timestamps; measure host receipt time separately. SDL defines gyro in radians/second and accelerometer in metres/second squared, including gravity, and defines left/right Joy-Con sensor variants [S08]. Query capabilities and enable the exact supported sensors; missing sensors disable the feature visibly.

1. Identify physical device and side; normalize the backend coordinate convention once.
2. Apply known device/factory calibration from a supported reader; do not write device flash.
3. Reject nonfinite values, out-of-order timestamps, implausible ranges and stale samples.
4. Estimate gyro zero-rate bias only during an explicit or confidently stationary window. A deliberate slow turn must not be calibrated away.
5. Fuse gyro and gravity evidence into orientation. Use a proven candidate such as GamepadMotionHelpers after checking its units, integration contract and license [S06]; do not casually mix degrees and radians.
6. Map orientation/rate into the user's calibrated grip and selected mode.
7. Apply bounded filtering, deadband/curve and clutch policy; preserve fractional mouse residuals.
8. Route to a named sink. When stale/disconnected, clear residuals, neutralize outputs and cancel gestures. Reconnection begins a new time epoch.

Default gyro smoothing should be minimal and explicit. Offer separate low-speed smoothing rather than a heavy moving average across all movement. Expose filter delay and measured noise; do not market smoothing as free accuracy.

For a relative-mouse axis, start from `delta = angular_rate * sample_dt * gain`, after bias and coordinate conversion. Gain has explicit units of mouse counts per radian. A real-world sensitivity ratio also depends on the game's degrees-per-count setting. Estimate it through a guided in-game turn test, not guessed per-title magic values. Field-of-view and aim-down-sights scaling need profile-specific validation.

## Calibration flow

- Show both sensors and invite the user to place each Joy-Con still for a short measured window.
- Collect enough valid samples and stationary time; report progress rather than using one fixed sleep.
- Reject calibration when motion or vibration exceeds thresholds; provide a retry explanation.
- Record mean bias, variance, valid sample count, duration, timestamp quality and controller identity.
- Ask for natural grip; record neutral orientation separately from sensor bias.
- Run a prompted left/right/up/down test to establish signs and intended axes.
- Provide an optional fine-target task to select comfortable gain, without claiming medical or skill assessment.
- Persist calibration locally with backend/device version. Invalidate or recheck if identity or sensor convention changes.

No magnetometer is listed for original Joy-Cons [S07]. Gravity helps correct roll/pitch but does not supply an absolute yaw reference. Offer recentering and relative pointer modes; explain heading drift. Integrating acceleration twice is not a viable way to obtain stable hand position. External optical tracking would be a separate sensor system.

## Two hands

Default gaming role: left hand movement/actions, right gyro aim. Permit left gyro aim for handedness and single-handed setups. Optional second-hand functions include a modifier-held lean/scroll/zoom axis or independent creative parameter.

Do not average both hands' orientation without a shared-frame calibration and a reason. Independent hands intentionally move differently. A two-handed steering metaphor can use one designated orientation source or a carefully calibrated combination, but not inferred distance between the controllers. Publish which sensor owns each output; arbitration must be deterministic.

## Gesture engine

Start with explicit, finite-state recognizers: roll-left/right, short upward flick, deliberate shake, and orientation hold. Require an arm button by default. Include threshold hysteresis, minimum duration, cooldown, return-to-neutral and cancellation. A recognizer emits once per completed gesture and logs why it rejected candidates. Trigger key sequences through the ordinary output arbiter so gesture cancellation releases modifiers.

Personal gesture recording can come later: record positive examples plus normal gameplay/editor motions as negatives, evaluate false positives locally, and display uncertainty. It should not silently turn random movement into commands. Never require cloud AI for the input loop.

## Haptics

Use short, bounded patterns for calibration success, layer changes, player identification and parameter detents. Support intensity limits and disable haptics during bias calibration. Send stop on profile changes and shutdown. Native game rumble must be routed back from the correct virtual slot to the assigned hand(s). Rich HD effects require a verified backend; conventional amplitude rumble is a useful first step. No game-specific damage/reload haptic without game telemetry or an explicit approximation label.

## Tests required before integration

- Unit tests: radians/degrees conversion, axis transforms, integration at several sample rates, neutral-pose handling, finite-number rejection, fractional-delta conservation.
- Replay tests: stationary trace, slow intentional turn, rapid turn, vibration, reconnect clock reset, out-of-order/stale samples, packet gaps.
- Gesture tests: intended examples and normal-action negatives; measure false activations, not just recognizer success on ideal examples.
- Hardware: both Joy-Con sides, combined/separate mode, two adapters, different battery levels and concurrent Bluetooth traffic.
- User task: controlled target acquisition and a ten-minute creative workflow; compare identical sensitivity/conditions against existing tools.

Do not claim measured latency from a configured polling interval. Record sensor-to-host, engine and output timings separately; end-to-end game response requires a separate measurement method.
