@echo off

set TASK_NAME=MediaCrawler_Dy_Creator
set SCRIPT_PATH=G:\github\MediaCrawler\dy_parse\run_crawler.bat

if "%1"=="" goto add_task
if "%1"=="check" goto check_task
if "%1"=="add" goto add_task

echo Usage:
echo   %0               - Add the scheduled task
echo   %0 check         - Check if task exists
goto end


:add_task
echo Adding scheduled task: %TASK_NAME%
echo Calling script: %SCRIPT_PATH%

:: 删除旧任务（如果存在）
schtasks /query /tn "%TASK_NAME%" >nul 2>&1
if %errorlevel% equ 0 (
    echo Task "%TASK_NAME%" already exists. Deleting...
    schtasks /delete /tn "%TASK_NAME%" /f
    if %errorlevel% equ 0 (
        echo SUCCESS: Old task deleted.
    ) else (
        echo WARNING: Failed to delete old task.
    )
)

:: 创建新任务：以当前用户交互式运行
echo Creating new task (interactive mode)...
schtasks /create /tn "%TASK_NAME%" ^
    /tr "%SCRIPT_PATH%" ^
    /sc daily ^
    /st 19:23 ^
    /f ^
    /ru %USERDOMAIN%\%USERNAME% ^
    /rl HIGHEST ^
    /it

if %errorlevel% equ 0 (
    echo SUCCESS: Task created successfully.
    echo IMPORTANT: This task will only run when you are logged in with desktop session.
) else (
    echo FAILED: Could not create task. Please run as Administrator.
)
goto end

:check_task
echo Checking task: %TASK_NAME%
schtasks /query /tn "%TASK_NAME%" >nul 2>&1
if %errorlevel% equ 0 (
    echo SUCCESS: Task "%TASK_NAME%" exists.
    echo.
    :: 显示任务详细信息（英文输出）
    schtasks /query /tn "%TASK_NAME%" /fo LIST /v 
) else (
    echo ERROR: Task "%TASK_NAME%" does NOT exist.
)
goto end

:end
pause