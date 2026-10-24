"""JoyBridge gaming UI: one SDL combined Joy-Con pair -> one virtual Xbox pad."""
import ctypes as C
import os
from pathlib import Path
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'experiments/android-motion'))
from bridge import SDL


def stick(value, deadzone=5000):
    if abs(value) <= deadzone:
        return 0
    return max(-32768, min(32767, round((abs(value)-deadzone)/(32767-deadzone)*32767)*(1 if value > 0 else -1)))


class Gaming:
    def __init__(self, root, demo=False):
        self.root, self.demo = root, demo
        self.sdl = self.controller = self.pad = None
        self.running = False
        self.selected_id = None
        root.title('JoyBridge • PC Gaming')
        root.geometry('780x630')
        root.resizable(False, False)
        root.configure(bg='#101827')
        style = ttk.Style(); style.theme_use('clam')
        style.configure('TButton', font=('Segoe UI', 11), padding=10)
        frame = tk.Frame(root, bg='#101827', padx=30, pady=24); frame.pack(fill='both', expand=True)
        def label(text, size=11, color='#afc4df'):
            tk.Label(frame, text=text, font=('Segoe UI', size), fg=color, bg='#101827', anchor='w', justify='left', wraplength=710).pack(fill='x', pady=(0,10))
        label('JoyBridge', 28, 'white')
        label('Two Joy-Cons. One PC controller.', 16, '#52dfb2')
        label('Slide both Joy-Cons into your grip. Pair each half with Windows once.')
        row = tk.Frame(frame,bg='#101827'); row.pack(fill='x',pady=8)
        for name, fn in [('Find / pair Joy-Cons', self.pair), ('Refresh connection', self.refresh), ('Driver setup', self.driver)]:
            ttk.Button(row,text=name,command=fn).pack(side='left',padx=(0,8))
        self.connection = tk.StringVar(value='Looking for your Joy-Con pair…')
        tk.Label(frame,textvariable=self.connection,bg='#1d2d46',fg='white',font=('Segoe UI',14),padx=16,pady=18,wraplength=680,justify='left',anchor='w').pack(fill='x',pady=12)
        self.status=tk.StringVar(value='Connect both halves, then choose Start controller.')
        tk.Label(frame,textvariable=self.status,bg='#101827',fg='#f5cd84',font=('Segoe UI',11),wraplength=710,justify='left',anchor='w').pack(fill='x',pady=8)
        actions=tk.Frame(frame,bg='#101827');actions.pack(fill='x',pady=8)
        self.start=ttk.Button(actions,text='Start controller',command=self.enable);self.start.pack(side='left',padx=(0,8))
        ttk.Button(actions,text='Stop',command=self.stop).pack(side='left',padx=(0,8))
        ttk.Button(actions,text='Test in Windows',command=lambda: os.startfile('joy.cpl')).pack(side='left')
        self.layout=tk.StringVar(value='position')
        ttk.Checkbutton(frame,text='Use Nintendo button letters (otherwise use Xbox button positions)',command=self.neutral,variable=self.layout,onvalue='letters',offvalue='position').pack(anchor='w',pady=12)
        self.live=tk.StringVar(value='Live input: controller stopped')
        tk.Label(frame,textvariable=self.live,bg='#1d2d46',fg='#91eccf',font=('Consolas',11),padx=14,pady=16,justify='left',anchor='w').pack(fill='x',pady=10)
        label('Works with games that accept Xbox/XInput controllers.\nFor keyboard-only games, use the legacy keyboard mapper.\nKeep JoyBridge open while playing. Stop other remappers to avoid duplicate input.',10)
        ttk.Button(frame,text='Help and game setup',command=self.help).pack(anchor='w')
        if demo:
            self.connection.set('Left Joy-Con  +  Right Joy-Con\nCombined pair detected — ready')
            self.status.set('Demo preview • no physical controllers connected')
            self.live.set('Left stick  X:     0  Y:     0\nRight stick X:     0  Y:     0\nButtons: none     ZL: 0     ZR: 0')
        else:
            try:
                dll=Path(getattr(sys,'_MEIPASS',Path(__file__).parent))/'SDL2.dll'
                self.sdl=SDL(dll, combine=True)
                lib=self.sdl.lib
                for name, result, args in [('SDL_GameControllerGetButton',C.c_uint8,[C.c_void_p,C.c_int]),('SDL_GameControllerGetAxis',C.c_int16,[C.c_void_p,C.c_int]),('SDL_JoystickGetDeviceInstanceID',C.c_int32,[C.c_int])]:
                    f=getattr(lib,name);f.restype=result;f.argtypes=args
                self.refresh()
            except Exception as e:
                self.status.set('Controller reader could not start: '+str(e))
            root.after(16,self.tick)
            root.after(1500,self.rescan)
        root.protocol('WM_DELETE_WINDOW',self.close)

    def pair(self):
        if self.demo:return
        self.stop()
        messagebox.showinfo('Pair both halves','1. Hold the small SYNC button on the left Joy-Con until its lights chase.\n2. In Bluetooth settings, choose Add device → Bluetooth → Joy-Con (L).\n3. Repeat for Joy-Con (R).\n4. Return here and choose Refresh connection.\n\nAlready paired? Press a button on each half to reconnect.')
        os.startfile('ms-settings:bluetooth')

    def driver(self):
        if messagebox.askokcancel('Xbox controller driver','JoyBridge needs ViGEmBus to create an Xbox controller.\n\nThis third-party driver is retired and no longer maintained. Download only from its official GitHub release page. Installing it needs Windows administrator approval and may need a restart.\n\nOpen the official download page?'):
            webbrowser.open('https://github.com/nefarius/ViGEmBus/releases/tag/v1.22.0')

    def refresh(self):
        if not self.sdl or self.demo:return
        self.sdl.pump();lib=self.sdl.lib
        pairs=[];names=[]
        for i in range(lib.SDL_NumJoysticks()):
            name=(lib.SDL_GameControllerNameForIndex(i) or b'').decode(errors='replace')
            if 'Joy-Con' in name:
                names.append(name)
                if 'L/R' in name: pairs.append(i)
        if self.controller and not lib.SDL_GameControllerGetAttached(self.controller):
            self.stop();lib.SDL_GameControllerClose(self.controller);self.controller=None;self.selected_id=None
        if len(pairs)!=1:
            self.stop()
            if self.controller:lib.SDL_GameControllerClose(self.controller);self.controller=None;self.selected_id=None
            self.connection.set('More than one pair found. Connect just your grip pair.' if len(pairs)>1 else 'Waiting for both halves\n'+('Detected: '+', '.join(names) if names else 'No Joy-Cons connected'))
            return
        device_id=lib.SDL_JoystickGetDeviceInstanceID(pairs[0])
        if self.selected_id != device_id:
            self.stop()
            if self.controller:lib.SDL_GameControllerClose(self.controller)
            self.controller=lib.SDL_GameControllerOpen(pairs[0]);self.selected_id=device_id
        self.connection.set('Left Joy-Con  +  Right Joy-Con\nCombined pair detected — ready' if self.controller else 'Could not open the pair. Close other remappers and refresh.')

    def rescan(self):
        self.refresh();self.root.after(1500,self.rescan)

    def enable(self):
        if self.demo:return
        if not self.controller:
            self.status.set('Connect both Joy-Cons first. Choose Find / pair Joy-Cons.');return
        if self.running:return
        try:
            import vgamepad as vg
            self.vg=vg
            self.pad=vg.VX360Gamepad()
            self.running=True
            self.status.set('Controller active • open your game and enable its gamepad controls.')
        except Exception:
            self.pad=None
            self.status.set('Xbox output unavailable. Choose Driver setup, install ViGEmBus, then reopen JoyBridge.')

    def neutral(self):
        if self.pad:self.pad.reset();self.pad.update()

    def stop(self):
        self.running=False
        try:self.neutral()
        except Exception:pass
        self.pad=None
        self.status.set('Controller stopped. Connect both halves, then choose Start controller.')

    def tick(self):
        try:
            if self.sdl:self.sdl.pump()
            if self.controller:
                lib=self.sdl.lib
                if not lib.SDL_GameControllerGetAttached(self.controller):self.refresh()
                else:
                    buttons=[lib.SDL_GameControllerGetButton(self.controller,i) for i in range(15)]
                    a=[lib.SDL_GameControllerGetAxis(self.controller,i) for i in range(6)]
                    self.live.set(f'Left stick  X:{a[0]:6}  Y:{a[1]:6}\nRight stick X:{a[2]:6}  Y:{a[3]:6}\nButtons: '+(','.join(str(i) for i,b in enumerate(buttons) if b) or 'none')+f'   ZL:{int(a[4]>16000)} ZR:{int(a[5]>16000)}')
                    if self.running:
                        self.pad.reset()
                        # SDL physical positions A B X Y, back guide start, sticks, shoulders, dpad.
                        masks=[0x1000,0x2000,0x4000,0x8000,0x20,0x400,0x10,0x40,0x80,0x100,0x200,1,2,4,8]
                        if self.layout.get()=='letters':masks[:4]=[0x2000,0x1000,0x8000,0x4000]
                        for b,m in zip(buttons,masks):
                            if b:self.pad.press_button(button=self.vg.XUSB_BUTTON(m))
                        self.pad.left_joystick(x_value=stick(a[0]),y_value=max(-32768,min(32767,-stick(a[1]))))
                        self.pad.right_joystick(x_value=stick(a[2]),y_value=max(-32768,min(32767,-stick(a[3]))))
                        self.pad.left_trigger(value=255 if a[4]>16000 else 0)
                        self.pad.right_trigger(value=255 if a[5]>16000 else 0)
                        self.pad.update()
        except Exception:
            self.stop();self.status.set('Connection interrupted. Refresh connection, then Start controller again.')
        self.root.after(16,self.tick)

    def help(self):
        messagebox.showinfo('Playing PC games','Use a Bluetooth-capable Windows x64 PC. A normal grip holds the Joy-Cons; it does not combine their Bluetooth connections. Pair L and R separately.\n\nStart controller before opening the game. Select Controller/Gamepad in game settings. Test in Windows shows an Xbox 360 controller when output is active.\n\nIf controls happen twice, close Steam Input or other remappers for this controller. Games seeing physical Joy-Cons too may need HidHide configured separately.\n\nRacing triggers are digital on Joy-Cons. No gyro aiming, force feedback, or universal game compatibility is claimed. Hardware testing is still pending.')

    def close(self):
        self.stop()
        if self.sdl:
            if self.controller:self.sdl.lib.SDL_GameControllerClose(self.controller)
            self.sdl.lib.SDL_Quit()
        self.root.destroy()


if __name__=='__main__':
    root=tk.Tk();app=Gaming(root,demo='--demo' in sys.argv or '--screenshot' in sys.argv)
    if '--screenshot' in sys.argv:
        def capture():
            from PIL import ImageGrab
            root.update()
            ImageGrab.grab((root.winfo_rootx(),root.winfo_rooty(),root.winfo_rootx()+780,root.winfo_rooty()+630)).save('gaming-ui.png')
            root.destroy()
        root.after(1500,capture)
    root.mainloop()
