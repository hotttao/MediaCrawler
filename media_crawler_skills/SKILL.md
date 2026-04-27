---
name: media-crawler
description: |
  抖音自媒体平台爬虫工具，用于抓取抖音视频数据、提取商品信息、计算日增统计。
  Use this skill when the user mentions:
  - 抖音爬虫、视频抓取、数据采集
  - douyin、aweme、video crawler
  - 商品信息提取、商品入库
  - 日增统计、点赞收藏转发计算
  - 抖音创作者、sec_uid、用户主页
  - 任何与 MediaCrawler 项目相关的操作
---

# MediaCrawler 抖音爬虫项目

## 重要：执行前必须先切换到项目根目录

**所有命令执行前必须先切换到项目根目录：**
```bash
cd D:\Code\media\MediaCrawler
```

## 项目概述

MediaCrawler 是一个抖音自媒体平台爬虫工具，主要功能：
1. 待抓取抖音账户的增删改查
2. 抓取抖音账户的用户信息、发布视频的点赞/收藏/转发数据
3. 计算所有用户、所有视频的日增统计数据
4. 从视频链接提取商品信息并入库

## 常用命令

### 1. 新增抖音爬虫主页配置
```bash
# --user_id 指定用户主页ID，--update_nickname 添加用户同时自动更新昵称
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

## 配置文件说明

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

### .env - 环境变量（数据库连接）
```bash
MYSQL_DB_PWD=nUar3Ml90f1xvBSL
MYSQL_DB_USER=root
MYSQL_HOST=192.168.2.38
MYSQL_DB_HOST=192.168.2.38
MYSQL_DB_PORT=3306
MYSQL_DB_NAME=douyin
```

### config/base_config.py - 关键配置项
- `PLATFORM = "dy"` - 平台（仅支持 dy）
- `SAVE_LOGIN_STATE = True` - 保存登录状态
- `USER_DATA_DIR = "%s_user_data_dir"` - 浏览器数据目录模板
- `HEADLESS = False` - 是否无头模式
- `CRAWLER_TYPE = "creator"` - 爬虫类型（search/detail/creator）
- `SAVE_DATA_OPTION = "db"` - 数据保存方式

## 浏览器登录缓存

登录后浏览器数据保存在 `browser_data/dy_user_data_dir/{nickname}/` 目录下。

不同用户分开保存，nickname 取自 account_config.py 中的配置。

## 数据库

### media_ai 数据库（外部系统）
- `products` 表：商品信息
- `product_images` 表：商品图片

### douyin 数据库（本地）
- `douyin_aweme` 表：视频详情
- `douyin_aweme_summary` 表：视频统计汇总
- `dy_creator` 表：创作者信息

## 商品信息提取工具（tools/get_product_from_url/）

输入抖音视频链接，自动完成：
1. 通过 Playwright 浏览器获取视频详情（使用已有登录态）
2. 从 `anchor_info.extra` 中提取商品信息
3. 下载商品图片到本地目录
4. 插入 `media_ai.products` 表
5. 插入 `media_ai.product_images` 表

### 数据库字段映射

**products 表**:
| 字段 | 来源 |
|------|------|
| id | product_id |
| user_id | d359ec83-a39c-4408-aac6-c1c818d08ab8 |
| team_id | 18982144-3d42-4a51-98d8-4d6959332d66 |
| name | title |
| targetAudience | SecondCName=女装→WOMENS, 男装→MENS, 其他→KIDS |
| promotion_id | 原字段 |
| elastic_title | 原字段 |
| FirstCName/SecondCName/ThirdCName/FourthCName | 分类信息 |
| price | 原字段（分） |
| aweme_id | 视频ID |

**product_images 表**:
| 字段 | 值 |
|------|-----|
| product_id | 商品ID |
| url | /uploads/teams/18982144-3d42-4a51-98d8-4d6959332d66/products/{product_id}.jpg |
| is_main | 1 |
| order | 0 |

### 图片本地保存路径
```
D:\Code\media\media_ai\public\uploads\teams\18982144-3d42-4a51-98d8-4d6959332d66\products\{product_id}.jpg
```

## 关键代码参考

### DouYinCrawler 启动流程 (media_platform/douyin/core.py)
核心类负责：
- 启动 Playwright 浏览器
- 处理登录（扫码登录/cookie）
- 根据 CRAWLER_TYPE 执行对应爬取任务

### DouYinClient API 客户端 (media_platform/douyin/client.py)
```python
async def get_video_by_id(self, aweme_id: str) -> Dict:
    # 调用抖音视频详情 API
    # 需要 a_bogus 签名（由 libs/douyin.js 生成）
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

1. **执行任何命令前必须先 cd 到项目根目录**
2. 登录态保存在 `browser_data/dy_user_data_dir/{nickname}/`，不同用户分目录
3. 抖音 API 需要 `a_bogus` 签名，由 `libs/douyin.js` 生成
4. 爬虫会自动处理登录，但需要浏览器交互（扫码）
5. `media_ai` 是外部数据库，与本项目 `douyin` 数据库不同
6. 商品图片先下载到本地，再插入数据库（url 字段存本地路径）
