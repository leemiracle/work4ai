import pytest
from system.utils import FileManager, JSONHandler, Logger
import os
import tempfile


class TestFileManager:
    
    def test_create_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = os.path.join(tmpdir, 'test_dir')
            result = FileManager.create_directory(test_dir)
            assert "已创建" in result or "已存在" in result
    
    def test_get_file_info(self):
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write('test content')
            test_file = f.name
        
        try:
            info = FileManager.get_file_info(test_file)
            assert info['is_file'] == True
            assert 'size' in info
            assert 'created' in info
        finally:
            os.unlink(test_file)
    
    def test_calculate_hash(self):
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write('test content')
            test_file = f.name
        
        try:
            hash1 = FileManager.calculate_hash(test_file)
            hash2 = FileManager.calculate_hash(test_file)
            assert hash1 == hash2
            assert len(hash1) == 32  # MD5 hash length
        finally:
            os.unlink(test_file)


class TestJSONHandler:
    
    def test_write_and_read_json(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            test_file = f.name
        
        try:
            data = {'key1': 'value1', 'key2': 123, 'key3': [1, 2, 3]}
            JSONHandler.write_json(test_file, data)
            result = JSONHandler.read_json(test_file)
            assert result == data
        finally:
            os.unlink(test_file)
    
    def test_merge_json(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f1:
            file1 = f1.name
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f2:
            file2 = f2.name
        
        try:
            JSONHandler.write_json(file1, {'a': 1, 'b': 2})
            JSONHandler.write_json(file2, {'b': 3, 'c': 4})
            result = JSONHandler.merge_json(file1, file2)
            assert result == {'a': 1, 'b': 3, 'c': 4}
        finally:
            os.unlink(file1)
            os.unlink(file2)


class TestLogger:
    
    def test_log(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            test_log = f.name
        
        try:
            logger = Logger(test_log)
            logger.info('Test info message')
            logger.warning('Test warning message')
            logger.error('Test error message')
            
            logs = logger.get_logs()
            assert len(logs) == 3
            assert 'INFO' in logs[0]
            assert 'WARNING' in logs[1]
            assert 'ERROR' in logs[2]
        finally:
            os.unlink(test_log)
    
    def test_filter_logs_by_level(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            test_log = f.name
        
        try:
            logger = Logger(test_log)
            logger.info('Test info')
            logger.warning('Test warning')
            logger.error('Test error')
            
            error_logs = logger.get_logs('ERROR')
            assert len(error_logs) == 1
            assert 'ERROR' in error_logs[0]
        finally:
            os.unlink(test_log)