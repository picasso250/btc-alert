#Requires AutoHotkey v2.0
#Warn

SetWorkingDir A_ScriptDir

PipeName := "\\.\pipe\test_pipe"

; Open the named pipe
hPipe := DllCall("CreateFile"
    , "Str", PipeName
    , "UInt", 0xC0000000  ; GENERIC_READ | GENERIC_WRITE
    , "UInt", 0           ; no sharing 
    , "UInt", 0           ; default security
    , "UInt", 3           ; OPEN_EXISTING
    , "UInt", 0           ; default attributes
    , "UInt", 0           ; no template file
    , "UInt")

if (hPipe = -1) {
    MsgBox("Failed to open pipe")
    ExitApp()
}

; Send messages
messages := ["Hello from AHK", "This is a test", "exit"]

for message in messages {
    ; Write message to pipe
    writeBuffer := Buffer(StrLen(message) * 2, 0)
    StrPut(message, writeBuffer, "UTF-8")
    bytesWritten := 0
    success := DllCall("WriteFile"
        , "Ptr", hPipe
        , "Ptr", writeBuffer.Ptr
        , "UInt", StrLen(message) * 2
        , "UInt*", &bytesWritten
        , "Ptr", 0)
    
    if (!success) {
        MsgBox("Failed to write to pipe")
        break
    }
    
    ; Read response from pipe
    bufferSize := 256
    readBuffer := Buffer(bufferSize, 0)
    bytesRead := 0
    success := DllCall("ReadFile"
        , "Ptr", hPipe
        , "Ptr", readBuffer.Ptr
        , "UInt", bufferSize
        , "UInt*", &bytesRead
        , "Ptr", 0)
    
    if (success && bytesRead > 0) {
        response := StrGet(readBuffer, bytesRead, "UTF-8")
        MsgBox("Received response: " response)
    }
}

; Close pipe handle
DllCall("CloseHandle", "UInt", hPipe)
ExitApp()
