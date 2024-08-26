[Setup]
AppName=Auto App Starter
AppVersion=1.0
DefaultDirName={pf}\AutoAppStarter
DefaultGroupName=Auto App Starter
OutputDir=.
OutputBaseFilename=AutoAppStarterInstaller
Compression=lzma
SolidCompression=yes

[Files]
; Main application
Source: ".\src\recorder.exe"; DestDir: "{app}"; Flags: ignoreversion
; Auto-start script
Source: ".\src\opener.py"; DestDir: "{app}"; Flags: ignoreversion
Source: ".\src\opener.bat"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Auto App Starter"; Filename: "{app}\recorder.exe"
Name: "{group}\Uninstall Auto App Starter"; Filename: "{uninstallexe}"

[Run]
; Add the auto-start script to the startup folder
Filename: "{app}\opener.bat"; Description: "Register Auto-Start Script"; Flags: runhidden

[Registry]
; Add a registry entry to run the script at startup (alternative to Startup folder)
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "AutoAppStarter"; ValueData: """{app}\opener.bat"""; Flags: uninsdeletevalue

[UninstallDelete]
; Remove the batch file from the startup folder during uninstall
Type: files; Name: "{app}\opener.bat"
