"""
Prompt 优化核心模块
实现自动化的 Prompt 生成、优化和评估
"""
import time
from typing import Optional, Literal
from langchain_core.prompts import ChatPromptTemplate
from templates import get_strategy_by_scene, OPTIMIZATION_PRINCIPLES
from config.models import OptimizedPrompt, ClassificationPrompt, SummarizationPrompt, TranslationPrompt, SearchSpace, SearchResult
from config.template_loader import get_generation_meta_prompt
from optimizers import ClassificationOptimizer, SummarizationOptimizer, TranslationOptimizer
from algorithms import SearchSpaceGenerator, RandomSearchAlgorithm, GeneticAlgorithm, BayesianOptimization
from services import LLMService, ResponseParser

try:
    import optuna
    OPTUNA_AVAILABLE = True
except ImportError:
    OPTUNA_AVAILABLE = False
    print("⚠️ Optuna 未安装，贝叶斯优化功能不可用。运行: pip install optuna")


class PromptOptimizer:
    """Prompt 自动优化器"""
    
    def __init__(self, 
                 api_key: Optional[str] = None, 
                 model: str = "meta/llama-3.1-405b-instruct", 
                 base_url: Optional[str] = None,
                 provider: Literal["openai", "nvidia"] = "nvidia",
                 temperature: float = 0.7,
                 top_p: float = 0.7,
                 max_tokens: int = 2048):
        """
        初始化优化器
        
        Args:
            api_key: API Key，如果不提供则从环境变量读取
            model: 使用的模型名称
            base_url: API base URL
            provider: API 提供商 ("openai" 或 "nvidia")
            temperature: 温度参数
            top_p: Top-p 采样参数
            max_tokens: 最大生成 token 数
        """
        self.provider = provider
        self.model = model
        
        # 使用 LLMService 创建 LLM 实例
        self.llm = LLMService.create_llm(
            provider=provider,
            api_key=api_key,
            model=model,
            base_url=base_url,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens
        )
        
        # 初始化任务优化器
        self.classification_optimizer = ClassificationOptimizer(self.llm, provider, model)
        self.summarization_optimizer = SummarizationOptimizer(self.llm, provider, model)
        self.translation_optimizer = TranslationOptimizer(self.llm, provider, model)
        
        # 初始化搜索算法
        self.search_space_generator = SearchSpaceGenerator(self.llm, provider)
        self.random_search = RandomSearchAlgorithm(self.llm)
        self.genetic_algorithm = GeneticAlgorithm(self.llm)
        self.bayesian_optimization = BayesianOptimization(self.llm)
    
    def optimize(self, 
                 user_prompt: str, 
                 scene_desc: str = "通用",
                 optimization_mode: str = "通用增强 (General)") -> OptimizedPrompt:
        """
        核心优化函数
        
        Args:
            user_prompt: 用户输入的原始 Prompt
            scene_desc: 场景描述
            optimization_mode: 优化模式
            
        Returns:
            OptimizedPrompt: 优化后的结构化 Prompt
        """
        # 打印优化开始信息
        print(f"\n{'='*60}")
        print(f"⚙️  开始 Prompt 优化")
        print(f"{'='*60}")
        print(f"🔌 API 提供商: {self.provider.upper()}")
        print(f"🤖 使用模型: {self.model}")
        print(f"🎯 优化模式: {optimization_mode}")
        print(f"📝 原始 Prompt: {user_prompt[:50]}{'...' if len(user_prompt) > 50 else ''}")
        if scene_desc:
            print(f"🎬 场景描述: {scene_desc[:50]}{'...' if len(scene_desc) > 50 else ''}")
        print(f"{'='*60}\n")
        
        # 获取场景对应的优化策略
        strategy = get_strategy_by_scene(optimization_mode)
        
        # 构建 Meta-Prompt
        system_prompt = self._build_meta_prompt(strategy, scene_desc)
        
        # 构建消息链
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "用户原始 Prompt：{input}\n\n场景补充说明：{scene}")
        ])
        
        # 执行优化
        try:
            print("📤 正在调用 API...")
            
            # 构建完整提示
            messages = prompt_template.format_messages(
                input=user_prompt,
                scene=scene_desc if scene_desc else "无特殊说明"
            )
            
            print(f"💬 消息长度: {len(str(messages))} 字符")
            
            # 调用 LLM（根据提供商选择是否使用 JSON mode）
            if LLMService.supports_json_mode(self.provider):
                print("🔧 使用 JSON mode")
                response = self.llm.invoke(
                    messages,
                    response_format={"type": "json_object"}
                )
            else:
                print("🔧 使用标准调用")
                response = self.llm.invoke(messages)
            
            time.sleep(0.5)  # API 调用延迟
            
            # 使用 ResponseParser 解析结果
            content = response.content
            print(f"📥 收到响应，长度: {len(content)} 字符")
            print(f"📄 响应前100字符: {content[:100]}...")
            
            # 解析 JSON 响应
            result_dict = ResponseParser.parse_optimization_response(content)
            
            print("🔨 正在验证数据结构...")
            optimized = OptimizedPrompt(**result_dict)
            
            # 清理 improved_prompt 字段
            original_prompt = optimized.improved_prompt
            cleaned_prompt, was_cleaned = ResponseParser.clean_prompt_field(original_prompt)
            
            if was_cleaned:
                # 创建新的优化结果对象
                optimized = OptimizedPrompt(
                    thinking_process=optimized.thinking_process,
                    improved_prompt=cleaned_prompt,
                    enhancement_techniques=optimized.enhancement_techniques,
                    keywords_added=optimized.keywords_added,
                    structure_applied=optimized.structure_applied
                )
            
            print("✅ 优化完成！")
            print(f"{'='*60}\n")
            
            return optimized
            
        except Exception as e:
            # 错误处理：详细记录到终端
            print(f"\n❌ 优化失败！")
            print(f"{'='*60}")
            
            error_msg = str(e)
            print(f"🐛 错误类型: {type(e).__name__}")
            print(f"📝 错误详情: {error_msg[:500]}")
            
            # 如果是 Pydantic 验证错误，打印详细信息
            if "validation" in error_msg.lower() or "Field required" in error_msg:
                print("\n⚠️ 这是数据结构验证错误，可能原因：")
                print("   1. 模型返回的 JSON 格式不符合要求")
                print("   2. 缺少必需的字段（thinking_process, improved_prompt 等）")
                print("   3. 模型可能不支持 JSON 格式输出")
                print("\n💡 建议：尝试更换模型，推荐使用 meta/llama-3.1-405b-instruct")
            
            # 打印完整堆栈
            import traceback
            print(f"\n📄 完整堆栈信息：")
            traceback.print_exc()
            print(f"{'='*60}\n")
            
            # 根据错误类型抛出明确的异常
            if "404" in error_msg:
                raise Exception(f"API 调用失败 (404): 请检查 API Key 是否有效，或模型名称是否正确。详细信息：{error_msg[:200]}")
            elif "401" in error_msg or "Unauthorized" in error_msg:
                raise Exception(f"API Key 无效或已过期。请检查您的 API Key 配置。")
            elif "rate_limit" in error_msg.lower():
                raise Exception(f"API 请求频率超限，请稍后再试。")
            else:
                raise Exception(f"优化失败: {error_msg[:300]}")
    
    def optimize_classification(self,
                               task_description: str,
                               labels: list[str]) -> ClassificationPrompt:
        """
        针对分类任务的优化函数
        
        Args:
            task_description: 分类任务描述，如 "判断用户评论的情感倾向"
            labels: 目标标签列表，如 ["Positive", "Negative", "Neutral"]
            
        Returns:
            ClassificationPrompt: 优化后的分类 Prompt
        """
        return self.classification_optimizer.optimize(task_description, labels)
    
    def optimize_summarization(self,
                              task_description: str,
                              source_type: str,
                              target_audience: str,
                              focus_points: str,
                              length_constraint: Optional[str] = None) -> SummarizationPrompt:
        """
        针对摘要任务的优化函数
        
        Args:
            task_description: 摘要任务描述，如 "总结技术会议的核心决策"
            source_type: 源文本类型，如 "会议记录"、"学术论文"、"新闻报道"
            target_audience: 目标读者，如 "技术经理"、"普通用户"
            focus_points: 核心关注点，如 "行动计划和负责人"
            length_constraint: 篇幅限制，如 "100字以内"、"3-5个要点"
            
        Returns:
            SummarizationPrompt: 优化后的摘要 Prompt
        """
        return self.summarization_optimizer.optimize(
            task_description, source_type, target_audience, focus_points, length_constraint
        )
    
    def optimize_translation(self,
                           source_lang: str,
                           target_lang: str,
                           domain: str,
                           tone: str,
                           user_glossary: str = "") -> TranslationPrompt:
        """
        针对翻译任务的优化函数
        
        Args:
            source_lang: 源语言，如 "中文"、"英文"
            target_lang: 目标语言
            domain: 应用领域，如 "通用日常"、"IT/技术文档"、"法律合同"等
            tone: 期望风格，如 "标准/准确"、"地道/口语化"
            user_glossary: 用户提供的术语表，格式如 "Prompt=提示词\nLLM=大语言模型"
            
        Returns:
            TranslationPrompt: 优化后的翻译 Prompt
        """
        return self.translation_optimizer.optimize(
            source_lang, target_lang, domain, tone, user_glossary
        )
    
    def _build_meta_prompt(self, strategy: dict, scene_desc: str) -> str:
        """构建 Meta-Prompt（教 LLM 如何优化 Prompt 的提示词）"""
        
        template_name = strategy.get("template", "CO-STAR")
        focus_principles = strategy.get("focus", ["clarity", "structure"])
        extra_requirements = strategy.get("extra_requirements", [])
        
        # 使用外部模板加载 Meta-Prompt
        return get_generation_meta_prompt(
            template_name,
            focus_principles,
            extra_requirements,
            scene_desc,
            OPTIMIZATION_PRINCIPLES
        )
    
    def _fallback_optimization(self, original_prompt: str, error: str) -> OptimizedPrompt:
        """当优化失败时的备用方案"""
        return OptimizedPrompt(
            thinking_process=f"优化过程中遇到错误：{error}。以下是基础优化版本。",
            improved_prompt=f"""
请以专业的态度完成以下任务：

{original_prompt}

要求：
1. 输出内容应该清晰、准确、完整
2. 使用恰当的格式组织信息
3. 注重细节和专业性
4. 如有需要，请展示你的思考过程
""",
            enhancement_techniques=["基础结构化", "添加通用要求"],
            keywords_added=[],
            structure_applied="简单优化"
        )
    
    def compare_results(self, original_prompt: str, optimized_prompt: str, 
                       test_query: Optional[str] = None) -> tuple[str, str]:
        """
        A/B 对比测试：分别运行原始和优化后的 Prompt
        
        Args:
            original_prompt: 原始 Prompt
            optimized_prompt: 优化后的 Prompt
            test_query: 可选的测试查询（如果 Prompt 本身不是直接的问题）
            
        Returns:
            (原始结果, 优化后结果)
        """
        try:
            # 运行原始 Prompt
            response_original = self.llm.invoke(original_prompt)
            time.sleep(0.3)  # API 调用延迟，避免频率过快（A/B 测试需要较长等待）
            result_original = response_original.content
            
            # 运行优化后的 Prompt
            response_optimized = self.llm.invoke(optimized_prompt)
            time.sleep(0.3)  # API 调用延迟，避免频率过快（A/B 测试需要较长等待）
            result_optimized = response_optimized.content
            
            return result_original, result_optimized
            
        except Exception as e:
            return f"运行失败: {str(e)}", f"运行失败: {str(e)}"
    
    def batch_optimize(self, prompts: list[str], 
                       scene_desc: str = "通用",
                       optimization_mode: str = "通用增强 (General)") -> list[OptimizedPrompt]:
        """
        批量优化多个 Prompt
        
        Args:
            prompts: Prompt 列表
            scene_desc: 场景描述
            optimization_mode: 优化模式
            
        Returns:
            优化结果列表
        """
        results = []
        for prompt in prompts:
            result = self.optimize(prompt, scene_desc, optimization_mode)
            results.append(result)
        return results


    def generate_search_space(self, task_description: str, task_type: str = "classification") -> SearchSpace:
        """
        让 LLM 自动分析任务，生成可供搜索的变量池
        
        Args:
            task_description: 任务描述
            task_type: 任务类型 (classification/summarization/translation)
            
        Returns:
            SearchSpace 对象，包含 roles, styles, techniques
        """
        return self.search_space_generator.generate(task_description, task_type)
    
    
    def run_random_search(
        self, 
        task_description: str,
        task_type: str,
        test_dataset: list[dict],
        search_space: SearchSpace,
        iterations: int = 5,
        progress_callback=None,
        labels: list[str] = None
    ) -> tuple[list[SearchResult], SearchResult]:
        """
        执行随机搜索优化
        
        Args:
            task_description: 任务描述
            task_type: 任务类型 (classification/summarization/translation)
            test_dataset: 测试数据集 [{'input': '...', 'ground_truth': '...'}]
            search_space: 搜索空间
            iterations: 搜索迭代次数
            progress_callback: 进度回调函数 callback(current, total, message)
            labels: 分类任务的标签列表（仅分类任务需要）
            
        Returns:
            (所有结果列表, 最佳结果)
        """
        return self.random_search.run(
            task_description, task_type, test_dataset, search_space, iterations, progress_callback, labels
        )
    
    def run_genetic_algorithm(
        self,
        task_description: str,
        task_type: str,
        test_dataset: list,
        search_space: 'SearchSpace',
        generations: int = 5,
        population_size: int = 8,
        elite_ratio: float = 0.2,
        mutation_rate: float = 0.2,
        progress_callback: Optional[callable] = None
    ) -> tuple[list, 'SearchResult', list]:
        """
        遗传算法优化 Prompt
        
        委托给 GeneticAlgorithm 类执行
        """
        return self.genetic_algorithm.run(
            task_description, task_type, test_dataset, search_space,
            generations, population_size, elite_ratio, mutation_rate, progress_callback
        )

    def run_bayesian_optimization(
        self,
        task_description: str,
        task_type: str,
        test_dataset: list,
        search_space: 'SearchSpace',
        n_trials: int = 20,
        progress_callback: Optional[callable] = None
    ) -> tuple[list, 'SearchResult', list]:
        """
        贝叶斯优化 Prompt
        
        委托给 BayesianOptimization 类执行
        """
        return self.bayesian_optimization.run(
            task_description, task_type, test_dataset, search_space,
            n_trials, progress_callback
        )


