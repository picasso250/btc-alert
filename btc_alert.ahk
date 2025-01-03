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

; 创建托盘图标  
A_IconTip := "BTC价格监控"
TraySetIcon("shell32.dll", 44)  ; 使用系统自带的股票相关图标（44号图标是股票图表）

; 每分钟更新价格
SetTimer(UpdatePrices, 60000)
UpdatePrices()  ; 立即执行一次

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

StdOutToVar(cmd) {
    shell := ComObject("WScript.Shell")
    exec := shell.Exec(cmd)
    return exec.StdOut.ReadAll()
}

UpdatePrices() {
    ; 调用python脚本获取最新价格
    try {
        ; 使用COM对象捕获python输出
        output := StdOutToVar('pythonw.exe get_latest_prices.py')
        
        ; 更新托盘提示
        A_IconTip := output
    } catch as e {
        A_IconTip := "获取价格失败: " e.Message
        ; 记录错误到日志文件
        try {
            FileAppend("[" A_Now "] " e.Message "`n", A_ScriptDir "\error.log")
        }
    }
}
