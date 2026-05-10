# 🔥 MediaCrawler - 自媒体平台爬虫 🕷️

项目克隆自[MediaCrawler 完整文档](https://nanmicoder.github.io/MediaCrawler/)。自己魔改了适配了自己一些需求。

有需求请关注作者 Pro 版本 [MediaCrawlerPro](https://github.com/MediaCrawlerPro)。

当前项目主要用于抓取抖音平台数据，包括如下功能:

1. 待抓取抖音账户的增删改查
2. 抓取抖音账户的用户信息、发布视频的点赞、收藏、转发信息
3. 计算所有用户，所有发布视频的日增点赞、收藏、转发数

# 常用命令

```python
# 1. 新增抖音爬虫主页配置
# --user_id 指定用户主页ID， --update_nickname 添加用户同时，自动更新用户昵称
uv run -m command.crawler_cfg --user_id MS4wLjABAAAA8EoZrCw43AWujry2n4wq63yLNqCxelDngM7hwXT6tY0 --update_nickname

# --remove 删除账户
uv run -m command.crawler_cfg --user_id MS4wLjABAAAA8EoZrCw43AWujry2n4wq63yLNqCxelDngM7hwXT6tY0 --remove

# 更新待爬取账户的昵称
uv run -m command.crawler_cfg --update_nickname

# 2. 启动爬虫，抓取重点关注的抖音账户数据（多账号轮询）
uv run main.py --platform dy --type creator --lt qrcode --get_comment 0 --save_data_option db

# 3. 计算所有用户，所有发布视频的日增点赞、收藏、转发数
uv run -m command.cal_day_incr

# 4. 爬取 + 日增计算（一键完成）
uv run -m command.run_full_crawl
uv run -m command.run_full_crawl -t 2025-01-15 -d 7

# 5. 从抖音分享链接提取用户ID
python -m command.extract_douyin_user_id "https://v.douyin.com/mlIAdeKJFxE/"


python -m command.extract_douyin_user_id "4.69 复制打开抖音，看看【可颂 Kesong的作品】白色修身法式收腰连衣裙显瘦裙子女夏季爆款2026新... https://v.douyin.com/Z_z5g1POreY/ i@C.UL 05/04 OKj:/ :5pm "

# 6. 从视频链接提取商品信息
python -m tools.get_product_from_url.main "https://www.douyin.com/video/7558626596425518371"


python -m tools.get_product_from_url.main "4.69 复制打开抖音，看看【可颂 Kesong的作品】白色修身法式收腰连衣裙显瘦裙子女夏季爆款2026新... https://v.douyin.com/Z_z5g1POreY/ i@C.UL 05/04 OKj:/ :5pm "
```

# 项目结构

```
MediaCrawler/
├── command/           # 命令行入口脚本
│   ├── crawler_cfg.py           # 创作者配置管理
│   ├── cal_day_incr.py          # 日增数据计算
│   ├── run_full_crawl.py       # 爬取+日增计算入口
│   └── extract_douyin_user_id.py # 用户ID提取
├── core/              # 核心模块
│   ├── account_manager.py       # 多账户管理
│   ├── login_manager.py         # 登录管理
│   ├── notifier/                # 通知模块
│   └── task_dispatcher.py       # 任务调度
├── config/            # 配置文件
│   ├── account_config.py        # 账户配置
│   ├── notification_config.py   # 通知配置
│   └── base_config.py          # 基础配置
├── test/              # 测试脚本
│   ├── test_notification.py     # 通知测试
│   └── test_qrcode_login.py     # 登录测试
└── dy_parse/          # 定时任务脚本（用户自定义）
```

# 账户配置

在 `config/account_config.py` 中配置多账户：

```python
ACCOUNTS = [
    {
        "account_id": "account_1",
        "nickname": "橙子Mama",
        "phone": "19156537759",
        "cookies": "",
    },
    {
        "account_id": "account_2",
        "nickname": "漫游者",
        "phone": "13826124760",
        "cookies": "",
    },
]
```

浏览器数据将保存在 `browser_data/dy_user_data_dir/{nickname}/` 目录下。
