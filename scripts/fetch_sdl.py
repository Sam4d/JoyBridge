#!/usr/bin/env python3
"""Fetch a checksum-pinned SDL2 build dependency; never execute downloaded code."""
from pathlib import Path, PurePosixPath
import hashlib
import shutil
import tarfile
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
VERSION = "2.32.10"
ARCHIVE_SHA256 = "83a5d74012311edc3c0d40ea6faecbe57ad692aa033fa5dc273cc937e3938ff2"
URL = f"https://libsdl.org/release/SDL2-devel-{VERSION}-mingw.tar.gz"


def sha256(path):
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def main():
    cache = ROOT / ".cache"
    cache.mkdir(exist_ok=True)
    archive = cache / f"SDL2-devel-{VERSION}-mingw.tar.gz"
    if not archive.exists() or sha256(archive) != ARCHIVE_SHA256:
        temporary = archive.with_suffix(".download")
        try:
            with urllib.request.urlopen(URL, timeout=60) as response, temporary.open("wb") as output:
                shutil.copyfileobj(response, output)
            if sha256(temporary) != ARCHIVE_SHA256:
                raise RuntimeError("SDL archive checksum mismatch; refusing extraction")
            temporary.replace(archive)
        finally:
            temporary.unlink(missing_ok=True)
    vendor = ROOT / "vendor"
    prefix = f"SDL2-{VERSION}/x86_64-w64-mingw32/"
    selected = {prefix + "lib/libSDL2.dll.a", prefix + "bin/SDL2.dll", f"SDL2-{VERSION}/LICENSE.txt"}
    extracted = 0
    with tarfile.open(archive, "r:gz") as bundle:
        for entry in bundle:
            if not entry.isfile() or not (entry.name in selected or entry.name.startswith(prefix + "include/")):
                continue
            parts = PurePosixPath(entry.name)
            if parts.is_absolute() or ".." in parts.parts:
                raise RuntimeError("Unsafe archive member")
            destination = vendor / entry.name
            destination.parent.mkdir(parents=True, exist_ok=True)
            with bundle.extractfile(entry) as source, destination.open("wb") as output:
                shutil.copyfileobj(source, output)
            extracted += 1
    for relative in selected:
        if not (vendor / relative).is_file():
            raise RuntimeError(f"Missing dependency: {relative}")
    print(f"SDL2 {VERSION} verified; extracted {extracted} build files")


if __name__ == "__main__":
    main()
