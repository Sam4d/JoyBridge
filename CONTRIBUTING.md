# Contributing

Start with docs/ROADMAP.md and docs/COMPATIBILITY.md. Keep commits focused and label proposals separately from implemented behaviour. Do not advertise hardware support from a successful compile alone.

For runtime changes, include tests for the actual failure or contract: disconnect while held, shared bindings, profile transitions, sensor timestamp discontinuities or output failure. Keep captured hardware traces anonymous and opt-in. Unit-test pure engine logic without Bluetooth or a GUI once the engine is extracted.

Build with `python3 scripts/fetch_sdl.py`, `bash build.sh` and `python3 scripts/verify_build.py`. The build uses warnings as errors. Preserve Windows header ordering; .clang-format disables include sorting for that reason.

A hardware report should follow the GitHub template, include exact versions and state what passed/failed. Never include credentials, serials or Bluetooth addresses in public logs. There is no automatic right to bundle third-party code merely because it is available on GitHub; preserve licenses and review dependencies before adding them.
