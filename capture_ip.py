import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import subprocess
import json
from util.file_util import FileUtil

def start_tshark(output_file):

    # 构建捕获过滤器
    capture_filter = 'port 80 or port 443'
    # 启动 tshark，指定输出文件和捕获过滤器
    # en0网卡配置一下
    tshark_process = subprocess.Popen(
        ['tshark', '-i', 'en0', '-f', capture_filter, '-w', output_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return tshark_process


def stop_tshark(tshark_process):
    tshark_process.terminate()
    out, err = tshark_process.communicate()
    if err:
        print(f'Tshark error: {err.decode()}')
    else:
        print(f'Tshark stopped and data saved to {output_file}')

def extract_ips_from_pcap(pcap_file):
    result = subprocess.run(['tshark', '-r', pcap_file, '-T', 'fields', '-e', 'ip.src', '-e', 'ip.dst'],
                            capture_output=True, text=True)
    # 将每行的IP地址对转换为元组，并去除空值
    ip_pairs = [tuple(line.split()) for line in result.stdout.splitlines() if line.strip()]

    # 将所有IP地址放入一个集合中，自动去重
    all_ips = set()
    for src_ip, dst_ip in ip_pairs:
        all_ips.add(src_ip)
        all_ips.add(dst_ip)

    # 将集合转换为列表
    unique_ips = list(all_ips)

    return unique_ips

def visit_website(url, output_file):
    # 设置 Chrome 选项
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 无头模式，不打开浏览器窗口
    chrome_options.add_argument('--disable-gpu')

    # 指定 ChromeDriver 的路径
    service = Service('/usr/local/bin/chromedriver')  # 替换为你的 chromedriver 路径

    # 创建 WebDriver 对象
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # 启动 tshark
        tshark_process = start_tshark(output_file)
        # 打开网页
        driver.get(url)
        print(f'Visited {url}')

        # 停留 5 秒
        time.sleep(5)

        # 停止 tshark
        stop_tshark(tshark_process)
    except Exception as e:
        print(f'Error visiting {url}: {e}')
    finally:
        # 关闭浏览器
        driver.quit()

def read_domains_from_file(file_path):
    with open(file_path, 'r') as file:
        domains = [line.strip() for line in file if line.strip()]
    return domains




if __name__ == '__main__':
    # 访问域名并使用Wireshark抓取对应的IP地址
    urls = read_domains_from_file('domain.txt')
    capture_ip_map = {}
    for i, url in enumerate(urls):
        output_file = f'output_{i}.pcap'
        # visit_website(url, output_file)
        ips = extract_ips_from_pcap(output_file)
        capture_ip_map[url] = ips
    output_file = 'capture_ip_map.json'
    FileUtil.write_to_file(capture_ip_map, output_file)
    read_kv_pairs = FileUtil.read_from_file(output_file)
    print(read_kv_pairs)


