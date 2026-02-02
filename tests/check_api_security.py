"""API Key 安全检查工具 - 确保没有硬编码的 API Key"""
import os
import re
from pathlib import Path
from datetime import datetime


class APIKeySecurityChecker:
    """API Key 安全检查器"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.issues = []
        
        # API Key 模式（NVIDIA 和 OpenAI）
        self.patterns = [
            (r'nvapi-[A-Za-z0-9_-]{20,}', 'NVIDIA API Key'),
            (r'sk-[A-Za-z0-9]{20,}', 'OpenAI API Key'),
            (r'NVIDIA_API_KEY\s*=\s*["\']nvapi-[^"\']+["\']', 'NVIDIA API Key 硬编码'),
            (r'OPENAI_API_KEY\s*=\s*["\']sk-[^"\']+["\']', 'OpenAI API Key 硬编码'),
        ]
        
        # 排除的文件和目录
        self.exclude_dirs = {
            '__pycache__', 
            '.git', 
            '.vscode', 
            'node_modules',
            '.pytest_cache',
            'htmlcov'
        }
        
        self.exclude_files = {
            '.env',  # .env 文件应该包含 API Key
            '.env.example',  # 示例文件可以有占位符
            '.gitignore'
        }
        
    def check_file(self, file_path: Path) -> list:
        """检查单个文件"""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
                for pattern, key_type in self.patterns:
                    matches = re.finditer(pattern, content)
                    
                    for match in matches:
                        # 跳过注释和文档中的示例
                        line_num = content[:match.start()].count('\n') + 1
                        line_content = lines[line_num - 1] if line_num <= len(lines) else ""
                        
                        # 跳过注释行
                        if line_content.strip().startswith('#'):
                            continue
                        
                        # 跳过文档字符串
                        if '"""' in line_content or "'''" in line_content:
                            continue
                        
                        # 跳过明确的示例
                        if any(keyword in line_content.lower() for keyword in ['example', '示例', '你的key', 'your-key', 'xxxxx']):
                            continue
                        
                        issues.append({
                            'file': file_path.relative_to(self.project_root),
                            'line': line_num,
                            'type': key_type,
                            'content': line_content.strip()[:80]  # 只显示前80字符
                        })
        
        except Exception as e:
            print(f"⚠️ 无法读取文件 {file_path}: {e}")
        
        return issues
    
    def scan_directory(self) -> list:
        """扫描整个项目目录"""
        print("🔍 开始扫描项目中的 API Key...")
        print(f"📁 项目路径: {self.project_root}")
        print()
        
        all_issues = []
        scanned_files = 0
        
        # 扫描所有 Python 文件和 Markdown 文件
        for ext in ['*.py', '*.md', '*.txt', '*.json', '*.yaml', '*.yml']:
            for file_path in self.project_root.rglob(ext):
                # 跳过排除的目录
                if any(excluded in file_path.parts for excluded in self.exclude_dirs):
                    continue
                
                # 跳过排除的文件
                if file_path.name in self.exclude_files:
                    continue
                
                scanned_files += 1
                issues = self.check_file(file_path)
                all_issues.extend(issues)
        
        print(f"✅ 已扫描 {scanned_files} 个文件")
        print()
        
        return all_issues
    
    def generate_report(self, issues: list):
        """生成安全报告"""
        print("="*70)
        print("API Key 安全检查报告")
        print("="*70)
        print(f"扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"发现问题: {len(issues)}")
        print("="*70)
        
        if not issues:
            print("\n✅ 太好了！没有发现硬编码的 API Key！")
            print("\n建议：")
            print("  1. 继续使用 .env 文件管理 API Key")
            print("  2. 确保 .env 文件在 .gitignore 中")
            print("  3. 不要在代码中直接写入 API Key")
        else:
            print("\n❌ 发现以下安全问题：\n")
            
            for i, issue in enumerate(issues, 1):
                print(f"{i}. {issue['type']}")
                print(f"   文件: {issue['file']}")
                print(f"   行号: {issue['line']}")
                print(f"   内容: {issue['content']}")
                print()
            
            print("⚠️ 修复建议：")
            print("  1. 将所有 API Key 移到 .env 文件中")
            print("  2. 使用 os.getenv('NVIDIA_API_KEY') 读取 API Key")
            print("  3. 删除代码中硬编码的 API Key")
            print("  4. 提交前再次运行此检查工具")
        
        print("="*70)
        
        # 保存报告
        report_path = self.project_root / 'tests' / f'security_check_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("API Key 安全检查报告\n")
            f.write("="*70 + "\n")
            f.write(f"扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"发现问题: {len(issues)}\n")
            f.write("="*70 + "\n\n")
            
            for i, issue in enumerate(issues, 1):
                f.write(f"{i}. {issue['type']}\n")
                f.write(f"   文件: {issue['file']}\n")
                f.write(f"   行号: {issue['line']}\n")
                f.write(f"   内容: {issue['content']}\n\n")
        
        print(f"\n📄 报告已保存到: {report_path}")


def main():
    """主函数"""
    project_root = Path(__file__).parent.parent
    
    checker = APIKeySecurityChecker(project_root)
    issues = checker.scan_directory()
    checker.generate_report(issues)
    
    # 返回退出码
    return 0 if len(issues) == 0 else 1


if __name__ == "__main__":
    exit(main())
