#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
sdl=vendor/SDL2-2.32.10/x86_64-w64-mingw32
if [[ ! -f "$sdl/lib/libSDL2.dll.a" ]]; then
  echo 'Run python3 scripts/fetch_sdl.py first.' >&2
  exit 1
fi
mkdir -p dist
cp "$sdl/bin/SDL2.dll" dist/SDL2.dll
cp vendor/SDL2-2.32.10/LICENSE.txt dist/LICENSE-SDL.txt
cp LICENSE dist/LICENSE.txt
cp resources/Quick-Start.txt dist/Quick-Start.txt
x86_64-w64-mingw32-gcc -std=c11 -O2 -Wall -Wextra -Werror \
  -municode -mwindows -static-libgcc -I"$sdl/include/SDL2" src/main.c \
  -L"$sdl/lib" -lSDL2 -lbthprops -lcomctl32 -lshell32 -lgdi32 -luser32 -lm \
  -o dist/JoyBridge.exe
x86_64-w64-mingw32-gcc -std=c11 -Wall -Wextra -Werror -fanalyzer \
  -fsyntax-only -I"$sdl/include/SDL2" src/main.c
makensis -V2 setup.nsi
