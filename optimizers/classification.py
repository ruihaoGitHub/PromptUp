"""
分类任务优化器
"""
from config.models import ClassificationPrompt
from config.template_loader import get_classification_meta_prompt
from .base import OptimizerBase


class ClassificationOptimizer(OptimizerBase):
    """分类任务优化器"""
    
    def optimize(self, task_description: str, labels: list[str]) -> ClassificationPrompt:
        """
        针对分类任务的优化函数
        
        Args:
            task_description: 分类任务描述，如 "判断用户评论的情感倾向"
            labels: 目标标签列表，如 ["Positive", "Negative", "Neutral"]
            
        Returns:
            ClassificationPrompt: 优化后的分类 Prompt
        """
        print(f"\n{'='*60}")
        print(f"🏷️  开始分类任务 Prompt 优化")
        print(f"{'='*60}")
        print(f"🔌 API 提供商: {self.provider.upper()}")
        print(f"🤖 使用模型: {self.model}")
        print(f"📝 任务描述: {task_description[:50]}...")
        print(f"🏷️  目标标签: {', '.join(labels)}")
        print(f"{'='*60}\n")
        
        # 使用外部模板加载 Meta-Prompt
        system_prompt = get_classification_meta_prompt(task_description, labels)
        
        try:
            # 调用 LLM
            content = self._call_llm(system_prompt)
            
            # 提取并解析 JSON
            content = self._extract_json(content)
            optimized = self._parse_and_validate(content, ClassificationPrompt)
            
            print("✅ 分类 Prompt 优化完成！")
            print(f"{'='*60}\n")
            
            return optimized
            
        except Exception as e:
            self._handle_error(e, "分类")
