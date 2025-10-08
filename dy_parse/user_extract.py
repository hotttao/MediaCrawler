# extract_douyin_links.py

from bs4 import BeautifulSoup
import re

def extract_douyin_user_links(file_path):
    """
    从指定的 HTML 文件中提取所有以 'www.douyin.com/user/' 开头的链接。

    Args:
        file_path (str): HTML 文件的路径。

    Returns:
        list: 包含所有匹配链接的列表。
    """
    try:
        # 读取 HTML 文件
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # 使用 BeautifulSoup 解析 HTML
        soup = BeautifulSoup(content, 'html.parser')
        
        # 查找所有 <a> 标签
        links = soup.find_all('a', href=True)
        
        # 使用正则表达式匹配以 'www.douyin.com/user/' 开头的链接
        # 注意：这里使用了 re.escape 来转义特殊字符，确保 . 匹配字面意义的点
        pattern = re.compile(r'(www\.)?douyin\.com/user/')
        
        douyin_user_links = set()
        for link in links:
            href = link['href']
            # 检查链接是否匹配模式
            if pattern.search(href):
                # 如果链接是相对路径（以 // 开头），补全协议
                if href.startswith('//'):
                    href = 'https:' + href
                douyin_user_links.add(href)
        
        return douyin_user_links

    except FileNotFoundError:
        print(f"错误：找不到文件 '{file_path}'。请确保文件存在于当前目录下。")
        return []
    except Exception as e:
        print(f"读取或解析文件时发生错误：{e}")
        return []

# ------------------- 主程序 -------------------

if __name__ == "__main__":
    # 定义文件路径
    html_file_path = 'a.html'
    
    # 提取链接
    user_links = extract_douyin_user_links(html_file_path)
    s = set(user_links)
    # 输出结果
    if user_links:
        print(f"共找到 {len(user_links)} 个抖音用户链接：")
        for i, link in enumerate(user_links, 1):
            l = link.replace('https://www.douyin.com/user/', '').split('?')[0]
            print(f'"{l}",')
        
        # 可选：将结果保存到文件
        # with open('douyin_user_links.txt', 'w', encoding='utf-8') as f:
        #     for link in user_links:
        #         f.write(link + '\n')
        # print("链接已保存到 'douyin_user_links.txt'")
        
    else:
        print("未找到任何以 'www.douyin.com/user/' 开头的链接。")