# -*- coding: utf-8 -*-
"""
核心提取逻辑
"""
import json
import re
from typing import Dict, Optional


def extract_aweme_id(url: str) -> Optional[str]:
    """
    从抖音视频链接中提取 aweme_id

    支持的格式：
    - https://www.douyin.com/video/7558626596425518371
    - https://v.douyin.com/xxxxx
    - 纯数字 ID

    Args:
        url: 抖音视频链接

    Returns:
        aweme_id 或 None
    """
    # 直接是数字
    if url.isdigit():
        return url

    # www.douyin.com/video/xxx 格式
    match = re.search(r'douyin\.com/video/(\d+)', url)
    if match:
        return match.group(1)

    # v.douyin.com/xxx 短链接格式
    match = re.search(r'v\.douyin\.com/(\w+)', url)
    if match:
        return match.group(1)

    return None


def extract_product_info(aweme_item: Dict) -> Dict:
    """
    从抖音视频详情中提取商品信息

    Args:
        aweme_item: 抖音视频详情数据（aweme_detail）

    Returns:
        Dict: 商品信息字典
    """
    product = {}
    anchor_info = aweme_item.get('anchor_info', {})
    extra_str = anchor_info.get('extra', '')

    if extra_str:
        try:
            extra_list = json.loads(extra_str)
            if extra_list and isinstance(extra_list, list):
                p = extra_list[0]
                # 提取指定字段
                product['promotion_id'] = p.get('promotion_id', '')
                product['product_id'] = p.get('product_id', '')
                product['title'] = p.get('title', '')
                product['elastic_title'] = p.get('elastic_title', '')
                # 提取 elastic_images 中的 uri
                elastic_images = p.get('elastic_images', [])
                if elastic_images and isinstance(elastic_images, list):
                    product['elastic_images_uri'] = elastic_images[0].get('uri', '')
                else:
                    product['elastic_images_uri'] = ''
                # 提取分类信息
                category = p.get('category', {})
                product['FirstCName'] = category.get('FirstCName', '')
                product['SecondCName'] = category.get('SecondCName', '')
                product['ThirdCName'] = category.get('ThirdCName', '')
                product['FourthCName'] = category.get('FourthCName', '')
                # 价格
                product['price'] = p.get('price', 0)
        except json.JSONDecodeError:
            pass

    return product


def format_product_json(product: Dict, pretty: bool = True) -> str:
    """
    格式化商品信息为 JSON 字符串

    Args:
        product: 商品信息字典
        pretty: 是否格式化输出

    Returns:
        JSON 字符串
    """
    if pretty:
        return json.dumps(product, ensure_ascii=False, indent=2)
    return json.dumps(product, ensure_ascii=False)