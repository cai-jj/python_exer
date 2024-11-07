import socket
import time
import subprocess
import platform


def clear_dns_cache(password):
    system = platform.system()
    if system == 'Windows':
        try:
            subprocess.run(['ipconfig', '/flushdns'], check=True)
            print("DNS cache cleared successfully on Windows.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to clear DNS cache on Windows: {e}")
    elif system == 'Darwin':  # macOS
        try:
            subprocess.run(['echo', password, '|', 'sudo', '-S', 'dscacheutil', '-flushcache'], shell=True, check=True)
            subprocess.run(['echo', password, '|', 'sudo', '-S', 'killall', '-HUP', 'mDNSResponder'], shell=True, check=True)
            print("DNS cache cleared successfully on macOS.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to clear DNS cache on macOS: {e}")
    elif system == 'Linux':
        try:
            subprocess.run(['echo', password, '|', 'sudo', '-S', 'systemd-resolve', '--flush-caches'], shell=True, check=True)
            print("DNS cache cleared successfully on Linux.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to clear DNS cache on Linux: {e}")
    else:
        print(f"Unsupported system: {system}")


def get_all_ips_from_domain(domain, attempts=50, interval=5):
    all_ips = set()
    for attempt in range(attempts):
        try:
            # 清除DNS缓存
            password = "Ck13687035404."
            clear_dns_cache(password)
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






if __name__ == '__main__':
    # 测试网易的域名
    domain = "www.163.com"
    iplist = get_all_ips_from_domain(domain)
    print(f"The IP addresses for {domain} are: {iplist}")







