# 🔥 MediaCrawler - 自媒体平台爬虫 🕷️

项目克隆自[MediaCrawler 完整文档](https://nanmicoder.github.io/MediaCrawler/)。自己魔改了适配了自己一些需求。

有需求请关注作者 Pro 版本 [MediaCrawlerPro](https://github.com/MediaCrawlerPro)。

# 常用命令

```python
# 启动爬虫
uv run main.py --platform dy --type creator --lt qrcode --get_comment 0 --save_data_option db

# 新增抖音爬虫主页配置
uv run -m command.crawler_cfg --user_id MS4wLjABAAAA8EoZrCw43AWujry2n4wq63yLNqCxelDngM7hwXT6tY0 --update_nickname
uv run -m command.crawler_cfg --user_id MS4wLjABAAAA8EoZrCw43AWujry2n4wq63yLNqCxelDngM7hwXT6tY0 --remove
```
