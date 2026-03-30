"""
Windows 定时任务管理脚本
用于添加和删除 MediaCrawler 相关定时任务
"""

import argparse
import subprocess
import sys
from datetime import datetime


TASK_NAME = "MediaCrawler_FullCrawl"
SCRIPT_PATH = r"d:\Code\media\MediaCrawler\command\run_full_crawl.py"
WORKING_DIR = r"d:\Code\media\MediaCrawler"

TRIGGER_TIMES = ["00:20", "08:20", "16:20", "22:20", "23:40"]


def get_powershell_cmd(action: str) -> list[str]:
    """生成 PowerShell 命令"""
    ps_script = f"""
$ErrorActionPreference = 'Stop'

$taskName = '{TASK_NAME}'
$scriptPath = '{SCRIPT_PATH}'
$workingDir = '{WORKING_DIR}'
$triggerTimes = @({','.join(f"'{t}'" for t in TRIGGER_TIMES)})

function Create-TaskWithTriggers() {{
    $existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    if ($existingTask) {{
        Write-Host "任务 '$taskName' 已存在，正在删除..."
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    }}

    $action = New-ScheduledTaskAction -Execute "cmd" -Argument "/c cd /d $workingDir && uv run -m command.run_full_crawl" -WorkingDirectory $workingDir

    $triggers = @()
    foreach ($time in $triggerTimes) {{
        $trigger = New-ScheduledTaskTrigger -Daily -At $time
        $triggers += $trigger
    }}

    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $triggers -Settings $settings -Description "MediaCrawler 完整爬取任务"

    Write-Host "任务创建成功!"
    Write-Host "执行时间: $($triggerTimes -join ', ')"
}}

function Remove-Task() {{
    $existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    if (-not $existingTask) {{
        Write-Host "任务 '$taskName' 不存在"
        return
    }}
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    Write-Host "任务 '$taskName' 已删除"
}}

function List-Task() {{
    $existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    if (-not $existingTask) {{
        Write-Host "任务 '$taskName' 不存在"
        return
    }}
    Get-ScheduledTask -TaskName $taskName | Get-ScheduledTaskInfo | Format-List
}}

function Run-Task() {{
    $existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    if (-not $existingTask) {{
        Write-Host "任务 '$taskName' 不存在"
        return
    }}
    Start-ScheduledTask -TaskName $taskName
    Write-Host "任务已触发执行"
}}

switch ('{action}') {{
    'add' {{ Create-TaskWithTriggers }}
    'remove' {{ Remove-Task }}
    'delete' {{ Remove-Task }}
    'list' {{ List-Task }}
    'run' {{ Run-Task }}
}}
"""
    return ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_script]


def run_command(cmd: list[str]) -> tuple[int, str, str]:
    """执行命令并返回结果"""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=WORKING_DIR,
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)


def main():
    parser = argparse.ArgumentParser(description="Windows 定时任务管理")
    parser.add_argument(
        "action",
        choices=["add", "remove", "delete", "list", "run"],
        help="操作: add(添加) | remove/delete(删除) | list(查看) | run(立即执行)",
    )
    args = parser.parse_args()

    print(f"=== MediaCrawler 定时任务管理 ===")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    cmd = get_powershell_cmd(args.action)
    code, stdout, stderr = run_command(cmd)

    if stdout:
        print(stdout)
    if stderr:
        print(f"错误: {stderr}", file=sys.stderr)

    if code != 0 and "不存在" not in stdout:
        sys.exit(code)


if __name__ == "__main__":
    main()
