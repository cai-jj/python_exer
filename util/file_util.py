import json

class FileUtil:
    @staticmethod
    def write_to_file(kv_pairs, output_file):
        """将键值对以 JSON 格式写入文件"""
        try:
            with open(output_file, 'w', encoding='utf-8') as file:
                json.dump(kv_pairs, file, ensure_ascii=False, indent=4)
        except IOError as e:
            print(f"Error writing to file: {e}")

    @staticmethod
    def read_from_file(input_file):
        """从文件中读取 JSON 格式的键值对"""
        try:
            with open(input_file, 'r', encoding='utf-8') as file:
                kv_pairs = json.load(file)
            return kv_pairs
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error reading from file: {e}")
            return {}

    @staticmethod
    def read_list_from_file(file_path):
        """从文件中读取 URL 列表，每行一个 URL"""
        with open(file_path, 'r', encoding='utf-8') as file:
            domains = [line.strip() for line in file if line.strip()]
        return domains

    @staticmethod
    def write_list_to_file(domains, file_path):
        """将 URL 列表写入文件，每行一个 URL"""
        with open(file_path, 'w', encoding='utf-8') as file:
            for domain in domains:
                file.write(f"{domain}\n")