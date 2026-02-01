"""监控 Streamlit 应用输出 - 捕获运行时错误"""
import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path

# 添加项目根目录
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class StreamlitMonitor:
    """Streamlit 监控器"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []
        
    def parse_line(self, line: str):
        """解析输出行"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # 检测错误
        if any(keyword in line.lower() for keyword in ['error', 'exception', 'traceback', 'failed']):
            self.errors.append((timestamp, line))
            print(f"❌ [{timestamp}] {line}", flush=True)
        # 检测警告
        elif any(keyword in line.lower() for keyword in ['warning', 'warn', 'deprecated']):
            self.warnings.append((timestamp, line))
            print(f"⚠️ [{timestamp}] {line}", flush=True)
        # 普通信息
        else:
            self.info.append((timestamp, line))
            print(f"ℹ️ [{timestamp}] {line}", flush=True)
    
    def run_streamlit(self):
        """运行 Streamlit 并监控输出"""
        print("╔══════════════════════════════════════════════════════════════════╗")
        print("║              Streamlit 应用监控器 - 实时错误捕获                  ║")
        print("╚══════════════════════════════════════════════════════════════════╝")
        print()
        print(f"📍 项目目录: {project_root}")
        print(f"🚀 启动 Streamlit 应用...")
        print(f"🔍 实时监控输出中...")
        print()
        print("="*70)
        print()
        
        try:
            # 启动 Streamlit
            process = subprocess.Popen(
                ['streamlit', 'run', 'app.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=str(project_root),
                bufsize=1,
                universal_newlines=True,
                encoding='utf-8',
                errors='replace'
            )
            
            # 实时读取输出
            for line in iter(process.stdout.readline, ''):
                if line:
                    self.parse_line(line.strip())
            
            process.wait()
            
        except KeyboardInterrupt:
            print("\n\n⚠️ 监控被用户中断")
            process.terminate()
        except Exception as e:
            print(f"\n\n❌ 监控器错误: {str(e)}")
        finally:
            self.generate_summary()
    
    def generate_summary(self):
        """生成监控摘要"""
        print("\n")
        print("="*70)
        print("监控摘要")
        print("="*70)
        print(f"❌ 错误数: {len(self.errors)}")
        print(f"⚠️ 警告数: {len(self.warnings)}")
        print(f"ℹ️ 信息数: {len(self.info)}")
        
        if self.errors:
            print("\n最近的错误:")
            for timestamp, error in self.errors[-5:]:  # 最后5个错误
                print(f"  [{timestamp}] {error}")
        
        if self.warnings:
            print("\n最近的警告:")
            for timestamp, warning in self.warnings[-5:]:  # 最后5个警告
                print(f"  [{timestamp}] {warning}")
        
        # 保存完整日志
        log_path = Path(__file__).parent / f"streamlit_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write("Streamlit 监控日志\n")
            f.write("="*70 + "\n\n")
            
            if self.errors:
                f.write("错误:\n")
                for timestamp, error in self.errors:
                    f.write(f"[{timestamp}] {error}\n")
                f.write("\n")
            
            if self.warnings:
                f.write("警告:\n")
                for timestamp, warning in self.warnings:
                    f.write(f"[{timestamp}] {warning}\n")
                f.write("\n")
        
        print(f"\n✅ 完整日志已保存到: {log_path}")
        print("="*70)


def main():
    monitor = StreamlitMonitor()
    monitor.run_streamlit()


if __name__ == "__main__":
    main()
