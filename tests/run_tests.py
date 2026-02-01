"""
PromptUp 项目自动化测试脚本
执行 Level 1-3 的测试（导入、单元、集成）
"""
import sys
import traceback
from typing import List, Tuple


class TestResult:
    """测试结果类"""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.errors = []
    
    def add_pass(self, test_name: str):
        self.passed += 1
        print(f"  ✅ {test_name}")
    
    def add_fail(self, test_name: str, error: str):
        self.failed += 1
        self.errors.append((test_name, error))
        print(f"  ❌ {test_name}")
        print(f"     错误: {error[:100]}...")
    
    def add_skip(self, test_name: str, reason: str):
        self.skipped += 1
        print(f"  ⏭️  {test_name} (跳过: {reason})")
    
    def summary(self):
        total = self.passed + self.failed + self.skipped
        print(f"\n{'='*60}")
        print(f"📊 测试总结")
        print(f"{'='*60}")
        print(f"总测试数: {total}")
        print(f"✅ 通过: {self.passed}")
        print(f"❌ 失败: {self.failed}")
        print(f"⏭️  跳过: {self.skipped}")
        
        if self.failed > 0:
            print(f"\n❌ 失败的测试:")
            for test_name, error in self.errors:
                print(f"  • {test_name}")
                print(f"    {error[:200]}")
        
        success_rate = (self.passed / total * 100) if total > 0 else 0
        print(f"\n成功率: {success_rate:.1f}%")
        print(f"{'='*60}\n")
        
        return self.failed == 0


def run_test(test_name: str, test_func, result: TestResult):
    """运行单个测试"""
    try:
        test_func()
        result.add_pass(test_name)
    except Exception as e:
        error_msg = str(e) if str(e) else traceback.format_exc()
        result.add_fail(test_name, error_msg)


# ============================================================
# Level 1: 导入测试
# ============================================================

def test_import_optimizer():
    """测试 optimizer.py 导入"""
    from optimizer import PromptOptimizer


def test_import_metrics():
    """测试 metrics.py 导入"""
    from metrics import MetricsCalculator


def test_import_app():
    """测试 app.py 导入"""
    import app


def test_import_utils():
    """测试 utils 模块导入"""
    from utils import safe_json_loads, clean_improved_prompt, parse_markdown_response


def test_import_config():
    """测试 config 模块导入"""
    from config.models import OptimizedPrompt, SearchSpace, SearchResult
    from config.template_loader import get_generation_meta_prompt


def test_import_optimizers():
    """测试 optimizers 模块导入"""
    from optimizers import ClassificationOptimizer, SummarizationOptimizer, TranslationOptimizer


def test_import_algorithms():
    """测试 algorithms 模块导入"""
    from algorithms import (
        SearchSpaceGenerator,
        RandomSearchAlgorithm,
        GeneticAlgorithm,
        BayesianOptimization
    )


def test_import_pages():
    """测试 pages 模块导入"""
    from pages import GenerationPage, ClassificationPage, SummarizationPage, TranslationPage


def test_import_ui():
    """测试 ui 模块导入"""
    from ui import apply_custom_styles, render_sidebar


def test_import_services():
    """测试 services 模块导入"""
    from services import LLMService, ResponseParser


# ============================================================
# Level 2: 单元测试
# ============================================================

def test_llm_service_supports_json_mode():
    """测试 LLMService.supports_json_mode()"""
    from services import LLMService
    
    assert LLMService.supports_json_mode("openai") == True
    assert LLMService.supports_json_mode("nvidia") == False
    assert LLMService.supports_json_mode("OPENAI") == True  # 大小写不敏感


def test_response_parser_extract_json():
    """测试 ResponseParser 提取 JSON"""
    from services import ResponseParser
    
    # 测试 Markdown JSON 块
    content1 = '```json\n{"key": "value"}\n```'
    result1 = ResponseParser.extract_json_from_response(content1)
    assert "```" not in result1
    assert "key" in result1
    
    # 测试普通代码块
    content2 = '```\n{"key": "value"}\n```'
    result2 = ResponseParser.extract_json_from_response(content2)
    assert "```" not in result2
    
    # 测试纯文本
    content3 = '{"key": "value"}'
    result3 = ResponseParser.extract_json_from_response(content3)
    assert result3 == content3


def test_response_parser_parse_json():
    """测试 ResponseParser 解析 JSON"""
    from services import ResponseParser
    
    json_str = '{"thinking_process": "test", "improved_prompt": "result"}'
    result = ResponseParser.parse_json(json_str)
    
    assert isinstance(result, dict)
    assert result["thinking_process"] == "test"
    assert result["improved_prompt"] == "result"


def test_optimized_prompt_model():
    """测试 OptimizedPrompt 数据模型"""
    from config.models import OptimizedPrompt
    
    data = {
        "thinking_process": "测试思考过程",
        "improved_prompt": "改进后的提示词",
        "enhancement_techniques": ["技术1", "技术2"],
        "keywords_added": ["关键词1"],
        "structure_applied": "CO-STAR"
    }
    
    prompt = OptimizedPrompt(**data)
    assert prompt.thinking_process == "测试思考过程"
    assert prompt.improved_prompt == "改进后的提示词"
    assert len(prompt.enhancement_techniques) == 2


def test_search_space_model():
    """测试 SearchSpace 数据模型"""
    from config.models import SearchSpace
    
    data = {
        "roles": ["专家", "助手"],
        "styles": ["简洁", "详细"],
        "techniques": ["技巧1", "技巧2"]
    }
    
    space = SearchSpace(**data)
    assert len(space.roles) == 2
    assert len(space.styles) == 2
    assert len(space.techniques) == 2


