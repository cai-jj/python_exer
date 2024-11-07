import re
import requests
from bs4 import BeautifulSoup
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


# 读取域名
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
# 写域名
def write_domains_to_file(domains, filename):
    with open(filename, "w") as file:
        for domain in domains:
            file.write(domain + "\n")
    print(f"Domains written to {filename}")

if __name__ == '__main__':
    read_file = 'domain.txt'
    urls = read_domains_from_file(read_file)
    alldomains = set()
    for url in urls:
        domains = get_domains_from_url(url)
        url = process_url(url)
        alldomains.add(url)
        alldomains.update(domains)
    out_file = 'all_domain.txt'
    write_domains_to_file(alldomains, out_file)

