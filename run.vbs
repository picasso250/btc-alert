Set WshShell = WScript.CreateObject("WScript.Shell")
WshShell.Run "cmd /c start /b python check_and_alert.py", 0, False
