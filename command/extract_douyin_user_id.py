"""
从抖音分享链接提取用户ID

用法:
    python extract_douyin_user_id.py <分享链接>
    
示例:
    python extract_douyin_user_id.py "https://v.douyin.com/mlIAdeKJFxE/"
"""

import requests
import re
import json
import sys
from urllib.parse import urlparse, parse_qs

def extract_url(text: str) -> str:
    """从文本中提取第一个抖音URL"""
    # 匹配 v.douyin.com 开头的URL
    pattern = r'https://v\.douyin\.com/[^\s]+'
    match = re.search(pattern, text)
    if match:
        return match.group(0)
    return text.strip()

def get_redirect_chain(short_url: str) -> list:
    """获取短链接的重定向链"""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
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

def extract_user_ids(urls: list) -> dict:
    """从重定向URL中提取用户ID和商品ID"""
    results = {}

    for url in urls:
        parsed = urlparse(url)
        params = parse_qs(parsed.query)

        # 1. 直接参数
        for key in ['uid', 'user_id', 'author_id', 'sec_uid', 'secuid']:
            if key in params and key not in results:
                results[key] = params[key][0]

        # 2. 商品ID参数
        for key in ['product_id', 'item_id', 'goods_id']:
            if key in params and 'product_id' not in results:
                results['product_id'] = params[key][0]

        # 3. 解析JSON参数
        for key in ['ecom_share_track_params', 'activity_info', 'share_track_info']:
            if key in params:
                try:
                    json_data = json.loads(params[key][0])

                    for k in ['secuid', 'sec_author_id', 'social_author_id', 'social_share_user_id']:
                        if k in json_data and k not in results:
                            results[k] = json_data[k]

                    # 商品ID从JSON中提取
                    for k in ['product_id', 'item_id', 'goods_id']:
                        if k in json_data and 'product_id' not in results:
                            results['product_id'] = json_data[k]
                except json.JSONDecodeError:
                    pass

        # 4. URL路径
        path_match = re.search(r'douyin\.com/user/([^/?\s]+)', url)
        if path_match and 'user_page' not in results:
            results['user_page'] = path_match.group(1)

        # 5. 从商品详情路径提取product_id
        product_match = re.search(r'douyin\.com/jupiter/detail/(\d+)', url)
        if product_match and 'product_id' not in results:
            results['product_id'] = product_match.group(1)

        # 6. 记录最终URL（重定向链最后一个）
        results['final_url'] = url

    return results

def main():
    # 获取分享链接
    if len(sys.argv) > 1:
        input_text = sys.argv[1].strip()
    else:
        input_text = input("请输入抖音分享链接或包含链接的文本: ").strip()

    if not input_text:
        print("错误: 请提供分享链接")
        sys.exit(1)

    # 从文本中提取URL
    share_url = extract_url(input_text)

    # 补全URL
    if not share_url.startswith('http'):
        share_url = 'https://' + share_url

    print(f"抖音分享链接: {share_url}\n")
    
    # 获取重定向链
    urls = get_redirect_chain(share_url)
    
    # 提取用户ID
    user_ids = extract_user_ids(urls)
    
    # 主要用户ID：优先使用 sec_author_id（原创作者），而非 secuid（转发者）
    main_id = user_ids.get('sec_author_id') or user_ids.get('secuid')
    
    print("=" * 50)
    print("提取结果:")
    print("=" * 50)
    print(f"用户ID (sec_author_id): {user_ids.get('sec_author_id', 'N/A')}")
    print(f"用户ID (secuid): {user_ids.get('secuid', 'N/A')}")
    print(f"商品URL (product_url): {user_ids.get('final_url', 'N/A')}")
    print(f"social_author_id: {user_ids.get('social_author_id', 'N/A')}")
    print(f"user_page: {user_ids.get('user_page', 'N/A')}")
    
    if main_id:
        print(f"\n✅ 最终用户ID: {main_id}")
    else:
        print("\n❌ 无法提取用户ID")
        sys.exit(1)
    
    return main_id

if __name__ == "__main__":
    main()
