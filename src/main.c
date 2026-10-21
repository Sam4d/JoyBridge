#ifndef UNICODE
#define UNICODE
#endif
#define _UNICODE
#define SDL_MAIN_HANDLED
#include <windows.h>
#include <bluetoothapis.h>
#include <commctrl.h>
#include <shellapi.h>
#ifndef BLUETOOTH_SERVICE_ENABLE
#define BLUETOOTH_SERVICE_ENABLE 1
#endif
#include <SDL.h>
#include <math.h>
#include <stdio.h>
#define N 25
#define DONE (WM_APP + 1)
static HWND win, status, devices, pairbtn, toggle, combos[N], speedbox, deadbox;
static HFONT font, titlefont;
static SDL_GameController *pads[4];
static int active = 0, held[256], mapping[N], mouseSpeed = 12, deadzone = 8000;
static double remainderX, remainderY;
static HANDLE pairthread;
static wchar_t ini[MAX_PATH];
static const wchar_t *labels[N] = {L"B (south)",
                                   L"A (east)",
                                   L"Y (west)",
                                   L"X (north)",
                                   L"Minus",
                                   L"Home",
                                   L"Plus",
                                   L"Left stick click",
                                   L"Right stick click",
                                   L"L",
                                   L"R",
                                   L"D-pad up",
                                   L"D-pad down",
                                   L"D-pad left",
                                   L"D-pad right",
                                   L"ZL",
                                   L"ZR",
                                   L"Left stick up",
                                   L"Left stick down",
                                   L"Left stick left",
                                   L"Left stick right",
                                   L"Right stick up",
                                   L"Right stick down",
                                   L"Right stick left",
                                   L"Right stick right"};
typedef struct {
  const wchar_t *name;
  int key;
} Choice;
static Choice choices[] = {{L"Unbound", 0},
                           {L"W", 'W'},
                           {L"A", 'A'},
                           {L"S", 'S'},
                           {L"D", 'D'},
                           {L"Space", VK_SPACE},
                           {L"E", 'E'},
                           {L"R", 'R'},
                           {L"Q", 'Q'},
                           {L"F", 'F'},
                           {L"Escape", VK_ESCAPE},
                           {L"Enter", VK_RETURN},
                           {L"Tab", VK_TAB},
                           {L"Shift", VK_SHIFT},
                           {L"Ctrl", VK_CONTROL},
                           {L"Alt", VK_MENU},
                           {L"Up", VK_UP},
                           {L"Down", VK_DOWN},
                           {L"Left", VK_LEFT},
                           {L"Right", VK_RIGHT},
                           {L"Mouse left", 250},
                           {L"Mouse right", 251},
                           {L"Mouse middle", 252},
                           {L"1", '1'},
                           {L"2", '2'},
                           {L"3", '3'},
                           {L"4", '4'},
                           {L"C", 'C'},
                           {L"V", 'V'},
                           {L"X", 'X'},
                           {L"Z", 'Z'},
                           {L"I", 'I'},
                           {L"J", 'J'},
                           {L"K", 'K'},
                           {L"L", 'L'},
                           {L"M", 'M'},
                           {L"N", 'N'},
                           {L"O", 'O'},
                           {L"P", 'P'},
                           {L"T", 'T'},
                           {L"U", 'U'},
                           {L"Y", 'Y'},
                           {L"G", 'G'},
                           {L"H", 'H'},
                           {L"B", 'B'},
                           {L"Backspace", VK_BACK},
                           {L"Delete", VK_DELETE}};
