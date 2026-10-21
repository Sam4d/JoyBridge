"""Beginner-facing Windows setup and launch UI for the experimental motion lab."""
import os
import platform
import queue
import socket
import subprocess
import sys
import threading
import time
import tkinter as tk
from tkinter import messagebox, ttk
import webbrowser
from pathlib import Path
import runtime

ROOT = Path(os.environ.get('LOCALAPPDATA', str(Path.home()))) / 'JoyBridge' / 'DanceLab'
BUNDLE = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).parent
PORT = 5580


class App:
    def __init__(self, window):
        self.window = window
        self.events = queue.Queue()
        self.cancelled = threading.Event()
        self.busy = False
        self.phone = self.motion = None
        self.devices = []
        self.buttons = []
        window.title('JoyBridge • Dance Lab')
        window.geometry('760x690')
        window.minsize(700, 650)
        window.configure(bg='#101827')
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TButton', font=('Segoe UI', 11), padding=10)
        outer = tk.Frame(window, bg='#101827', padx=28, pady=22)
        outer.pack(fill='both', expand=True)
        self.label(outer, 'Your Joy-Con. A lighter way to dance.', 22, '#ffffff')
        self.label(outer, 'Guided setup • No Android Studio • No commands to type', 11, '#9ab2d4')
        self.label(outer, 'Experimental: Just Dance Now compatibility has not been verified.', 10, '#f6c56f')
        self.row(outer, '1', 'Prepare your virtual phone', 'Downloads Android once. Allow 16 GB of free space.', 'Prepare', self.prepare)
        self.row(outer, '2', 'Connect your Joy-Con', 'Hold its small SYNC button until the lights chase, then add it in Bluetooth.', 'Bluetooth settings', lambda: os.startfile('ms-settings:bluetooth'))
        self.row(outer, '3', 'Start your virtual phone', 'Sign in to Google Play in the phone window. Install Just Dance Now.', 'Start phone', self.start_phone)
        self.row(outer, '4', 'Choose your controller', 'Close the original JoyBridge mapper before continuing.', 'Find Joy-Cons', self.find)
        self.choice = ttk.Combobox(outer, state='readonly', font=('Segoe UI', 11))
        self.choice.pack(fill='x', pady=(0, 8))
        actions = tk.Frame(outer, bg='#101827')
        actions.pack(fill='x')
        for title, fn in [('Start motion', self.start_motion), ('Stop motion', self.stop_motion), ('Open dance screen', lambda: webbrowser.open('https://justdancenow.com/'))]:
            button = ttk.Button(actions, text=title, command=fn)
            button.pack(side='left', padx=(0, 8))
            if title != 'Stop motion':
                self.buttons.append(button)
        self.status = tk.StringVar(value='Start with Prepare. You only need to download Android once.')
        tk.Label(outer, textvariable=self.status, wraplength=690, justify='left', bg='#1c2b42', fg='white', font=('Segoe UI', 11), padx=14, pady=14).pack(fill='x', pady=16)
        bottom = tk.Frame(outer, bg='#101827')
        bottom.pack(fill='x')
        ttk.Button(bottom, text='Cancel setup', command=self.cancelled.set).pack(side='left')
        ttk.Button(bottom, text='Help', command=self.help).pack(side='left', padx=8)
        ttk.Button(bottom, text='Diagnostics', command=self.logs).pack(side='right')
        self.window.protocol('WM_DELETE_WINDOW', self.close)
        self.window.after(100, self.tick)

    def label(self, parent, text, size, color):
        tk.Label(parent, text=text, font=('Segoe UI', size), fg=color, bg='#101827', anchor='w', wraplength=690, justify='left').pack(fill='x', pady=(0, 7))

    def row(self, parent, number, title, detail, action, fn):
        row = tk.Frame(parent, bg='#101827')
        row.pack(fill='x', pady=8)
        text = tk.Frame(row, bg='#101827')
        text.pack(side='left', fill='x', expand=True)
        tk.Label(text, text=number + '  ' + title, fg='white', bg='#101827', font=('Segoe UI', 13, 'bold'), anchor='w').pack(fill='x')
        tk.Label(text, text=detail, fg='#a8bad2', bg='#101827', font=('Segoe UI', 10), wraplength=470, anchor='w', justify='left').pack(fill='x')
        button = ttk.Button(row, text=action, command=fn)
        button.pack(side='right', padx=(10, 0))
        self.buttons.append(button)

    def report(self, text):
        self.events.put(('status', text))

    def work(self, task):
        if self.busy:
            return
        self.busy = True
        self.cancelled.clear()
        for button in self.buttons:
            button.state(['disabled'])
        def run():
            try:
                task()
            except Exception as error:
                ROOT.mkdir(parents=True, exist_ok=True)
                with (ROOT / 'setup.log').open('a', encoding='utf-8') as log:
                    log.write(type(error).__name__ + ': ' + str(error) + '\n')
                if isinstance(error, (OSError, TimeoutError)):
                    self.report('That step could not finish. Check your internet connection, then try again. Details are in Diagnostics.')
                else:
                    self.report(str(error))
            finally:
                self.events.put(('done', None))
        threading.Thread(target=run, daemon=True).start()

    def tick(self):
        latest = None
        while True:
            try:
                kind, value = self.events.get_nowait()
            except queue.Empty:
                break
            if kind == 'status':
                latest = value
            elif kind == 'done':
                self.busy = False
                for button in self.buttons:
                    button.state(['!disabled'])
            elif kind == 'licenses':
                self.window.after(0, lambda p=value: self.licenses(p))
            elif kind == 'devices':
                self.devices = value
                self.choice['values'] = [name for _, name in value]
                if value:
                    self.choice.current(0)
        if latest:
            self.status.set(latest)
        if self.motion is not None and self.motion.poll() is not None:
            code = self.motion.returncode
            self.motion = None
            self.status.set('Motion stopped.' if code == 0 else 'Motion stopped. Reconnect your Joy-Con and check that the phone is open. See Diagnostics for details.')
        self.window.after(100, self.tick)

    def prepare(self):
        if self.phone and self.phone.poll() is None:
            messagebox.showinfo('Close phone first', 'Close the virtual phone before preparing or updating its files.')
            return
        if platform.machine().lower() not in ('amd64', 'x86_64'):
            messagebox.showinfo('PC compatibility', 'This experimental build needs a 64-bit Intel or AMD Windows PC.')
            return
        def task():
            self.report('Checking Android download details…')
            self.events.put(('licenses', runtime.catalog()))
        self.work(task)

    def licenses(self, packages):
        dialog = tk.Toplevel(self.window)
        dialog.title('Android download terms')
        dialog.geometry('700x520')
        dialog.transient(self.window)
        dialog.grab_set()
        gb = sum(p['size'] for p in packages) / 1e9
        ttk.Label(dialog, text=f'Download {gb:.1f} GB directly from Google. Review its terms before continuing.', wraplength=650, padding=15).pack()
        box = tk.Text(dialog, wrap='word', padx=12, pady=8)
        box.pack(fill='both', expand=True, padx=15)
        box.insert('1.0', '\n\n'.join(dict.fromkeys(p['license'] for p in packages)))
        box.configure(state='disabled')
        accepted = tk.BooleanVar()
        button = ttk.Button(dialog, text='Accept and download', state='disabled')
        ttk.Checkbutton(dialog, text='I have read and accept these Android terms', variable=accepted, command=lambda: button.configure(state='normal' if accepted.get() else 'disabled')).pack(pady=8)
        def proceed():
            dialog.destroy()
            def task():
                runtime.install(ROOT, packages, self.report, self.cancelled)
                self.report('Your virtual phone is prepared. Connect your Joy-Con, then choose Start phone.')
            self.work(task)
        button.configure(command=proceed)
        button.pack(pady=(0, 12))

    def start_phone(self):
        def task():
            emulator = ROOT / 'sdk/emulator/emulator.exe'
            if not emulator.exists() or not (ROOT / 'phones/JoyBridge.avd/config.ini').exists():
                raise RuntimeError('Choose Prepare first to download your virtual phone.')
            if self.phone and self.phone.poll() is None:
                self.report('Your phone is already open. Switch to its window.')
                return
            result = runtime.run([emulator, '-accel-check'], env=runtime.environment(ROOT))
            if result.returncode:
                (ROOT / 'pc-check.log').write_text(result.stdout + result.stderr, encoding='utf-8')
                raise RuntimeError('Windows needs virtualization enabled. Open Help for the two setup checks, then restart your PC.')
            with socket.socket() as check:
                try:
                    check.bind(('127.0.0.1', PORT))
                except OSError:
                    raise RuntimeError('A virtual phone is already using this connection. Close it, then try again.') from None
            with (ROOT / 'phone.log').open('w', encoding='utf-8') as log:
                self.phone = subprocess.Popen([str(emulator), '-avd', 'JoyBridge', '-port', str(PORT), '-no-snapshot', '-no-boot-anim'], env=runtime.environment(ROOT), stdout=log, stderr=log, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
            self.report('Starting your phone… The first start can take a few minutes.')
            adb = ROOT / 'sdk/platform-tools/adb.exe'
            for _ in range(90):
                if self.cancelled.is_set():
                    self.report('Stopped waiting. You can close the phone window.')
                    return
                if self.phone.poll() is not None:
                    raise RuntimeError('The phone could not start. Open Diagnostics to see its startup report.')
                try:
                    boot = runtime.run([adb, '-s', f'emulator-{PORT}', 'shell', 'getprop', 'sys.boot_completed'])
                    if boot.stdout.strip() == '1':
                        self.report('Phone ready. Open Play Store inside it and install Just Dance Now. Then choose Find Joy-Cons.')
                        return
                except subprocess.TimeoutExpired:
                    pass
                time.sleep(2)
            raise RuntimeError('The phone is taking longer than expected. Check its window; if stuck, close it and try again.')
        self.work(task)

    def find(self):
        def task():
            result = runtime.run([BUNDLE / 'JoyBridge-Motion-Lab.exe', '--list'])
            if result.returncode:
                raise RuntimeError('Could not read controllers. Close other controller apps and try again.')
            devices = []
            for line in result.stdout.splitlines():
                index, sep, name = line.partition(': ')
                if sep and index.isdigit():
                    devices.append((index, name + ' (' + index + ')'))
            self.events.put(('devices', devices))
            self.report('Choose your Joy-Con, then Start motion.' if devices else 'No Joy-Con found yet. Hold SYNC and add it in Windows Bluetooth settings, then try again.')
        self.work(task)

    def start_motion(self):
        if self.motion and self.motion.poll() is None:
            return
        index = self.choice.current()
        if index < 0 or index >= len(self.devices):
            messagebox.showinfo('Connect controller', 'Choose Find Joy-Cons and select a controller first.')
            return
        device = self.devices[index][0]
        def task():
            check = runtime.run([BUNDLE / 'JoyBridge-Motion-Lab.exe', '--check', '--port', str(PORT)])
            if check.returncode:
                raise RuntimeError('Start your virtual phone first and wait for its home screen.')
            ROOT.mkdir(parents=True, exist_ok=True)
            with (ROOT / 'motion.log').open('w', encoding='utf-8') as log:
                self.motion = subprocess.Popen([str(BUNDLE / 'JoyBridge-Motion-Lab.exe'), '--device', device, '--port', str(PORT), '--stop-file', str(ROOT / 'stop-motion')], stdout=log, stderr=log, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
            self.report('Motion bridge started. Open the dance screen and join its room in the phone app. Scoring is still experimental.')
        (ROOT / 'stop-motion').unlink(missing_ok=True)
        self.work(task)

    def stop_motion(self):
        ROOT.mkdir(parents=True, exist_ok=True)
        (ROOT / 'stop-motion').touch()
        self.status.set('Stopping motion…')

    def help(self):
        dialog = tk.Toplevel(self.window)
        dialog.title('Help getting started')
        ttk.Label(dialog, padding=20, wraplength=570, text='If the PC check asks for virtualization:\n\n1. Open Windows features, tick Windows Hypervisor Platform, and restart. Windows may ask for administrator approval.\n\n2. If it still fails, check Task Manager → Performance → CPU → Virtualization. If disabled, your PC manufacturer’s instructions explain how to enable it in firmware.\n\nGoogle Play sign-in happens only inside your phone window. Just Dance Now may be unavailable or incompatible in the virtual phone. We have not yet verified a complete dance session.\n\nUse a wrist strap. If motion looks wrong, stop and report it; grip calibration is still experimental.').pack()
        ttk.Button(dialog, text='Open Windows features', command=lambda: subprocess.Popen(['optionalfeatures.exe'])).pack(pady=10)
        ttk.Button(dialog, text='Detailed guide', command=lambda: webbrowser.open('https://github.com/Sam4d/JoyBridge/tree/main/experiments/android-motion')).pack(pady=10)

    def logs(self):
        ROOT.mkdir(parents=True, exist_ok=True)
        os.startfile(str(ROOT))

    def close(self):
        self.cancelled.set()
        self.stop_motion()
        self.window.destroy()


if __name__ == '__main__':
    window = tk.Tk()
    App(window)
    if '--smoke-test' in sys.argv:
        window.after(500, window.destroy)
    window.mainloop()
