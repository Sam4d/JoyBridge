Unicode True
!include "MUI2.nsh"
Name "JoyBridge"
OutFile "JoyBridge-Setup.exe"
InstallDir "$LOCALAPPDATA\Programs\JoyBridge"
RequestExecutionLevel user
SetCompressor /SOLID lzma
!define MUI_ABORTWARNING
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!define MUI_FINISHPAGE_RUN "$INSTDIR\JoyBridge.exe"
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "English"
Section "JoyBridge"
SetOutPath "$INSTDIR"
File "dist\JoyBridge.exe"
File "dist\SDL2.dll"
File "dist\LICENSE-SDL.txt"
File "dist\LICENSE.txt"
File "dist\Quick-Start.txt"
WriteUninstaller "$INSTDIR\Uninstall.exe"
CreateDirectory "$SMPROGRAMS\JoyBridge"
CreateShortcut "$SMPROGRAMS\JoyBridge\JoyBridge.lnk" "$INSTDIR\JoyBridge.exe"
CreateShortcut "$SMPROGRAMS\JoyBridge\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
CreateShortcut "$DESKTOP\JoyBridge.lnk" "$INSTDIR\JoyBridge.exe"
WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\JoyBridge" "DisplayName" "JoyBridge 0.1"
WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\JoyBridge" "UninstallString" '"$INSTDIR\Uninstall.exe"'
WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\JoyBridge" "DisplayVersion" "0.1.0"
WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\JoyBridge" "NoModify" 1
WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\JoyBridge" "NoRepair" 1
SectionEnd
Section "Uninstall"
Delete "$INSTDIR\JoyBridge.exe"
Delete "$INSTDIR\SDL2.dll"
Delete "$INSTDIR\LICENSE-SDL.txt"
Delete "$INSTDIR\LICENSE.txt"
Delete "$INSTDIR\Quick-Start.txt"
Delete "$INSTDIR\Uninstall.exe"
RMDir "$INSTDIR"
Delete "$DESKTOP\JoyBridge.lnk"
Delete "$SMPROGRAMS\JoyBridge\JoyBridge.lnk"
Delete "$SMPROGRAMS\JoyBridge\Uninstall.lnk"
RMDir "$SMPROGRAMS\JoyBridge"
DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\JoyBridge"
SectionEnd
