; Inno Setup script for SecureSFTPClient
[Setup]
AppName=Secure SFTP Client
AppVersion=1.0.0
DefaultDirName={pf}\SecureSFTPClient
DefaultGroupName=Secure SFTP Client
OutputBaseFilename=SecureSFTPClient_Installer
SetupIconFile=..\logo.ico
Compression=lzma
SolidCompression=yes

[Files]
Source: "..\dist\SecureSFTPClient.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\logo.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Secure SFTP Client"; Filename: "{app}\SecureSFTPClient.exe"; WorkingDir: "{app}"; IconFilename: "{app}\logo.ico"
Name: "{commondesktop}\Secure SFTP Client"; Filename: "{app}\SecureSFTPClient.exe"; WorkingDir: "{app}"; IconFilename: "{app}\logo.ico"

[Run]
Filename: "{app}\SecureSFTPClient.exe"; Description: "Launch Secure SFTP Client"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: files; Name: "{app}\SecureSFTPClient.exe"
Type: files; Name: "{app}\logo.ico"
