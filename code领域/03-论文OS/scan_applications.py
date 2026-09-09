"""
Paper-OS 应用代码深度挖掘工具
扫描并索引所有应用项目的代码资源
"""
import os
import ast
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import hashlib


class CodeScanner:
    """代码扫描器 - 扫描Python文件并提取信息"""
    
    def __init__(self):
        self.stats = {
            'total_files': 0,
            'python_files': 0,
            'total_lines': 0,
            'total_functions': 0,
            'total_classes': 0,
            'total_modules': 0
        }
    
    def scan_directory(self, directory: str, exclude_dirs: List[str] = None) -> Dict[str, Any]:
        """扫描目录下的所有Python文件"""
        if exclude_dirs is None:
            exclude_dirs = ['__pycache__', '.git', 'venv', 'env', 'build', 'dist']
        
        root = Path(directory)
        results = {
            'directory': str(root),
            'files': [],
            'modules': [],
            'classes': [],
            'functions': [],
            'imports': []
        }
        
        for file_path in root.rglob('*.py'):
            # 跳过排除的目录
            if any(excl in str(file_path) for excl in exclude_dirs):
                continue
            
            file_info = self.scan_file(file_path)
            if file_info:
                results['files'].append(file_info)
                results['modules'].extend(file_info.get('modules', []))
                results['classes'].extend(file_info.get('classes', []))
                results['functions'].extend(file_info.get('functions', []))
                results['imports'].extend(file_info.get('imports', []))
                
                self.stats['total_files'] += 1
                self.stats['python_files'] += 1
                self.stats['total_lines'] += file_info.get('line_count', 0)
                self.stats['total_classes'] += len(file_info.get('classes', []))
                self.stats['total_functions'] += len(file_info.get('functions', []))
        
        return results
    
    def scan_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """扫描单个Python文件"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            file_info = {
                'path': str(file_path),
                'relative_path': str(file_path.relative_to(file_path.parent.parent.parent) if file_path.parent.parent.parent else file_path),
                'name': file_path.name,
                'line_count': len(content.splitlines()),
                'size': file_path.stat().st_size,
                'modules': [],
                'classes': [],
                'functions': [],
                'imports': [],
                'docstring': ast.get_docstring(tree)
            }
            
            # 提取导入
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        file_info['imports'].append({
                            'type': 'import',
                            'name': alias.name,
                            'asname': alias.asname,
                            'line': node.lineno
                        })
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    for alias in node.names:
                        file_info['imports'].append({
                            'type': 'from',
                            'module': module,
                            'name': alias.name,
                            'asname': alias.asname,
                            'line': node.lineno
                        })
            
            # 提取顶级类和函数
            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    class_info = self._extract_class(node, file_path)
                    file_info['classes'].append(class_info)
                elif isinstance(node, ast.FunctionDef):
                    func_info = self._extract_function(node, file_path, is_method=False)
                    file_info['functions'].append(func_info)
            
            return file_info
            
        except Exception as e:
            print(f"  ⚠️  跳过 {file_path}: {e}")
            return None
    
    def _extract_class(self, node: ast.ClassDef, file_path: Path) -> Dict[str, Any]:
        """提取类信息"""
        class_info = {
            'name': node.name,
            'type': 'class',
            'file': str(file_path),
            'line': node.lineno,
            'docstring': ast.get_docstring(node),
            'bases': [self._get_name(base) for base in node.bases],
            'methods': [],
            'attributes': []
        }
        
        # 提取方法和属性
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_info = self._extract_function(item, file_path, is_method=True)
                class_info['methods'].append(method_info)
            elif isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        class_info['attributes'].append({
                            'name': target.id,
                            'line': item.lineno
                        })
        
        return class_info
    
    def _extract_function(self, node: ast.FunctionDef, file_path: Path, is_method: bool = False) -> Dict[str, Any]:
        """提取函数/方法信息"""
        func_info = {
            'name': node.name,
            'type': 'method' if is_method else 'function',
            'file': str(file_path),
            'line': node.lineno,
            'docstring': ast.get_docstring(node),
            'args': [arg.arg for arg in node.args.args],
            'returns': self._get_name(node.returns) if node.returns else None,
            'decorators': [self._get_name(dec) for dec in node.decorator_list],
            'is_async': isinstance(node, ast.AsyncFunctionDef)
        }
        
        # 提取函数体信息
        func_info['has_return'] = any(isinstance(stmt, ast.Return) for stmt in ast.walk(node))
        func_info['has_yield'] = any(isinstance(stmt, (ast.Yield, ast.YieldFrom)) for stmt in ast.walk(node))
        
        return func_info
    
    def _get_name(self, node: ast.AST) -> str:
        """获取AST节点的名称"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Constant):
            return str(node.value)
        else:
            return ""


