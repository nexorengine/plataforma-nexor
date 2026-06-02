Set WshShell = WScript.CreateObject("WScript.Shell")
strDesktop = WshShell.SpecialFolders("Desktop")
strApp = WshShell.CurrentDirectory

' === NEXOR SERVER ===
Set oShortcut = WshShell.CreateShortcut(strDesktop & "\NEXOR SERVER.lnk")
oShortcut.TargetPath = strApp & "\nexor_server.bat"
oShortcut.WorkingDirectory = strApp
oShortcut.IconLocation = strApp & "\nexor_server.ico"
oShortcut.Description = "NEXOR SERVER - Iniciar Servidor"
oShortcut.Save

' === NEXOR QUIZ ===
Set oShortcut2 = WshShell.CreateShortcut(strDesktop & "\NEXOR QUIZ.lnk")
oShortcut2.TargetPath = "http://localhost:8765"
oShortcut2.IconLocation = strApp & "\nexor_quiz.ico"
oShortcut2.Description = "NEXOR QUIZ ENGINE"
oShortcut2.Save

WScript.Echo "Atalhos criados na Area de Trabalho!"