def test_safe_json_loads():
    """测试 safe_json_loads 工具函数"""
    from utils import safe_json_loads
    
    # 正常 JSON
    result1 = safe_json_loads('{"key": "value"}')
    assert result1["key"] == "value"
    
    # 带转义的 JSON
    result2 = safe_json_loads(r'{"key": "value"}')
    assert "key" in result2


def test_clean_improved_prompt():
    """测试 clean_improved_prompt 工具函数"""
    from utils import clean_improved_prompt
    
    # 正常文本
    text1 = "这是正常的提示词"
    result1 = clean_improved_prompt(text1)
    assert result1 == text1
    
    # 包含 JSON 包裹的文本
    text2 = '{"improved_prompt": "实际内容"}'
    result2 = clean_improved_prompt(text2)
    # 应该提取出实际内容


# ============================================================
# Level 3: 集成测试
# ============================================================

def test_optimizer_initialization():
    """测试 PromptOptimizer 初始化"""
    from optimizer import PromptOptimizer
    
    # 使用测试配置初始化
    optimizer = PromptOptimizer(
        api_key="test-key-for-init",
        model="test-model",
        provider="nvidia"
    )
    
    # 验证 LLM 已初始化
    assert optimizer.llm is not None
    assert optimizer.provider == "nvidia"
    assert optimizer.model == "test-model"
    
    # 验证任务优化器已初始化
    assert optimizer.classification_optimizer is not None
    assert optimizer.summarization_optimizer is not None
    assert optimizer.translation_optimizer is not None
    
    # 验证算法已初始化
    assert optimizer.search_space_generator is not None
    assert optimizer.random_search is not None
    assert optimizer.genetic_algorithm is not None
    assert optimizer.bayesian_optimization is not None
    
    print("    ℹ️  所有组件已正确初始化")


def test_llm_service_create_nvidia():
    """测试 LLMService 创建 NVIDIA LLM"""
    from services import LLMService
    
    llm = LLMService.create_llm(
        provider="nvidia",
        api_key="test-key",
        model="test-model"
    )
    
    assert llm is not None
    print("    ℹ️  NVIDIA LLM 创建成功")


def test_llm_service_create_openai():
    """测试 LLMService 创建 OpenAI LLM"""
    from services import LLMService
    
    llm = LLMService.create_llm(
        provider="openai",
        api_key="test-key",
        model="gpt-4o"
    )
    
    assert llm is not None
    print("    ℹ️  OpenAI LLM 创建成功")


def test_metrics_calculator():
    """测试 MetricsCalculator"""
    from metrics import MetricsCalculator
    
    calc = MetricsCalculator()
    
    # 测试准确率
    predictions = ["A", "B", "C"]
    ground_truths = ["A", "B", "C"]
    accuracy = calc.calculate_accuracy(predictions, ground_truths)
    assert accuracy == 100.0
    
    print("    ℹ️  MetricsCalculator 工作正常")


# ============================================================
# 主测试函数
# ============================================================

def run_level1_tests(result: TestResult):
    """运行 Level 1: 导入测试"""
    print(f"\n{'='*60}")
    print("📦 Level 1: 导入测试")
    print(f"{'='*60}\n")
    
    tests = [
        ("optimizer.py 导入", test_import_optimizer),
        ("metrics.py 导入", test_import_metrics),
        ("app.py 导入", test_import_app),
        ("utils 模块导入", test_import_utils),
        ("config 模块导入", test_import_config),
        ("optimizers 模块导入", test_import_optimizers),
        ("algorithms 模块导入", test_import_algorithms),
        ("pages 模块导入", test_import_pages),
        ("ui 模块导入", test_import_ui),
        ("services 模块导入", test_import_services),
    ]
    
    for test_name, test_func in tests:
        run_test(test_name, test_func, result)


def run_level2_tests(result: TestResult):
    """运行 Level 2: 单元测试"""
    print(f"\n{'='*60}")
    print("🧪 Level 2: 单元测试")
    print(f"{'='*60}\n")
    
    tests = [
        ("LLMService.supports_json_mode()", test_llm_service_supports_json_mode),
        ("ResponseParser 提取 JSON", test_response_parser_extract_json),
        ("ResponseParser 解析 JSON", test_response_parser_parse_json),
        ("OptimizedPrompt 模型", test_optimized_prompt_model),
        ("SearchSpace 模型", test_search_space_model),
        ("safe_json_loads 函数", test_safe_json_loads),
        ("clean_improved_prompt 函数", test_clean_improved_prompt),
    ]
    
    for test_name, test_func in tests:
        run_test(test_name, test_func, result)


def run_level3_tests(result: TestResult):
    """运行 Level 3: 集成测试"""
    print(f"\n{'='*60}")
    print("🔗 Level 3: 集成测试")
    print(f"{'='*60}\n")
    
    tests = [
        ("PromptOptimizer 初始化", test_optimizer_initialization),
        ("LLMService 创建 NVIDIA LLM", test_llm_service_create_nvidia),
        ("LLMService 创建 OpenAI LLM", test_llm_service_create_openai),
        ("MetricsCalculator 功能", test_metrics_calculator),
    ]
    
    for test_name, test_func in tests:
        run_test(test_name, test_func, result)


def main():
    """主测试入口"""
    print("\n" + "="*60)
    print("🚀 PromptUp 项目自动化测试")
    print("="*60)
    print("测试范围: Level 1-3 (导入、单元、集成)")
    print("="*60 + "\n")
    
    result = TestResult()
    
    # 运行测试
    run_level1_tests(result)
    run_level2_tests(result)
    run_level3_tests(result)
    
    # 显示总结
    success = result.summary()
    
    # 返回退出码
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
