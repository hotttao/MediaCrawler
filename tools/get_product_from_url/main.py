# -*- coding: utf-8 -*-
"""
抖音视频商品信息提取工具 - 命令行入口
"""
import argparse
import asyncio
import json
import sys
from typing import Optional

from .fetcher import get_product_from_url, extract_aweme_id


def print_json(data: dict, pretty: bool = True):
    """打印 JSON 结果"""
    if pretty:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(data, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(
        description="抖音视频链接商品信息提取工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python -m tools.get_product_from_url.main "https://www.douyin.com/video/7558626596425518371"
  python -m tools.get_product_from_url.main "https://v.douyin.com/xxxxx"
        """
    )
    parser.add_argument("url", nargs="?", help="抖音视频链接")
    parser.add_argument("--format", "-f", choices=["json", "compact"], default="json",
                        help="输出格式（默认: json）")

    args = parser.parse_args()

    if not args.url:
        parser.print_help()
        sys.exit(1)

    # 先检查链接格式
    aweme_id = extract_aweme_id(args.url)
    if not aweme_id:
        print_json({"error": f"无法从链接中提取视频 ID: {args.url}"})
        sys.exit(1)

    print(f"已识别视频 ID: {aweme_id}", file=sys.stderr)

    # 运行异步获取
    result = asyncio.run(get_product_from_url(args.url))

    # 输出结果
    pretty = args.format == "json"
    print_json(result, pretty)


if __name__ == "__main__":
    main()
