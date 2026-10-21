"""Experimental Joy-Con -> Android Emulator motion bridge. Python 3.11+.
No app protocol emulation and no claim of Just Dance Now compatibility.
"""
import argparse
import ctypes as C
import math
import socket
import sys
import time
from pathlib import Path


class Console:
    """Authenticated, persistent loopback connection; never log the auth token."""
    def __init__(self, port, token_file):
        self.sock = socket.create_connection(('127.0.0.1', port), timeout=2)
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.stream = self.sock.makefile('rb')
        try:
            greeting = self.response()
            if 'Authentication required' in greeting:
                token = Path(token_file).read_text().strip()
                if not token or not token.isascii() or any(c.isspace() for c in token):
                    raise RuntimeError('Invalid emulator console token file')
                try:
                    self.command('auth ' + token)
                except RuntimeError:
                    raise RuntimeError('Emulator console authentication failed') from None
        except BaseException:
            self.close()
            raise

    def response(self):
        lines = []
        total = 0
        while True:
            line = self.stream.readline(4097)
            total += len(line)
            if not line:
                raise ConnectionError('Emulator console disconnected')
            if len(line) > 4096 or total > 65536:
                raise RuntimeError('Oversized emulator console response')
            text = line.decode('utf-8', errors='replace').strip()
            if text == 'OK':
                return '\n'.join(lines)
            if text.startswith('KO'):
                raise RuntimeError('Emulator rejected a command: ' + text)
            lines.append(text)

    def command(self, text):
        if '\n' in text or '\r' in text:
            raise ValueError('Invalid console command')
        self.sock.sendall((text + '\n').encode('ascii'))
        return self.response()

    def set_sensor(self, name, values):
        if name not in ('acceleration', 'gyroscope'):
            raise ValueError('Unsupported sensor')
        if len(values) != 3 or not all(math.isfinite(v) for v in values):
            raise ValueError('Sensor data must contain three finite values')
        self.command('sensor set ' + name + ' ' + ':'.join(f'{v:.7g}' for v in values))

    def neutral(self):
        # A stationary upright phone: keep gravity, remove angular velocity.
        self.set_sensor('acceleration', (0, 9.80665, 0))
        self.set_sensor('gyroscope', (0, 0, 0))

    def close(self):
        self.stream.close()
        self.sock.close()


def axes(value):
    parts = value.lower().split(',')
    if len(parts) != 3 or {p.lstrip('-') for p in parts} != {'x', 'y', 'z'}:
        raise argparse.ArgumentTypeError('Use a signed permutation, e.g. x,z,-y')
    result = tuple(('xyz'.index(p.lstrip('-')), -1 if p.startswith('-') else 1) for p in parts)
    # Only proper rotations: a reflection would transform gyro incorrectly.
    inversions = sum(result[i][0] > result[j][0] for i in range(3) for j in range(i+1, 3))
    if (-1) ** inversions * math.prod(sign for _, sign in result) != 1:
        raise argparse.ArgumentTypeError('Axis mapping must preserve handedness (a rotation)')
    return result


def transform(values, mapping):
    return tuple(values[index] * sign for index, sign in mapping)


class SDL:
    def __init__(self, dll):
        self.lib = C.CDLL(str(Path(dll).resolve()))
        signatures = {
            'SDL_SetHint': (C.c_int, [C.c_char_p, C.c_char_p]),
            'SDL_Init': (C.c_int, [C.c_uint32]),
            'SDL_Quit': (None, []),
            'SDL_GetError': (C.c_char_p, []),
            'SDL_NumJoysticks': (C.c_int, []),
            'SDL_IsGameController': (C.c_int, [C.c_int]),
            'SDL_JoystickGetDeviceVendor': (C.c_uint16, [C.c_int]),
            'SDL_JoystickGetDeviceProduct': (C.c_uint16, [C.c_int]),
            'SDL_GameControllerNameForIndex': (C.c_char_p, [C.c_int]),
            'SDL_GameControllerOpen': (C.c_void_p, [C.c_int]),
            'SDL_GameControllerClose': (None, [C.c_void_p]),
            'SDL_GameControllerGetAttached': (C.c_int, [C.c_void_p]),
            'SDL_GameControllerHasSensor': (C.c_int, [C.c_void_p, C.c_int]),
            'SDL_GameControllerSetSensorEnabled': (C.c_int, [C.c_void_p, C.c_int, C.c_int]),
            'SDL_GameControllerGetSensorDataWithTimestamp': (C.c_int, [C.c_void_p, C.c_int, C.POINTER(C.c_uint64), C.POINTER(C.c_float), C.c_int]),
            'SDL_PollEvent': (C.c_int, [C.c_void_p]),
        }
        for name, (result, args) in signatures.items():
            fn = getattr(self.lib, name)
            fn.restype, fn.argtypes = result, args
        for name, value in {
            'SDL_JOYSTICK_HIDAPI': '1', 'SDL_JOYSTICK_HIDAPI_JOY_CONS': '1',
            'SDL_JOYSTICK_HIDAPI_COMBINE_JOY_CONS': '0',
            'SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS': '1',
        }.items():
            self.lib.SDL_SetHint(name.encode(), value.encode())
        if self.lib.SDL_Init(0x00002000 | 0x00004000) != 0:
            raise RuntimeError(self.lib.SDL_GetError().decode())

    def devices(self):
        self.pump()
        found = {}
        for index in range(self.lib.SDL_NumJoysticks()):
            if (self.lib.SDL_IsGameController(index)
                and self.lib.SDL_JoystickGetDeviceVendor(index) == 0x057e
                and self.lib.SDL_JoystickGetDeviceProduct(index) in (0x2006, 0x2007)):
                found[index] = (self.lib.SDL_GameControllerNameForIndex(index) or b'Joy-Con').decode(errors='replace')
        return found

    def pump(self):
        event = (C.c_uint64 * 8)()  # SDL_Event storage, aligned and >= 56 bytes
        while self.lib.SDL_PollEvent(C.byref(event)):
            pass

    def read(self, controller, sensor):
        values = (C.c_float * 3)()
        stamp = C.c_uint64()
        if self.lib.SDL_GameControllerGetSensorDataWithTimestamp(controller, sensor, C.byref(stamp), values, 3) != 0:
            raise RuntimeError('Unable to read Joy-Con motion sensor')
        return stamp.value, tuple(values)


