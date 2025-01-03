#Requires AutoHotkey v2.0
SendMode("Input")
SetWorkingDir(A_ScriptDir)

; 启动python脚本
try {
    Run("pythonw.exe check_and_alert.py",,, &PID)
    ; 定期检查python进程是否仍在运行
    SetTimer(CheckPythonProcess, 5000)
} catch as e {
    MsgBox("启动python脚本失败: " e.Message)
}

; 显示启动消息
Run('show_msg.ahk "BTC价格监控" "程序已启动"')

; 创建托盘图标  
A_IconTip := "BTC价格监控"
TraySetIcon("shell32.dll", 44)  ; 使用系统自带的股票相关图标（44号图标是股票图表）

; 右键菜单
A_TrayMenu.Delete()
A_TrayMenu.Add("退出", ExitScript)

; 保持脚本运行
Return

CheckPythonProcess() {
    if !ProcessExist(PID) {
        MsgBox("警告：python进程已意外终止！")
        SetTimer(CheckPythonProcess, 0)  ; 停止定时器
    }
}

ExitScript(*) {
    ; 终止python进程
    ProcessClose(PID)
    ExitApp()
}
