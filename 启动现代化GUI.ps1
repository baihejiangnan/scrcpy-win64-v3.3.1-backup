# PowerShell脚本 - Scrcpy现代化控制中心启动器
# 设置控制台编码为UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 设置窗口标题
$Host.UI.RawUI.WindowTitle = "Scrcpy现代化控制中心"

Write-Host ""
Write-Host "=========================================="
Write-Host "   🎮 Scrcpy 现代化投屏控制中心 v2.0"
Write-Host "=========================================="
Write-Host ""
Write-Host "正在启动现代化界面..." -ForegroundColor Green
Write-Host ""

try {
    # 启动Python程序
    python scrcpy_gui_modern.py
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "❌ 启动失败，请检查Python环境是否正确安装" -ForegroundColor Red
        Write-Host ""
        Read-Host "按任意键退出"
    }
}
catch {
    Write-Host ""
    Write-Host "❌ 发生错误: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Read-Host "按任意键退出"
} 