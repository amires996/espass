#define MyAppName "espass"
#define MyAppVersion "1.1.0"
#define MyAppPublisher "Amir Mohammad Eskandari"
#define MyAppExeName "espass.exe"

[Setup]
AppId={{9A64C1E8-57A2-4C36-A27B-7D1C0B7E5F92}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\Programs\espass
DefaultGroupName=espass
UninstallDisplayIcon={app}\{#MyAppExeName}
SetupIconFile=..\..\assets\icons\espass.ico
OutputDir=..\..\installer
OutputBaseFilename=espass-Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
Uninstallable=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"; Flags: unchecked

[Files]
Source: "..\..\dist\espass\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\espass"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\espass"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch espass"; Flags: postinstall nowait skipifsilent
