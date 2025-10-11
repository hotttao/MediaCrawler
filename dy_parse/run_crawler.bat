@echo off
cd /d G:\github\MediaCrawler

:: 将 uv run 的输出重定向到 crawler.log
uv run main.py --platform dy --type creator --lt qrcode --get_comment 0 --save_data_option db > crawler.log 2>&1

echo Crawling finished. Shutting down in 10 seconds...
shutdown /s /f /t 10
exit /b