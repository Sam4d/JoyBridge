#!/usr/bin/env python3
"""Check packaging contracts. Does not run Windows or test Joy-Con hardware."""
from pathlib import Path
import hashlib
import json
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def pe_machine(path):
    data = path.read_bytes()
    if len(data) < 64 or data[:2] != b"MZ":
        raise RuntimeError(f"Not a PE executable: {path.name}")
    offset = struct.unpack_from("<I", data, 0x3C)[0]
    if data[offset:offset + 4] != b"PE\0\0":
        raise RuntimeError(f"Invalid PE signature: {path.name}")
    return struct.unpack_from("<H", data, offset + 4)[0]


def main():
    app = ROOT / "dist/JoyBridge.exe"
    sdl = ROOT / "dist/SDL2.dll"
    setup = ROOT / "JoyBridge-Setup.exe"
    if pe_machine(app) != 0x8664 or pe_machine(sdl) != 0x8664:
        raise RuntimeError("Application and SDL must both be Windows x64")
    if pe_machine(setup) not in (0x14C, 0x8664):
        raise RuntimeError("Unexpected installer architecture")
    expected = {"bthprops.cpl", "gdi32.dll", "kernel32.dll", "msvcrt.dll", "shell32.dll", "user32.dll", "sdl2.dll"}
    dump = subprocess.check_output(["x86_64-w64-mingw32-objdump", "-p", str(app)], text=True)
    imports = {line.split("DLL Name:", 1)[1].strip().lower() for line in dump.splitlines() if "DLL Name:" in line}
    if imports - expected or "sdl2.dll" not in imports:
        raise RuntimeError(f"Unexpected or missing dependencies: {sorted(imports)}")
    for name in ("LICENSE.txt", "LICENSE-SDL.txt", "Quick-Start.txt"):
        if not (ROOT / "dist" / name).is_file():
            raise RuntimeError(f"Missing packaged documentation: {name}")
    hashes = {str(f.relative_to(ROOT)): hashlib.sha256(f.read_bytes()).hexdigest() for f in (app, sdl, setup)}
    report = {"status": "build-verified-only", "checks": ["x64 application and SDL", "installer PE", "application imports", "licenses and quick start"], "sha256": hashes, "not_tested": ["Windows execution", "installer interaction", "Bluetooth pairing", "physical Joy-Con input", "game compatibility"]}
    (ROOT / "dist/build-verification.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
