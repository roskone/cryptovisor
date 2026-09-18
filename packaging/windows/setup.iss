; Inno Setup 6 — установщик Криптовизора.
; Компиляция из корня проекта после PyInstaller:
;   ISCC.exe packaging\windows\setup.iss
; Результат: dist\CryptoVisor-Setup-1.0.0.exe

#define AppName "Криптовизор"
#define AppId "CryptoVisor"
#define AppVersion "1.0.0"
#define AppExe "CryptoVisor.exe"
#define SourceDir "..\..\dist\CryptoVisor"

[Setup]
AppId={{27DCD33C-39FB-48A2-B214-0979B23B95C5}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher=CryptoVisor
DefaultDirName={autopf}\{#AppId}
DefaultGroupName={#AppName}
UninstallDisplayIcon={app}\{#AppExe}
UninstallDisplayName={#AppName}
OutputDir=..\..\dist
OutputBaseFilename={#AppId}-Setup-{#AppVersion}
SetupIconFile=..\..\assets\icon.ico
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
; ставится без прав администратора (в {localappdata}), если их нет — удобно для лекционных ПК
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
DisableProgramGroupPage=yes
ShowLanguageDialog=no

[Languages]
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExe}"
Name: "{group}\{cm:UninstallProgram,{#AppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExe}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExe}"; Description: "{cm:LaunchProgram,{#AppName}}"; Flags: nowait postinstall skipifsilent
