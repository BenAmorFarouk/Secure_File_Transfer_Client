; NSIS Installer script for SecureSFTPClient
; Create with NSIS (makensis SecureSFTPClient_installer.nsi)

!define APP_NAME "Secure SFTP Client"
!define APP_EXE "SecureSFTPClient.exe"
!define APP_DIR "${PROGRAMFILES64}\SecureSFTPClient"
!define VERSION "1.0.0"

OutFile "SecureSFTPClient_Installer.exe"
InstallDir "$PROGRAMFILES\SecureSFTPClient"
InstallDirRegKey HKLM "Software\${APP_NAME}" "Install_Dir"
RequestExecutionLevel admin

; Pages
Page directory
Page instfiles
Page uninstConfirm

; Language files
!include "MUI2.nsh"

Section "Install"
  SetOutPath "$INSTDIR"
  File /oname=${APP_EXE} "..\dist\${APP_EXE}"
  File "..\logo.ico"

  ; Create Start Menu shortcut
  CreateDirectory "$SMPROGRAMS\${APP_NAME}"
  CreateShortCut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" "$INSTDIR\\${APP_EXE}" "" "$INSTDIR\\logo.ico" 0

  ; Create Desktop shortcut
  CreateShortCut "$DESKTOP\\${APP_NAME}.lnk" "$INSTDIR\\${APP_EXE}" "" "$INSTDIR\\logo.ico" 0

  ; Write uninstall info
  WriteRegStr HKLM "Software\${APP_NAME}" "Install_Dir" "$INSTDIR"
  WriteUninstaller "$INSTDIR\\Uninstall.exe"
SectionEnd

Section "Uninstall"
  ; Remove shortcuts
  Delete "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk"
  RMDir "$SMPROGRAMS\${APP_NAME}"
  Delete "$DESKTOP\\${APP_NAME}.lnk"

  ; Remove files
  Delete "$INSTDIR\\${APP_EXE}"
  Delete "$INSTDIR\\logo.ico"
  Delete "$INSTDIR\\Uninstall.exe"

  ; Remove directory
  RMDir "$INSTDIR"

  ; Remove registry
  DeleteRegKey HKLM "Software\${APP_NAME}"
SectionEnd
