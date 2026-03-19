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


# 2. 启动爬虫，抓取重点关注的抖音账户数据
uv run main.py --platform dy --type creator --lt qrcode --get_comment 0 --save_data_option db

# 3. 计算所有用户，所有发布视频的日增点赞、收藏、转发数
uv run -m command.cal_day_incr
```
