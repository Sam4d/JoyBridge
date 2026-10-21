# Third-party components

- Original JoyBridge source: MIT, see LICENSE.
- SDL2 2.32.10: downloaded from the official SDL release site; its original LICENSE.txt is copied to dist/LICENSE-SDL.txt and included in the installer. Download hash is pinned in scripts/fetch_sdl.py.
- MinGW and NSIS are build tools. Review the relevant tool/runtime terms when changing compiler or installer distribution.
- No reWASD source, proprietary driver or assets are included.
- JoyShockMapper, GamepadMotionHelpers and Nintendo protocol research are referenced for evaluation; their code is not copied into this repository.
- No virtual-controller driver, gamepad-hiding driver, cloud SDK, OBS client, MIDI library, or Blender add-on is currently bundled.

Licenses and provenance must be checked before integrating any new dependency. The project name is a working name; no trademark-clearance claim is made.