# 便捷函数
def quick_optimize(user_prompt: str, 
                   api_key: Optional[str] = None,
                   scene: str = "通用",
                   mode: str = "通用增强 (General)",
                   provider: str = "nvidia") -> OptimizedPrompt:
    """
    快速优化函数，适合简单调用
    
    Example:
        result = quick_optimize("写个贪吃蛇", scene="Python初学者", mode="代码生成 (Coding)")
        print(result.improved_prompt)
    """
    optimizer = PromptOptimizer(api_key=api_key, provider=provider)
    return optimizer.optimize(user_prompt, scene, mode)


if __name__ == "__main__":
    # 测试代码
    from dotenv import load_dotenv
    load_dotenv()
    
    # 示例测试
    test_prompt = "写个贪吃蛇游戏"
    
    optimizer = PromptOptimizer()
    result = optimizer.optimize(
        test_prompt, 
        scene_desc="Python, 给小孩学编程用",
        optimization_mode="代码生成 (Coding)"
    )
    
    print("=" * 50)
    print("优化思考过程：")
    print(result.thinking_process)
    print("\n" + "=" * 50)
    print("优化后的 Prompt：")
    print(result.improved_prompt)
    print("\n" + "=" * 50)
    print("使用的技术：", result.enhancement_techniques)
    print("新增关键词：", result.keywords_added)