static int choiceCount = sizeof choices / sizeof *choices;
static void output(int key, int down) {
  INPUT x = {0};
  if (key >= 250) {
    x.type = INPUT_MOUSE;
    DWORD a = key == 250   ? MOUSEEVENTF_LEFTDOWN
              : key == 251 ? MOUSEEVENTF_RIGHTDOWN
                           : MOUSEEVENTF_MIDDLEDOWN;
    DWORD b = key == 250   ? MOUSEEVENTF_LEFTUP
              : key == 251 ? MOUSEEVENTF_RIGHTUP
                           : MOUSEEVENTF_MIDDLEUP;
    x.mi.dwFlags = down ? a : b;
  } else {
    x.type = INPUT_KEYBOARD;
    x.ki.wScan = (WORD)MapVirtualKey((UINT)key, MAPVK_VK_TO_VSC);
    if (!x.ki.wScan)
      x.ki.wVk = (WORD)key;
    x.ki.dwFlags =
        (down ? 0 : KEYEVENTF_KEYUP) | (x.ki.wScan ? KEYEVENTF_SCANCODE : 0);
    if ((key >= VK_LEFT && key <= VK_DOWN) || key == VK_DELETE)
      x.ki.dwFlags |= KEYEVENTF_EXTENDEDKEY;
  }
  SendInput(1, &x, sizeof x);
}
static void releaseAll(void) {
  remainderX = remainderY = 0;
  for (int i = 1; i < 256; i++)
    if (held[i]) {
      output(i, 0);
      held[i] = 0;
    }
}
static void stop(void) {
  active = 0;
  releaseAll();
  SetWindowText(toggle, L"Enable mapping");
}
static void defaults(int desktop) {
  int a[N] = {VK_SPACE, 'E', 'R', 'F', VK_TAB, 0,       VK_ESCAPE,
              VK_SHIFT, 'C', 'Q', 'E', VK_UP,  VK_DOWN, VK_LEFT,
              VK_RIGHT, 251, 250, 'W', 'S',    'A',     'D',
              0,        0,   0,   0};
  if (desktop) {
    a[0] = VK_RETURN;
    a[1] = VK_ESCAPE;
    a[2] = 250;
    a[3] = 251;
    a[4] = VK_TAB;
    a[6] = VK_SPACE;
    a[17] = VK_UP;
    a[18] = VK_DOWN;
    a[19] = VK_LEFT;
    a[20] = VK_RIGHT;
  }
  for (int i = 0; i < N; i++)
    mapping[i] = a[i];
}
static void syncCombos(void) {
  for (int i = 0; i < N; i++) {
    int index = 0;
    for (int j = 0; j < choiceCount; j++)
      if (choices[j].key == mapping[i])
        index = j;
    SendMessage(combos[i], CB_SETCURSEL, index, 0);
  }
}
static void save(void) {
  wchar_t key[24], v[24];
  for (int i = 0; i < N; i++) {
    swprintf(key, 24, L"Bind%d", i);
    swprintf(v, 24, L"%d", mapping[i]);
    WritePrivateProfileString(L"Mapping", key, v, ini);
  }
  swprintf(v, 24, L"%d", mouseSpeed);
  WritePrivateProfileString(L"Settings", L"MouseSpeed", v, ini);
  swprintf(v, 24, L"%d", deadzone);
  WritePrivateProfileString(L"Settings", L"Deadzone", v, ini);
}
static void scan(void) {
  for (int p = 0; p < 4; p++)
    if (pads[p] && !SDL_GameControllerGetAttached(pads[p])) {
      SDL_GameControllerClose(pads[p]);
      pads[p] = 0;
    }
  int count = 0;
  for (int j = 0; j < SDL_NumJoysticks(); j++) {
    const char *name = SDL_JoystickNameForIndex(j);
    if (!name || !strstr(name, "Joy-Con") || !SDL_IsGameController(j))
      continue;
    SDL_JoystickID id = SDL_JoystickGetDeviceInstanceID(j);
    int exists = 0;
    for (int p = 0; p < 4; p++)
      if (pads[p] &&
          SDL_JoystickInstanceID(SDL_GameControllerGetJoystick(pads[p])) == id)
        exists = 1;
    if (!exists)
      for (int p = 0; p < 4; p++)
        if (!pads[p]) {
          pads[p] = SDL_GameControllerOpen(j);
          break;
        }
  }
  for (int p = 0; p < 4; p++)
    if (pads[p])
      count++;
  wchar_t s[160];
  swprintf(s, 160, L"Joy-Con devices: %d   |   %ls", count,
           active ? L"Mapping enabled (F8 pauses)" : L"Mapping paused");
  SetWindowText(devices, s);
}
static double curve(int v) {
  double a = fabs((double)v);
  if (a < deadzone)
    return 0;
  double n = (a - deadzone) / (32768 - deadzone);
  return (v < 0 ? -1 : 1) * n * n;
}
static void tick(void) {
  SDL_PumpEvents();
  SDL_Event e;
  while (SDL_PollEvent(&e)) {
  }
  SDL_GameControllerUpdate();
  int want[256] = {0};
  double mx = 0, my = 0;
  int focused = GetForegroundWindow() == win;
  for (int p = 0; p < 4; p++)
    if (pads[p] && SDL_GameControllerGetAttached(pads[p]) && active &&
        !focused) {
      int pressed[N] = {0};
      for (int i = 0; i < 15; i++)
        pressed[i] =
            SDL_GameControllerGetButton(pads[p], (SDL_GameControllerButton)i);
      pressed[15] = SDL_GameControllerGetAxis(
                        pads[p], SDL_CONTROLLER_AXIS_TRIGGERLEFT) > 16000;
      pressed[16] = SDL_GameControllerGetAxis(
                        pads[p], SDL_CONTROLLER_AXIS_TRIGGERRIGHT) > 16000;
      int lx = SDL_GameControllerGetAxis(pads[p], SDL_CONTROLLER_AXIS_LEFTX),
          ly = SDL_GameControllerGetAxis(pads[p], SDL_CONTROLLER_AXIS_LEFTY),
          rx = SDL_GameControllerGetAxis(pads[p], SDL_CONTROLLER_AXIS_RIGHTX),
          ry = SDL_GameControllerGetAxis(pads[p], SDL_CONTROLLER_AXIS_RIGHTY);
      pressed[17] = ly < -deadzone;
      pressed[18] = ly > deadzone;
      pressed[19] = lx < -deadzone;
      pressed[20] = lx > deadzone;
      pressed[21] = ry < -deadzone;
      pressed[22] = ry > deadzone;
      pressed[23] = rx < -deadzone;
      pressed[24] = rx > deadzone;
      for (int i = 0; i < N; i++)
        if (pressed[i] && mapping[i] > 0 && mapping[i] < 256)
          want[mapping[i]] = 1;
      mx += curve(rx) * mouseSpeed;
      my += curve(ry) * mouseSpeed;
    }
  for (int k = 1; k < 256; k++) {
    if (want[k] != held[k]) {
      output(k, want[k]);
      held[k] = want[k];
    }
  }
  if (mx || my) {
    INPUT x = {0};
    x.type = INPUT_MOUSE;
    x.mi.dwFlags = MOUSEEVENTF_MOVE;
    remainderX += mx;
    remainderY += my;
    x.mi.dx = (LONG)round(remainderX);
    x.mi.dy = (LONG)round(remainderY);
    remainderX -= x.mi.dx;
    remainderY -= x.mi.dy;
    SendInput(1, &x, sizeof x);
  } else {
    remainderX = remainderY = 0;
  }
}
static DWORD WINAPI pairWorker(void *unused) {
  (void)unused;
  BLUETOOTH_FIND_RADIO_PARAMS rp = {sizeof rp};
  HANDLE radio = 0;
  HBLUETOOTH_RADIO_FIND rf = BluetoothFindFirstRadio(&rp, &radio);
  int found = 0, ok = 0;
  DWORD err = 0;
  if (rf) {
    do {
      BLUETOOTH_DEVICE_SEARCH_PARAMS sp = {0};
      sp.dwSize = sizeof sp;
      sp.fReturnAuthenticated = TRUE;
      sp.fReturnRemembered = TRUE;
      sp.fReturnUnknown = TRUE;
      sp.fReturnConnected = TRUE;
      sp.fIssueInquiry = TRUE;
      sp.cTimeoutMultiplier = 8;
      sp.hRadio = radio;
      BLUETOOTH_DEVICE_INFO d = {0};
      d.dwSize = sizeof d;
      HBLUETOOTH_DEVICE_FIND df = BluetoothFindFirstDevice(&sp, &d);
      if (df) {
        do {
          if (wcsstr(d.szName, L"Joy-Con (L)") ||
              wcsstr(d.szName, L"Joy-Con (R)")) {
            found++;
            GUID hid = {
                0x1124, 0, 0x1000, {0x80, 0, 0, 0x80, 0x5f, 0x9b, 0x34, 0xfb}};
            DWORD r = BluetoothSetServiceState(radio, &d, &hid,
                                               BLUETOOTH_SERVICE_ENABLE);
            if (r == ERROR_SUCCESS || d.fConnected)
              ok++;
            else
              err = r;
          }
        } while (BluetoothFindNextDevice(df, &d));
        BluetoothFindDeviceClose(df);
      } else
        err = GetLastError();
      CloseHandle(radio);
    } while (BluetoothFindNextRadio(rf, &radio));
    BluetoothFindRadioClose(rf);
  } else
    err = GetLastError();
  wchar_t *s =
      HeapAlloc(GetProcessHeap(), HEAP_ZERO_MEMORY, 640 * sizeof(wchar_t));
  if (s) {
    if (ok)
      swprintf(s, 640,
               L"HID enabled for %d Joy-Con(s). Waiting for Windows to "
               L"connect. If none appear, use Bluetooth settings.",
               ok);
    else
      swprintf(s, 640,
               L"Pair attempt finished: %d found; Windows code %lu. Hold sync "
               L"until LEDs chase and retry, or pair in Bluetooth settings.",
               found, (unsigned long)err);
    PostMessage(win, DONE, 0, (LPARAM)s);
  } else
    PostMessage(win, DONE, 0, 0);
  return 0;
}
static HWND control(const wchar_t *cls, const wchar_t *text, DWORD style, int x,
                    int y, int w, int h, int id) {
  HWND c = CreateWindow(cls, text, WS_CHILD | WS_VISIBLE | style, x, y, w, h,
                        win, (HMENU)(INT_PTR)id, GetModuleHandle(0), 0);
  SendMessage(c, WM_SETFONT, (WPARAM)font, TRUE);
  return c;
}
static LRESULT CALLBACK proc(HWND h, UINT m, WPARAM w, LPARAM l) {
  switch (m) {
  case WM_CREATE: {
    win = h;
    font = CreateFont(17, 0, 0, 0, FW_NORMAL, 0, 0, 0, DEFAULT_CHARSET, 0, 0,
                      CLEARTYPE_QUALITY, 0, L"Segoe UI");
    titlefont = CreateFont(30, 0, 0, 0, FW_SEMIBOLD, 0, 0, 0, DEFAULT_CHARSET,
                           0, 0, CLEARTYPE_QUALITY, 0, L"Segoe UI");
    HWND t = control(L"STATIC", L"JoyBridge", 0, 24, 18, 480, 40, 0);
    SendMessage(t, WM_SETFONT, (WPARAM)titlefont, TRUE);
    control(L"STATIC",
            L"Original Switch Joy-Cons • keyboard + mouse for Windows", 0, 26,
            62, 710, 26, 0);
    pairbtn =
        control(L"BUTTON", L"Pair Joy-Cons", WS_TABSTOP, 24, 100, 160, 36, 1);
    control(L"BUTTON", L"Bluetooth settings", WS_TABSTOP, 194, 100, 175, 36, 2);
    toggle =
        control(L"BUTTON", L"Enable mapping", WS_TABSTOP, 380, 100, 170, 36, 3);
    control(L"BUTTON", L"Save profile", WS_TABSTOP, 562, 100, 150, 36, 4);
    devices =
        control(L"STATIC", L"Detecting controllers...", 0, 26, 150, 700, 26, 0);
    status = control(L"STATIC",
                     L"Hold both SYNC buttons until the LEDs chase, then click "
                     L"Pair Joy-Cons.",
                     0, 26, 181, 690, 48, 0);
    control(L"BUTTON", L"Gaming preset", WS_TABSTOP, 24, 237, 152, 30, 5);
    control(L"BUTTON", L"Desktop preset", WS_TABSTOP, 186, 237, 152, 30, 6);
    control(L"STATIC", L"Mouse speed", 0, 355, 242, 105, 25, 0);
    speedbox = control(L"EDIT", L"12", WS_BORDER | ES_NUMBER | WS_TABSTOP, 462,
                       238, 48, 28, 7);
    control(L"STATIC", L"Deadzone %", 0, 527, 242, 105, 25, 0);
    deadbox = control(L"EDIT", L"24", WS_BORDER | ES_NUMBER | WS_TABSTOP, 639,
                      238, 55, 28, 8);
    for (int i = 0; i < N; i++) {
      int col = i / 13, row = i % 13, x = 24 + col * 352, y = 285 + row * 31;
      control(L"STATIC", labels[i], 0, x, y + 3, 151, 26, 0);
      combos[i] =
          control(L"COMBOBOX", L"", CBS_DROPDOWNLIST | WS_VSCROLL | WS_TABSTOP,
                  x + 155, y, 174, 240, 100 + i);
      for (int j = 0; j < choiceCount; j++)
        SendMessage(combos[i], CB_ADDSTRING, 0, (LPARAM)choices[j].name);
    }
    control(L"STATIC",
            L"Right stick always moves mouse. F8: pause/resume. F9: release + "
            L"pause.\nMapping pauses while this window is focused. Keep it "
            L"open while playing.",
            0, 24, 700, 694, 48, 0);
    syncCombos();
    SetTimer(h, 1, 16, 0);
    SetTimer(h, 2, 1000, 0);
    RegisterHotKey(h, 1, MOD_NOREPEAT, VK_F8);
    RegisterHotKey(h, 2, MOD_NOREPEAT, VK_F9);
    return 0;
  }
  case WM_TIMER:
    if (w == 1)
      tick();
    else
      scan();
    return 0;
  case WM_HOTKEY:
    if (w == 2)
      stop();
    else
      SendMessage(h, WM_COMMAND, 3, 0);
    return 0;
  case WM_COMMAND: {
    int id = LOWORD(w);
    if (id == 1 && !pairthread) {
      stop();
      EnableWindow(pairbtn, FALSE);
      SetWindowText(
          status, L"Scanning Bluetooth radios (about 10 seconds per radio)...");
      pairthread = CreateThread(0, 0, pairWorker, 0, 0, 0);
      if (!pairthread) {
        EnableWindow(pairbtn, TRUE);
        SetWindowText(status,
                      L"Could not start pairing. Use Bluetooth settings.");
      }
    } else if (id == 2)
      ShellExecute(h, L"open", L"ms-settings:bluetooth", 0, 0, SW_SHOWNORMAL);
    else if (id == 3) {
      releaseAll();
      active = !active;
      SetWindowText(toggle, active ? L"Pause mapping" : L"Enable mapping");
      scan();
    } else if (id == 4) {
      stop();
      wchar_t b[24];
      GetWindowText(speedbox, b, 24);
      int s = _wtoi(b);
      GetWindowText(deadbox, b, 24);
      int d = _wtoi(b);
      if (s < 1 || s > 50 || d < 5 || d > 80) {
        MessageBox(h, L"Use mouse speed 1–50 and deadzone 5–80 percent.",
                   L"Check settings", MB_OK);
        return 0;
      }
      mouseSpeed = s;
      deadzone = d * 32768 / 100;
      save();
      SetWindowText(status,
                    L"Profile saved. Enable mapping and switch to your game.");
    } else if (id == 5 || id == 6) {
      stop();
      defaults(id == 6);
      syncCombos();
    } else if (id >= 100 && id < 100 + N && HIWORD(w) == CBN_SELCHANGE) {
      stop();
      int j = SendMessage(combos[id - 100], CB_GETCURSEL, 0, 0);
      if (j >= 0 && j < choiceCount)
        mapping[id - 100] = choices[j].key;
    }
    return 0;
  }
  case DONE:
    if (l) {
      SetWindowText(status, (wchar_t *)l);
      HeapFree(GetProcessHeap(), 0, (void *)l);
    }
    if (pairthread) {
      CloseHandle(pairthread);
      pairthread = 0;
    }
    EnableWindow(pairbtn, TRUE);
    return 0;
  case WM_POWERBROADCAST:
    if (w == PBT_APMSUSPEND)
      stop();
    return TRUE;
  case WM_CLOSE:
    if (pairthread) {
      ShowWindow(h, SW_MINIMIZE);
      SetWindowText(status,
                    L"Wait for Bluetooth scan to finish before closing.");
      return 0;
    }
    DestroyWindow(h);
    return 0;
  case WM_DESTROY:
    releaseAll();
    KillTimer(h, 1);
    KillTimer(h, 2);
    UnregisterHotKey(h, 1);
    UnregisterHotKey(h, 2);
    for (int i = 0; i < 4; i++)
      if (pads[i])
        SDL_GameControllerClose(pads[i]);
    SDL_Quit();
    DeleteObject(font);
    DeleteObject(titlefont);
    PostQuitMessage(0);
    return 0;
  }
  return DefWindowProc(h, m, w, l);
}
int WINAPI wWinMain(HINSTANCE inst, HINSTANCE prev, LPWSTR cmd, int show) {
  (void)prev;
  (void)cmd;
  SetProcessDPIAware();
  HANDLE mutex = CreateMutex(0, TRUE, L"Local\\JoyBridge-0.1");
  if (GetLastError() == ERROR_ALREADY_EXISTS) {
    MessageBox(0, L"JoyBridge is already running.", L"JoyBridge", MB_OK);
    if (mutex)
      CloseHandle(mutex);
    return 0;
  }
  wchar_t dir[MAX_PATH];
  GetEnvironmentVariable(L"LOCALAPPDATA", dir, MAX_PATH);
  wcscat(dir, L"\\JoyBridge");
  CreateDirectory(dir, 0);
  swprintf(ini, MAX_PATH, L"%ls\\profile.ini", dir);
  defaults(0);
  for (int i = 0; i < N; i++) {
    wchar_t k[24];
    swprintf(k, 24, L"Bind%d", i);
    int v = GetPrivateProfileInt(L"Mapping", k, mapping[i], ini);
    mapping[i] = 0;
    for (int j = 0; j < choiceCount; j++)
      if (choices[j].key == v)
        mapping[i] = v;
  }
  mouseSpeed = GetPrivateProfileInt(L"Settings", L"MouseSpeed", 12, ini);
  deadzone = GetPrivateProfileInt(L"Settings", L"Deadzone", 8000, ini);
  if (mouseSpeed < 1 || mouseSpeed > 50)
    mouseSpeed = 12;
  if (deadzone < 1638 || deadzone > 26214)
    deadzone = 8000;
  SDL_SetMainReady();
  SDL_SetHint("SDL_JOYSTICK_HIDAPI", "1");
  SDL_SetHint("SDL_JOYSTICK_HIDAPI_JOY_CONS", "1");
  SDL_SetHint("SDL_JOYSTICK_HIDAPI_COMBINE_JOY_CONS", "1");
  SDL_SetHint("SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS", "1");
  SDL_SetHint("SDL_GAMECONTROLLER_USE_BUTTON_LABELS", "0");
  if (SDL_Init(SDL_INIT_GAMECONTROLLER | SDL_INIT_EVENTS) < 0) {
    MessageBoxA(0, SDL_GetError(), "SDL initialization failed",
                MB_OK | MB_ICONERROR);
    return 1;
  }
  WNDCLASS c = {0};
  c.hInstance = inst;
  c.lpszClassName = L"JoyBridgeWindow";
  c.lpfnWndProc = proc;
  c.hCursor = LoadCursor(0, IDC_ARROW);
  c.hbrBackground = (HBRUSH)(COLOR_WINDOW + 1);
  RegisterClass(&c);
  HWND h =
      CreateWindow(c.lpszClassName, L"JoyBridge 0.1 • Joy-Con mapper",
                   WS_OVERLAPPED | WS_CAPTION | WS_SYSMENU | WS_MINIMIZEBOX,
                   CW_USEDEFAULT, CW_USEDEFAULT, 758, 805, 0, 0, inst, 0);
  wchar_t v[24];
  swprintf(v, 24, L"%d", mouseSpeed);
  SetWindowText(speedbox, v);
  swprintf(v, 24, L"%d", deadzone * 100 / 32768);
  SetWindowText(deadbox, v);
  ShowWindow(h, show);
  MSG msg;
  while (GetMessage(&msg, 0, 0, 0) > 0) {
    if (!IsDialogMessage(h, &msg)) {
      TranslateMessage(&msg);
      DispatchMessage(&msg);
    }
  }
  CloseHandle(mutex);
  return 0;
}
