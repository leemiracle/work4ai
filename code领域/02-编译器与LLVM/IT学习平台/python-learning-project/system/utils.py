import os
import shutil
import hashlib
import json
from typing import List, Dict, Optional
from datetime import datetime
import subprocess


class FileManager:
    
    @staticmethod
    def create_directory(path: str):
        if not os.path.exists(path):
            os.makedirs(path)
            return f"目录已创建: {path}"
        return f"目录已存在: {path}"
    
    @staticmethod
    def list_files(directory: str, pattern: Optional[str] = None) -> List[str]:
        files = []
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isfile(item_path):
                if pattern is None or pattern in item:
                    files.append(item)
        return files
    
    @staticmethod
    def get_file_info(filepath: str) -> Dict:
        stat = os.stat(filepath)
        return {
            'path': filepath,
            'size': stat.st_size,
            'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'is_file': os.path.isfile(filepath),
            'is_dir': os.path.isdir(filepath)
        }
    
    @staticmethod
    def calculate_hash(filepath: str, algorithm: str = 'md5') -> str:
        hash_func = hashlib.new(algorithm)
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_func.update(chunk)
        return hash_func.hexdigest()


class JSONHandler:
    
    @staticmethod
    def read_json(filepath: str) -> Dict:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def write_json(filepath: str, data: Dict):
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    @staticmethod
    def merge_json(*filepaths: str) -> Dict:
        merged = {}
        for filepath in filepaths:
            if os.path.exists(filepath):
                data = JSONHandler.read_json(filepath)
                merged.update(data)
        return merged


class SystemMonitor:
    
    @staticmethod
    def get_disk_usage(path: str = '.') -> Dict:
        usage = shutil.disk_usage(path)
        total_gb = usage.total / (1024 ** 3)
        used_gb = usage.used / (1024 ** 3)
        free_gb = usage.free / (1024 ** 3)
        
        return {
            'total_gb': round(total_gb, 2),
            'used_gb': round(used_gb, 2),
            'free_gb': round(free_gb, 2),
            'usage_percent': round((used_gb / total_gb) * 100, 2)
        }
    
    @staticmethod
    def execute_command(command: List[str]) -> Dict:
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=30)
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode
            }
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': '命令执行超时'}
        except Exception as e:
            return {'success': False, 'error': str(e)}


class Logger:
    
    def __init__(self, log_file: str):
        self.log_file = log_file
    
    def log(self, message: str, level: str = 'INFO'):
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    
    def info(self, message: str):
        self.log(message, 'INFO')
    
    def warning(self, message: str):
        self.log(message, 'WARNING')
    
    def error(self, message: str):
        self.log(message, 'ERROR')
    
    def get_logs(self, level: Optional[str] = None) -> List[str]:
        if not os.path.exists(self.log_file):
            return []
        
        with open(self.log_file, 'r', encoding='utf-8') as f:
            logs = f.readlines()
        
        if level:
            return [log for log in logs if f"[{level}]" in log]
        return logs