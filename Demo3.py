import json
# 将结果写入文件
def write_domain_ip_map_to_file(domain_ip_map, filename="domain_ip_map.json"):
    with open(filename, "w") as file:
        json.dump(domain_ip_map, file, indent=4)
    print(f"Domain-IP map written to {filename}")


# 从文件中读取
def read_domain_ip_map_from_file(filename="domain_ip_map.json"):
    with open(filename, "r") as file:
        domain_ip_map_str_keys = json.load(file)
    # 将键（字符串）转换回列表
    domain_ip_map = {json.loads(key): value for key, value in domain_ip_map_str_keys.items()}
    print(f"Domain-IP map read from {filename}")
    return domain_ip_map

if __name__ == '__main__':
    # 示例数据
    domains = [
        ['www.163.com', 'www.baidu.com'],
        ['www.google.com', 'www.github.com']
    ]

    ips = [
        ['1.1.1.1', '2.2.2.2'],
        ['3.3.3.3', '4.4.4.4']
    ]

    # 初始化 domain_ip_map
    domain_ip_map = {json.dumps(key): value for key, value in zip(domains, ips)}

    # 打印初始化后的字典
    print(domain_ip_map)