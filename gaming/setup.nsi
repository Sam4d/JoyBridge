Unicode True
!include "MUI2.nsh"
Name "JoyBridge PC Gaming"
OutFile "JoyBridge-Gaming-Setup.exe"
InstallDir "$LOCALAPPDATA\Programs\JoyBridge-Gaming"
RequestExecutionLevel user
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!define MUI_FINISHPAGE_RUN "$INSTDIR\JoyBridge-Gaming.exe"
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "English"
Section
SetOutPath "$INSTDIR"
File "dist/JoyBridge-Gaming.exe"
File "LICENSE"
CreateShortcut "$DESKTOP\JoyBridge PC Gaming.lnk" "$INSTDIR\JoyBridge-Gaming.exe"
CreateShortcut "$SMPROGRAMS\JoyBridge PC Gaming.lnk" "$INSTDIR\JoyBridge-Gaming.exe"
WriteUninstaller "$INSTDIR\Uninstall.exe"
WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\JoyBridgeGaming" "DisplayName" "JoyBridge PC Gaming"
WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\JoyBridgeGaming" "UninstallString" '$"$INSTDIR\Uninstall.exe$"'
SectionEnd
Section "Uninstall"
Delete "$DESKTOP\JoyBridge PC Gaming.lnk"
Delete "$SMPROGRAMS\JoyBridge PC Gaming.lnk"
Delete "$INSTDIR\JoyBridge-Gaming.exe"
Delete "$INSTDIR\LICENSE"
Delete "$INSTDIR\Uninstall.exe"
RMDir "$INSTDIR"
DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\JoyBridgeGaming"
SectionEnd
