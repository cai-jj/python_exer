import re
import time
import requests
from bs4 import BeautifulSoup
import socket
import urllib.parse

# 获取域名对应的IP地址
def get_all_ips_from_domain(domain, attempts=5, interval=2):
    all_ips = set()
    for attempt in range(attempts):
        try:
            # 使用socket.getaddrinfo进行DNS查询
            results = socket.getaddrinfo(domain, None)
            ips = {result[-1][0] for result in results}
            all_ips.update(ips)
            print(f"Attempt {attempt + 1}: Found {len(ips)} IPs")
        except socket.gaierror as e:
            print(f"DNS resolution error for {domain}: {e}")
        except Exception as e:
            print(f"Error querying DNS for {domain}: {e}")
        time.sleep(interval)
    return list(all_ips)
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

def write_to_file(kv_pairs, output_file):
    """将键值对写入文件，其中值为列表形式"""
    with open(output_file, 'w', encoding='utf-8') as file:
        for key, value in kv_pairs.items():
            # 将列表转换为字符串，使用逗号分隔
            value_str = ','.join(value)
            file.write(f"{key}:{value_str}\n")

def process_url(url):
    """处理单个URL，去除https://前缀和域名后面的斜杠及之后的部分"""
    # 使用正则表达式匹配域名
    match = re.match(r'https?://([^/]+)', url)
    if match:
        return match.group(1)
    return url

if __name__ == '__main__':
    urls = read_domains_from_file('domain.txt')
    output_file = 'output.txt'
    url_domain_map = {}
    for url in urls:
        domains = get_domains_from_url(url)
        url = process_url(url)
        url_domain_map[url] = domains
    write_to_file(url_domain_map, output_file)
    alldomains = set()
    for url in urls:
        domains = get_domains_from_url(url)
        url = process_url(url)
        alldomains.add(url)
        alldomains.update(domains)
    domain_ip_map_out_file = 'domain_ip_map.txt'
    domain_ip_map = {}
    for domain in alldomains:
        iplist = get_all_ips_from_domain(domain, 1, 0)
        domain_ip_map[domain] = iplist
    write_to_file(domain_ip_map, domain_ip_map_out_file)
    # for url in urls:
    #     domains = get_domains_from_url(url)
    #     domain_info = {}
    #     for domain in domains:
    #         ip_address = get_all_ips_from_domain(domain, 1, 0)
    #         domain_info[domain] = ip_address
    #     # 输出结果
    #     print(f"主域名:{url} ===========")
    #     print("Domains and their IP addresses:")
    #     for domain, ip in domain_info.items():
    #         print(f"{domain}: {ip}")
