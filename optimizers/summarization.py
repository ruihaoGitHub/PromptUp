"""
摘要任务优化器
"""
from typing import Optional
from config.models import SummarizationPrompt
from config.template_loader import get_summarization_meta_prompt
from .base import OptimizerBase


class SummarizationOptimizer(OptimizerBase):
    """摘要任务优化器"""
    
    def optimize(self,
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
        print(f"\n{'='*60}")
        print(f"📝 开始摘要任务 Prompt 优化")
        print(f"{'='*60}")
        print(f"🔌 API 提供商: {self.provider.upper()}")
        print(f"🤖 使用模型: {self.model}")
        print(f"📝 任务描述: {task_description[:50]}...")
        print(f"📄 源文本类型: {source_type}")
        print(f"👥 目标受众: {target_audience}")
        print(f"🎯 关注点: {focus_points[:50]}...")
        if length_constraint:
            print(f"📏 篇幅限制: {length_constraint}")
        print(f"{'='*60}\n")
        
        # 使用外部模板加载 Meta-Prompt
        system_prompt = get_summarization_meta_prompt(
            task_description, source_type, target_audience, focus_points, length_constraint
        )
        
        try:
            # 调用 LLM
            content = self._call_llm(system_prompt)
            
            # 提取并解析 JSON
            content = self._extract_json(content)
            optimized = self._parse_and_validate(content, SummarizationPrompt)
            
            print("✅ 摘要 Prompt 优化完成！")
            print(f"{'='*60}\n")
            
            return optimized
            
        except Exception as e:
            self._handle_error(e, "摘要")
