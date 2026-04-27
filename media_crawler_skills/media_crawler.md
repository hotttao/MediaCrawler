---
name: media-crawler
description: 抖音自媒体平台爬虫工具，支持视频数据抓取、商品信息提取、日增统计等功能
---

# MediaCrawler 项目

**重要：所有命令执行前必须先切换到项目根目录**
```bash
cd D:\Code\media\MediaCrawler
```

抖音自媒体平台爬虫，支持视频数据抓取、商品信息提取、日增统计等。

## 项目结构

```
MediaCrawler/
├── command/                    # 命令行入口脚本
│   ├── crawler_cfg.py         # 创作者配置管理
│   ├── cal_day_incr.py        # 日增数据计算
│   ├── run_full_crawl.py      # 爬取+日增计算入口
│   ├── extract_douyin_user_id.py  # 用户ID提取
│   └── push_hot_videos.py     # 热门视频推送
├── core/                       # 核心模块
│   ├── account_manager.py      # 多账户管理
│   ├── login_manager.py        # 登录管理
│   ├── notifier/              # 通知模块
│   └── task_dispatcher.py      # 任务调度
├── media_platform/douyin/       # 抖音平台爬虫核心
│   ├── core.py                # DouYinCrawler 类
│   ├── client.py              # DouYinClient API 客户端
│   ├── login.py               # 登录逻辑
│   └── help.py                # a_bogus 签名生成
├── store/douyin/               # 数据存储模块
│   └── __init__.py            # update_douyin_aweme 等函数
├── tools/get_product_from_url/  # 商品信息提取工具
│   ├── fetcher.py             # 主入口，获取视频商品信息
│   ├── extractor.py            # 商品信息提取逻辑
│   ├── db_helper.py           # 数据库插入辅助
│   └── main.py                # CLI 入口
├── config/                     # 配置文件
│   ├── base_config.py         # 基础配置（PLATFORM, SAVE_LOGIN_STATE 等）
│   ├── account_config.py      # 多账户配置
│   └── dy_config.py           # 抖音特定配置
├── database/                   # 数据库模型
│   └── models.py              # SQLAlchemy 模型定义
├── browser_data/              # 浏览器登录缓存
│   └── dy_user_data_dir/{nickname}/  # 按用户昵称分目录
└── libs/                      # 第三方库
    ├── douyin.js              # a_bogus 签名 JS
    └── stealth.min.js          # 反检测脚本
```

## 常用命令

### 1. 新增抖音爬虫主页配置
```bash
# --user_id 指定用户主页ID， --update_nickname 添加用户同时自动更新昵称
uv run -m command.crawler_cfg --user_id MS4wLjABAAAA8EoZrCw43AWujry2n4wq63yLNqCxelDngM7hwXT6tY0 --update_nickname

# --remove 删除账户
uv run -m command.crawler_cfg --user_id MS4wLjABAAAA8EoZrCw43AWujry2n4wq63yLNqCxelDngM7hwXT6tY0 --remove

# 更新待爬取账户的昵称
uv run -m command.crawler_cfg --update_nickname
```

### 2. 启动爬虫（多账号轮询）
```bash
uv run main.py --platform dy --type creator --lt qrcode --get_comment 0 --save_data_option db
```

### 3. 计算日增数据
```bash
uv run -m command.cal_day_incr
```

### 4. 爬取 + 日增计算（一键完成）
```bash
uv run -m command.run_full_crawl
uv run -m command.run_full_crawl -t 2025-01-15 -d 7
```

### 5. 从抖音分享链接提取用户ID
```bash
python -m command.extract_douyin_user_id "https://v.douyin.com/mlIAdeKJFxE/"
```

### 6. 从视频链接提取商品信息（并入库）
```bash
python -m tools.get_product_from_url.main "https://www.douyin.com/video/7558626596425518371"
```

## 配置文件

