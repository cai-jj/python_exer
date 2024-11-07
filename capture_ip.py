from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import subprocess


def visit_website(url):
    # 设置Chrome选项
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 无头模式，不打开浏览器窗口
    chrome_options.add_argument('--disable-gpu')

    # 指定ChromeDriver的路径
    service = Service('/path/to/chromedriver')  # 替换为你的ChromeDriver路径

    # 创建WebDriver对象
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # 打开网页
        driver.get(url)
        print(f'Visited {url}')

        # 停留5秒
        time.sleep(5)
    except Exception as e:
        print(f'Error visiting {url}: {e}')
    finally:
        # 关闭浏览器
        driver.quit()
def start_tshark():
    # 这里假设我们只对HTTP流量感兴趣
    tshark_process = subprocess.Popen(['tshark', '-i', 'eth0', '-Y', 'http', '-w', 'output.pcap'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return tshark_process

def stop_tshark(tshark_process):
    tshark_process.terminate()
    out, err = tshark_process.communicate()
    if err:
        print(f'Tshark error: {err.decode()}')
    else:
        print('Tshark stopped and data saved to output.pcap')
def extract_ips_from_pcap(pcap_file):
    result = subprocess.run(['tshark', '-r', pcap_file, '-T', 'fields', '-e', 'ip.src', '-e', 'ip.dst'], capture_output=True, text=True)
    ips = set(line.split() for line in result.stdout.splitlines())
    return ips

# 提取IP地址
ips = extract_ips_from_pcap('output.pcap')
for ip in ips:
    print(ip)
if __name__ == '__main__':
    # 在访问网站前启动tshark
    tshark_process = start_tshark()
    # 访问网站
    url = "https://www.163.com"
    visit_website(url)
    # 访问后停止tshark
    stop_tshark(tshark_process)