class ProjectAnalyzer:
    """项目分析器 - 分析应用项目"""
    
    def __init__(self, output_dir: str = "code_index"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.scanner = CodeScanner()
    
    def analyze_project(self, project_path: str, project_name: str) -> Dict[str, Any]:
        """分析单个项目"""
        print(f"\n🔍 分析项目: {project_name}")
        print(f"   路径: {project_path}")
        
        if not os.path.exists(project_path):
            print(f"   ⚠️  项目不存在")
            return None
        
        scan_result = self.scanner.scan_directory(project_path)
        
        # 添加项目元数据
        scan_result['project_name'] = project_name
        scan_result['project_path'] = project_path
        scan_result['scan_time'] = datetime.now().isoformat()
        
        # 生成统计信息
        scan_result['statistics'] = {
            'total_files': len(scan_result['files']),
            'python_files': len(scan_result['files']),
            'total_lines': sum(f.get('line_count', 0) for f in scan_result['files']),
            'total_functions': len(scan_result['functions']),
            'total_classes': len(scan_result['classes']),
            'total_imports': len(scan_result['imports'])
        }
        
        print(f"   ✅ 完成:")
        print(f"      文件: {scan_result['statistics']['total_files']}")
        print(f"      类: {scan_result['statistics']['total_classes']}")
        print(f"      函数: {scan_result['statistics']['total_functions']}")
        print(f"      行数: {scan_result['statistics']['total_lines']:,}")
        
        return scan_result
    
    def analyze_all_projects(self, projects: List[Dict[str, str]]):
        """分析所有项目"""
        print("╔══════════════════════════════════════════════════════════╗")
        print("║     Paper-OS 应用代码深度挖掘                               ║")
        print("╚══════════════════════════════════════════════════════════╝")
        
        all_results = []
        
        for project in projects:
            result = self.analyze_project(
                project['path'],
                project['name']
            )
            if result:
                all_results.append(result)
        
        # 生成汇总报告
        self._generate_summary_report(all_results)
        
        # 保存每个项目的详细分析
        for result in all_results:
            output_file = self.output_dir / f"{result['project_name']}_analysis.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
        
        print("\n" + "=" * 60)
        print(f"✅ 分析完成! 共 {len(all_results)} 个项目")
        print(f"📁 输出目录: {self.output_dir.absolute()}")
        print("=" * 60)
        
        return all_results
    
    def _generate_summary_report(self, results: List[Dict[str, Any]]):
        """生成汇总报告"""
        total_files = sum(r['statistics']['total_files'] for r in results)
        total_lines = sum(r['statistics']['total_lines'] for r in results)
        total_functions = sum(r['statistics']['total_functions'] for r in results)
        total_classes = sum(r['statistics']['total_classes'] for r in results)
        
        report = f"""# 应用代码深度挖掘报告

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 总体统计

- 分析项目数: {len(results)}
- Python文件数: {total_files}
- 代码总行数: {total_lines:,}
- 函数总数: {total_functions}
- 类总数: {total_classes}

## 项目列表

"""
        
        for result in results:
            stats = result['statistics']
            report += f"""
### {result['project_name']}

- 路径: `{result['project_path']}`
- 文件数: {stats['total_files']}
- 代码行数: {stats['total_lines']:,}
- 函数数: {stats['total_functions']}
- 类数: {stats['total_classes']}

"""
        
        output_file = self.output_dir / "summary_report.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ 汇总报告已生成: {output_file}")


def main():
    """主函数"""
    # 定义要分析的项目列表
    projects = [
        {'name': 'transformers', 'path': 'transformers/src/transformers'},
        {'name': 'vllm', 'path': 'vllm/vllm'},
        {'name': 'sglang', 'path': 'sglang/sglang'},
        {'name': 'text-generation-inference', 'path': 'text-generation-inference/server'},
        {'name': 'mmdetection', 'path': 'mmdetection/mmdet'},
        {'name': 'mmsegmentation', 'path': 'mmsegmentation/mmseg'},
        {'name': 'petals', 'path': 'petals/src/petals'},
        {'name': 'RWKV-LM', 'path': 'RWKV-LM/RWKV'},
        {'name': 'nano-vllm', 'path': 'nano-vllm/nano_vllm'},
    ]
    
    # 创建分析器并运行
    analyzer = ProjectAnalyzer()
    results = analyzer.analyze_all_projects(projects)
    
    # 打印总体统计
    print(f"\n{'='*60}")
    print("📊 总体统计")
    print(f"{'='*60}")
    print(f"  总文件数: {analyzer.scanner.stats['total_files']}")
    print(f"  Python文件: {analyzer.scanner.stats['python_files']}")
    print(f"  总行数: {analyzer.scanner.stats['total_lines']:,}")
    print(f"  总函数: {analyzer.scanner.stats['total_functions']}")
    print(f"  总类: {analyzer.scanner.stats['total_classes']}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
