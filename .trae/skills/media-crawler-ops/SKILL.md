---
name: "media-crawler-ops"
description: "MediaCrawler operations skill - manage Douyin crawler, increment calculation, hot video push, and scheduled tasks. Invoke when user asks to run, configure, or manage MediaCrawler tasks."
---

# MediaCrawler Operations

MediaCrawler 项目运维技能，提供抖音数据爬取、日增计算、热点视频推送和定时任务管理功能。

## 项目入口

| 脚本 | 功能 | 命令 |
|------|------|------|
| `command/run_full_crawl.py` | 爬取 + 日增计算 + 热点推送 | `uv run -m command.run_full_crawl -t YYYY-MM-DD` |
| `command/cal_day_incr.py` | 仅计算日增数据 | `uv run -m command.cal_day_incr -t YYYY-MM-DD -d 15` |
| `command/push_hot_videos.py` | 仅推送热点视频 | `uv run -m command.push_hot_videos -t YYYY-MM-DD -f digg_count -m 20` |
| `command/crawler_cfg.py` | 更新待爬取创作者配置 | `uv run -m command.crawler_cfg` |
| `command/scheduler_task.py` | 管理 Windows 定时任务 | `python -m command.scheduler_task [add\|remove\|list\|run]` |

## 常用操作

### 1. 完整爬取流程（爬取 + 日增 + 热点推送）

```bash
uv run -m command.run_full_crawl -t 2024-01-15 -d 15 -r 1
```

参数：
- `-t`: 目标日期，格式 YYYY-MM-DD
- `-d`: 往前推天数，默认 15
- `-r`: 轮询次数，默认 1

### 2. 仅计算日增

```bash
uv run -m command.cal_day_incr -t 2024-01-15 -d 15
```

### 3. 仅推送热点视频

```bash
uv run -m command.push_hot_videos -t 2024-01-15 -f digg_count -m 20
```

参数：
- `-t`: 数据日期
- `-s`: 视频发布起始时间（默认 target_date 往前 7 天）
- `-f`: 过滤字段（默认 digg_count，可选 comment_count, collect_count 等）
- `-m`: 最小值过滤（默认 20）

### 4. Windows 定时任务管理

```bash
# 添加定时任务（每天 00:20, 08:20, 16:20, 22:20, 23:40 执行）
python -m command.scheduler_task add

# 查看任务状态
python -m command.scheduler_task list

# 立即执行一次
python -m command.scheduler_task run

# 删除定时任务
python -m command.scheduler_task remove
```

## 配置信息

- 数据库：MySQL（通过环境变量配置）
- 通知渠道：飞书（已配置 Webhook）
- 账号管理：`config/account_config.py`

## 执行环境

- Python 虚拟环境：使用 `uv run` 调用
- 工作目录：`d:\Code\media\MediaCrawler`
