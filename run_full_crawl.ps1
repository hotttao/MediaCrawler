# 抖音爬虫完整抓取流程
param(
    [switch]$SkipCalIncr
)

$ErrorActionPreference = "Stop"
$workDir = "D:\Code\media\MediaCrawler"
$success = $false
$step1Result = ""
$step2Result = ""
$startTime = Get-Date

Set-Location $workDir

# 步骤1: 抓取数据
Write-Host "========== [Step 1] Starting Douyin Crawler ==========" -ForegroundColor Green
try {
    uv run main.py --platform dy --type creator --lt qrcode --get_comment 0 --save_data_option db 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "========== [Step 1] Crawler SUCCESS ==========" -ForegroundColor Green
        $success = $true
        $step1Result = "✅ 成功"
    } else {
        Write-Host "========== [Step 1] Crawler FAILED (exit code: $LASTEXITCODE) ==========" -ForegroundColor Red
        $step1Result = "❌ 失败 (exit code: $LASTEXITCODE)"
    }
} catch {
    Write-Host "========== [Step 1] Crawler EXCEPTION: $_ ==========" -ForegroundColor Red
    $step1Result = "❌ 异常: $_"
    $success = $false
}

# 步骤2: 计算日增（仅在步骤1成功时执行）
if ($success -and -not $SkipCalIncr) {
    Write-Host "========== [Step 2] Calculating Daily Increment ==========" -ForegroundColor Green
    try {
        $env:PYTHONPATH = $workDir
        & ".\.venv\Scripts\python.exe" "command\cal_day_incr.py" 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "========== [Step 2] Calculation SUCCESS ==========" -ForegroundColor Green
            $step2Result = "✅ 成功"
        } else {
            Write-Host "========== [Step 2] Calculation FAILED (exit code: $LASTEXITCODE) ==========" -ForegroundColor Red
            $step2Result = "❌ 失败 (exit code: $LASTEXITCODE)"
        }
    } catch {
        Write-Host "========== [Step 2] Calculation EXCEPTION: $_ ==========" -ForegroundColor Red
        $step2Result = "❌ 异常: $_"
    }
} elseif (-not $success) {
    Write-Host "========== [Step 2] SKIPPED (Step 1 failed) ==========" -ForegroundColor Yellow
    $step2Result = "⏭️ 已跳过（Step 1 失败）"
}

$endTime = Get-Date
$duration = ($endTime - $startTime).TotalSeconds

Write-Host "========== Workflow Complete ==========" -ForegroundColor Green

# 构建通知消息
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$overallStatus = if ($success) { "✅ 成功" } else { "❌ 失败" }

$notification = @"
【抖音爬虫任务完成】

⏰ 执行时间: $timestamp
⏱️ 耗时: $([Math]::Round($duration, 2)) 秒

📊 执行结果:
  • Step 1 (抓取数据): $step1Result
  • Step 2 (计算日增): $step2Result

🎯 整体状态: $overallStatus
"@

Write-Host $notification

# 返回退出码
if ($success) { exit 0 } else { exit 1 }