### config/account_config.py - 多账户配置
```python
ACCOUNTS = [
    {
        "account_id": "account_1",
        "nickname": "橙子Mama",
        "phone": "19156537759",
        "cookies": "",
    },
]
```

### .env - 环境变量
```bash
MYSQL_DB_PWD=nUar3Ml90f1xvBSL
MYSQL_DB_USER=root
MYSQL_HOST=192.168.2.38
MYSQL_DB_HOST=192.168.2.38
MYSQL_DB_PORT=3306
MYSQL_DB_NAME=douyin
```

### config/base_config.py - 关键配置
- `PLATFORM = "dy"` - 平台
- `SAVE_LOGIN_STATE = True` - 保存登录状态
- `USER_DATA_DIR = "%s_user_data_dir"` - 浏览器数据目录模板
- `HEADLESS = False` - 是否无头模式
- `CRAWLER_TYPE = "creator"` - 爬虫类型（search/detail/creator）
- `SAVE_DATA_OPTION = "db"` - 数据保存方式

## 浏览器登录缓存

登录后浏览器数据保存在 `browser_data/dy_user_data_dir/{nickname}/` 目录下。

## 数据库

### media_ai 数据库（外部系统）
- `products` 表：商品信息
- `product_images` 表：商品图片

### douyin 数据库（本地）
- `douyin_aweme` 表：视频详情
- `douyin_aweme_summary` 表：视频统计汇总
- `dy_creator` 表：创作者信息

## 商品信息提取工具

### tools/get_product_from_url/

输入抖音视频链接，自动：
1. 通过 Playwright 浏览器获取视频详情（使用已有登录态）
2. 提取 `anchor_info.extra` 中的商品信息
3. 下载商品图片到本地
4. 插入 `media_ai.products` 表
5. 插入 `media_ai.product_images` 表

### 数据库字段映射

**products 表**:
- `id` = `product_id`
- `user_id` = `d359ec83-a39c-4408-aac6-c1c818d08ab8`
- `team_id` = `18982144-3d42-4a51-98d8-4d6959332d66`
- `name` = `title`
- `targetAudience`: 女装→WOMENS, 男装→MENS, 其他→KIDS
- `promotion_id`, `elastic_title`, `FirstCName`, `SecondCName`, `ThirdCName`, `FourthCName`, `price`, `aweme_id`

**product_images 表**:
- `product_id` = 商品ID
- `url` = 本地路径 `/uploads/teams/18982144-3d42-4a51-98d8-4d6959332d66/products/{product_id}.jpg`
- `is_main` = 1
- `order` = 0

### 图片保存路径
```
D:\Code\media\media_ai\public\uploads\teams\18982144-3d42-4a51-98d8-4d6959332d66\products\{product_id}.jpg
```

## 关键代码参考

### DouYinCrawler 启动流程 (media_platform/douyin/core.py)
```python
async def start(self):
    # 1. 启动浏览器（使用已有登录态或扫码登录）
    # 2. 检查登录状态
    # 3. 根据 CRAWLER_TYPE 执行对应爬取任务
```

### DouYinClient 获取视频详情 (media_platform/douyin/client.py)
```python
async def get_video_by_id(self, aweme_id: str) -> Dict:
    # 调用抖音 API，需要 a_bogus 签名
    # 签名由 libs/douyin.js 生成
```

### 商品信息提取 (store/douyin/__init__.py)
```python
def extract_product_info(aweme_item: Dict) -> Dict:
    anchor_info = aweme_item.get('anchor_info', {})
    extra_str = anchor_info.get('extra', '')
    extra_list = json.loads(extra_str)
    return extra_list[0]  # 商品信息在 extra 字段中
```

## 注意事项

1. 登录态保存在 `browser_data/dy_user_data_dir/{nickname}/`，不同用户分开
2. 抖音 API 需要 `a_bogus` 签名，由 `libs/douyin.js` 生成
3. 爬虫会自动处理登录（扫码登录），但需要有浏览器交互
4. `media_ai` 数据库与本项目是不同数据库，连接信息在 `.env` 中
