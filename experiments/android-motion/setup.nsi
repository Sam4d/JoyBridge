Unicode True
!include "MUI2.nsh"
Name "JoyBridge Dance Lab (Experimental)"
OutFile "JoyBridge-Dance-Lab-Setup.exe"
InstallDir "$LOCALAPPDATA\Programs\JoyBridge-Dance-Lab"
RequestExecutionLevel user
!define MUI_ABORTWARNING
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!define MUI_FINISHPAGE_RUN "$INSTDIR\JoyBridge-Dance-Lab.exe"
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "English"
Section "Install"
 SetOutPath "$INSTDIR"
 File "dist/JoyBridge-Dance-Lab.exe"
 File "dist/JoyBridge-Motion-Lab.exe"
 File "dist/Motion-Lab-Readme.md"
 File "dist/LICENSE.txt"
 File "dist/LICENSE-SDL.txt"
 CreateShortcut "$DESKTOP\JoyBridge Dance Lab.lnk" "$INSTDIR\JoyBridge-Dance-Lab.exe"
 CreateDirectory "$SMPROGRAMS\JoyBridge Dance Lab"
 CreateShortcut "$SMPROGRAMS\JoyBridge Dance Lab\JoyBridge Dance Lab.lnk" "$INSTDIR\JoyBridge-Dance-Lab.exe"
 WriteUninstaller "$INSTDIR\Uninstall.exe"
 WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\JoyBridgeDanceLab" "DisplayName" "JoyBridge Dance Lab (Experimental)"
 WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\JoyBridgeDanceLab" "UninstallString" '$"$INSTDIR\Uninstall.exe$"'
SectionEnd
Section "Uninstall"
 Delete "$INSTDIR\JoyBridge-Dance-Lab.exe"
 Delete "$INSTDIR\JoyBridge-Motion-Lab.exe"
 Delete "$INSTDIR\Motion-Lab-Readme.md"
 Delete "$INSTDIR\LICENSE.txt"
 Delete "$INSTDIR\LICENSE-SDL.txt"
 Delete "$INSTDIR\Uninstall.exe"
 RMDir "$INSTDIR"
 Delete "$DESKTOP\JoyBridge Dance Lab.lnk"
 Delete "$SMPROGRAMS\JoyBridge Dance Lab\JoyBridge Dance Lab.lnk"
 RMDir "$SMPROGRAMS\JoyBridge Dance Lab"
 DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\JoyBridgeDanceLab"
 MessageBox MB_OK "The app was removed. Your virtual phone and sign-in data are kept in $LOCALAPPDATA\JoyBridge\DanceLab. Delete that folder manually if you want to remove them too."
SectionEnd
