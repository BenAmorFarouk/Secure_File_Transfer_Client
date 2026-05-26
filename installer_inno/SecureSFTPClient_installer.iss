; Inno Setup script for Secure SFTP Client
; Professional installer with modern UI and features

[Setup]
AppName=Secure SFTP Client
AppVersion=1.0.0
AppPublisher=Secure File Transfer
AppPublisherURL=https://github.com
AppSupportURL=https://github.com
AppUpdatesURL=https://github.com
DefaultDirName={pf}\SecureSFTPClient
DefaultGroupName=Secure SFTP Client
AllowNoIcons=yes
OutputDir=..\dist
OutputBaseFilename=SecureSFTPClient_Installer
SetupIconFile=..\logo.ico
WizardStyle=modern
WizardImageFile=..\high-resolution-color-logo.png
WizardSmallImageFile=..\logo.ico
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64
ArchitecturesAllowed=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "..\dist\SecureSFTPClient.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\logo.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\high-resolution-color-logo.png"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Secure SFTP Client"; Filename: "{app}\SecureSFTPClient.exe"; WorkingDir: "{app}"; IconFilename: "{app}\logo.ico"; Comment: "Launch Secure SFTP Client"
Name: "{commondesktop}\Secure SFTP Client"; Filename: "{app}\SecureSFTPClient.exe"; WorkingDir: "{app}"; IconFilename: "{app}\logo.ico"; Comment: "Launch Secure SFTP Client"
Name: "{group}\Uninstall Secure SFTP Client"; Filename: "{uninstallexe}"; Comment: "Uninstall Secure SFTP Client"

[Run]
Filename: "{app}\SecureSFTPClient.exe"; Description: "Launch Secure SFTP Client"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: files; Name: "{app}\SecureSFTPClient.exe"
Type: files; Name: "{app}\logo.ico"
Type: files; Name: "{app}\high-resolution-color-logo.png"
Type: dirifempty; Name: "{app}"

[Code]
procedure InitializeWizard;
begin
  WizardForm.Caption := 'Secure SFTP Client Setup';
end;
