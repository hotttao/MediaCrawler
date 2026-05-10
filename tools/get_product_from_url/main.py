# -*- coding: utf-8 -*-
"""
抖音视频商品信息提取工具 - 命令行入口
"""
import argparse
import asyncio
import json
import re
import sys
from typing import Optional

from .fetcher import get_product_from_url, extract_aweme_id

# 复用 command.extract_douyin_user_id 的 URL 提取逻辑
def extract_url(text: str) -> str:
    """从文本中提取第一个抖音URL"""
    pattern = r'https://v\.douyin\.com/[^\s]+'
    match = re.search(pattern, text)
    if match:
        return match.group(0)
    return text.strip()

# 复用 command.extract_douyin_user_id 的重定向链获取逻辑
def get_redirect_chain(short_url: str) -> list:
    """获取短链接的重定向链"""
    import requests
    from urllib.parse import urlparse

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    })

    urls = []
    current_url = short_url

    for _ in range(5):
        try:
            response = session.get(current_url, allow_redirects=False, timeout=10)
            location = response.headers.get('Location')
            if location:
                if not location.startswith('http'):
                    parsed = urlparse(current_url)
                    location = f"{parsed.scheme}://{parsed.netloc}{location}"
                urls.append(location)
                current_url = location
            else:
                urls.append(response.url)
                break
        except Exception as e:
            print(f"Error: {e}")
            break

    return urls

def extract_product_url(input_text: str) -> str:
    """从分享文本中提取最终的视频URL"""
    share_url = extract_url(input_text)
    if not share_url.startswith('http'):
        share_url = 'https://' + share_url

    urls = get_redirect_chain(share_url)
    if urls:
        # 取最后一个URL并过滤冗余参数
        final_url = urls[-1]
        final_url = re.sub(r'\?previous_page=.*$', '', final_url)
        return final_url
    return share_url


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

    # 先从输入中提取最终的视频URL（支持分享文本格式）
    input_url = extract_product_url(args.url)
    if input_url != args.url.strip():
        print(f"从分享文本中提取URL: {input_url}", file=sys.stderr)

    # 检查链接格式
    aweme_id = extract_aweme_id(input_url)
    if not aweme_id:
        print_json({"error": f"无法从链接中提取视频 ID: {input_url}"})
        sys.exit(1)

    print(f"已识别视频 ID: {aweme_id}", file=sys.stderr)

    # 运行异步获取
    result = asyncio.run(get_product_from_url(input_url))

    # 输出结果
    pretty = args.format == "json"
    print_json(result, pretty)


if __name__ == "__main__":
    main()