class Freshness:
    def __init__(self, timeout=0.5):
        self.timeout = timeout
        self.stamps = None
        self.changed = None

    def check(self, stamps, now):
        if self.changed is None:
            self.changed = [now, now]
        for i, stamp in enumerate(stamps):
            if stamp and (self.stamps is None or stamp != self.stamps[i]):
                self.changed[i] = now
        self.stamps = stamps
        if any(now - value > self.timeout for value in self.changed):
            raise RuntimeError('Motion stream stale for over 500 ms; stopped')
        return all(stamps)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    default_dll = Path(getattr(sys, '_MEIPASS', Path(__file__).parent)) / 'SDL2.dll'
    parser.add_argument('--dll', default=str(default_dll))
    parser.add_argument('--list', action='store_true', help='List original Nintendo Joy-Cons')
    parser.add_argument('--check', action='store_true', help='Query emulator sensors without sending motion')
    parser.add_argument('--device', type=int, help='SDL device index from --list')
    parser.add_argument('--port', type=int, default=5554)
    parser.add_argument('--token-file', default=str(Path.home() / '.emulator_console_auth_token'))
    parser.add_argument('--axes', type=axes, default=axes('x,y,z'), help='Phone x,y,z from SDL axes; identity is UNCALIBRATED')
    parser.add_argument('--hz', type=int, default=60, choices=range(10, 121), metavar='10..120')
    parser.add_argument('--stop-file', help='Exit cleanly when this file appears (used by the launcher)')
    args = parser.parse_args(argv)
    if not 5554 <= args.port <= 5584 or args.port % 2:
        parser.error('--port must be an even emulator console port from 5554 to 5584')
    sdl = controller = console = None
    streaming = False
    try:
        if args.check:
            console = Console(args.port, args.token_file)
            print(console.command('sensor status'))
            for name in ('acceleration', 'gyroscope'):
                print(console.command('sensor get ' + name))
            return 0
        sdl = SDL(args.dll)
        devices = sdl.devices()
        if args.list:
            for index, name in devices.items():
                print(f'{index}: {name}')
            if not devices:
                print('No original Joy-Cons found. Pair in Windows Bluetooth settings first.')
            return 0
        if args.device is None:
            if len(devices) != 1:
                raise RuntimeError('Run --list, then select one controller with --device INDEX')
            args.device = next(iter(devices))
        if args.device not in devices:
            raise RuntimeError('Selected device is not an available original Joy-Con')
        controller = sdl.lib.SDL_GameControllerOpen(args.device)
        if not controller:
            raise RuntimeError('Could not open selected Joy-Con')
        for sensor in (1, 2):
            if not sdl.lib.SDL_GameControllerHasSensor(controller, sensor):
                raise RuntimeError('Selected controller does not expose both motion sensors')
            if sdl.lib.SDL_GameControllerSetSensorEnabled(controller, sensor, 1) != 0:
                raise RuntimeError('Could not enable Joy-Con motion sensors')
        console = Console(args.port, args.token_file)
        for name in ('acceleration', 'gyroscope'):
            console.command('sensor get ' + name)
        print('EXPERIMENTAL: sending real motion. Just Dance Now support is UNVERIFIED.')
        print(f'{devices[args.device]} -> emulator {args.port}; requested {args.hz} Hz. Ctrl+C stops.')
        fresh = Freshness()
        count, report = 0, time.monotonic()
        streaming = True
        while True:
            if args.stop_file and Path(args.stop_file).exists():
                print('Stopped by launcher.')
                return 0
            started = time.monotonic()
            sdl.pump()
            if not sdl.lib.SDL_GameControllerGetAttached(controller):
                raise RuntimeError('Joy-Con disconnected; stopped')
            accel_stamp, accel = sdl.read(controller, 1)
            gyro_stamp, gyro = sdl.read(controller, 2)
            if fresh.check((accel_stamp, gyro_stamp), started):
                console.set_sensor('acceleration', transform(accel, args.axes))
                console.set_sensor('gyroscope', transform(gyro, args.axes))
                count += 1
            now = time.monotonic()
            if now - report >= 2:
                print(f'{count/(now-report):.1f} delivered samples/s | accel {tuple(round(v,2) for v in accel)} m/s^2 | gyro {tuple(round(v,2) for v in gyro)} rad/s')
                count, report = 0, now
            time.sleep(max(0, 1 / args.hz - (time.monotonic() - started)))
    except KeyboardInterrupt:
        print('\nStopped.')
        return 0
    except (OSError, RuntimeError, ValueError) as error:
        print(f'Error: {error}', file=sys.stderr)
        return 1
    finally:
        if console:
            if streaming:
                try:
                    console.neutral()
                except (OSError, RuntimeError, ValueError):
                    print('Could not reset virtual sensors. Restart the AVD before continuing.', file=sys.stderr)
            console.close()
        if controller:
            sdl.lib.SDL_GameControllerClose(controller)
        if sdl:
            sdl.lib.SDL_Quit()


if __name__ == '__main__':
    raise SystemExit(main())
