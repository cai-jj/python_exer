import json
import re
import time
import requests
from bs4 import BeautifulSoup
import socket
import urllib.parse
# 获取网页托管的域名
def get_domains_from_url(url, headers = None) :
    if headers is None:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
    try:
        # 步骤 1: 获取网页内容
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 检查请求是否成功
        html_content = response.text

        # 步骤 2: 解析HTML内容
        soup = BeautifulSoup(html_content, 'html.parser')

        # 步骤 3: 提取所有链接
        links = []
        for link in soup.find_all('a', href=True):
            links.append(link['href'])

        # 步骤 4: 提取域名
        domains = set()
        for link in links:
            try:
                parsed_url = urllib.parse.urlparse(link)
                domain = parsed_url.netloc
                if domain:
                    domains.add(domain)
            except Exception as e:
                print(f"Error parsing URL {link}: {e}")

        return domains
    except requests.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return set()

def read_domains_from_file(file_path):
    with open(file_path, 'r') as file:
        domains = [line.strip() for line in file if line.strip()]
    return domains
def process_url(url):
    """处理单个URL，去除https://前缀和域名后面的斜杠及之后的部分"""
    # 使用正则表达式匹配域名
    match = re.match(r'https?://([^/]+)', url)
    if match:
        return match.group(1)
    return url

def write_domain_ip_map_to_file(domain_ip_map, filename="domain_map.json"):
    with open(filename, "w") as file:
        json.dump(domain_ip_map, file, indent=4)
    print(f"Domain-IP map written to {filename}")

if __name__ == '__main__':
    domains = read_domains_from_file('domain.txt')
    domain_map = {}
    for domain in domains:
        domains = get_domains_from_url(domain)
        if domain in domains:
            domains.remove(domain)
        domain_list = list(domains)
        url = process_url(domain)
        domain_map[url] = domain_list
    write_domain_ip_map_to_file(domain_map)
