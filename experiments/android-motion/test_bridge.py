import argparse
import math
import socketserver
import tempfile
import threading
import unittest
from pathlib import Path
from bridge import Console, Freshness, axes, transform


class Handler(socketserver.StreamRequestHandler):
    def handle(self):
        self.wfile.write(b'Android Console: Authentication required\r\nOK\r\n')
        authenticated = False
        for raw in self.rfile:
            text = raw.decode().strip()
            self.server.commands.append(text)
            if text.startswith('auth '):
                authenticated = text == 'auth secret-test-token'
                self.wfile.write(b'OK\n' if authenticated else b'KO: authentication failed\n')
            elif not authenticated or text == 'sensor get missing':
                self.wfile.write(b'KO: unavailable\n')
            elif text == 'sensor status':
                # Multiple lines and fragmented response exercise framed reading.
                self.wfile.write(b'acceleration: enabled\r\n')
                self.wfile.flush()
                self.wfile.write(b'gyroscope: enabled\r\nOK\r\n')
            else:
                self.wfile.write(b'OK\n')


class Tests(unittest.TestCase):
    def test_rotations(self):
        self.assertEqual(transform((1, 2, 3), axes('x,z,-y')), (1, 3, -2))
        self.assertEqual(transform((1, 2, 3), axes('-x,-y,z')), (-1, -2, 3))
        for value in ('x,x,z', 'x,y', 'x,y,-z', 'x,y,NaN', 'x,y,z\nauth x'):
            with self.assertRaises(argparse.ArgumentTypeError):
                axes(value)

    def test_stale_individual_sensor(self):
        fresh = Freshness()
        self.assertTrue(fresh.check((1, 1), 0))
        self.assertTrue(fresh.check((2, 1), 0.4))
        with self.assertRaises(RuntimeError):
            fresh.check((3, 1), 0.6)

    def test_missing_sensor_timestamp(self):
        fresh = Freshness()
        self.assertFalse(fresh.check((0, 0), 0))
        with self.assertRaises(RuntimeError):
            fresh.check((0, 0), 0.6)

    def test_console_roundtrip(self):
        with tempfile.TemporaryDirectory() as directory, socketserver.TCPServer(('127.0.0.1', 0), Handler) as server:
            server.commands = []
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            token = Path(directory) / 'token'
            token.write_text('secret-test-token')
            client = None
            try:
                client = Console(server.server_address[1], token)
                self.assertIn('gyroscope: enabled', client.command('sensor status'))
                client.set_sensor('acceleration', (1, 9.80665, 3))
                self.assertIn('sensor set acceleration 1:9.80665:3', server.commands)
                with self.assertRaises(RuntimeError):
                    client.command('sensor get missing')
                for values in ((math.nan, 0, 0), (math.inf, 0, 0), (0, 0)):
                    with self.assertRaises(ValueError):
                        client.set_sensor('gyroscope', values)
                with self.assertRaises(ValueError):
                    client.command('sensor status\nauth bad')
                client.neutral()
                self.assertEqual(server.commands[-1], 'sensor set gyroscope 0:0:0')
                client.close()
                client = None
                token.write_text('wrong-token')
                with self.assertRaisesRegex(RuntimeError, '^Emulator console authentication failed$'):
                    Console(server.server_address[1], token)
            finally:
                if client:
                    client.close()
                server.shutdown()
                thread.join()


if __name__ == '__main__':
    unittest.main()
