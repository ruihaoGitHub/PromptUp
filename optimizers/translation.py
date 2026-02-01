"""
翻译任务优化器
"""
from config.models import TranslationPrompt
from config.template_loader import get_translation_meta_prompt
from .base import OptimizerBase


class TranslationOptimizer(OptimizerBase):
    """翻译任务优化器"""
    
    def optimize(self,
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
        print(f"\n{'='*60}")
        print(f"🌍 开始翻译任务 Prompt 优化")
        print(f"{'='*60}")
        print(f"🔌 API 提供商: {self.provider.upper()}")
        print(f"🤖 使用模型: {self.model}")
        print(f"🔄 翻译方向: {source_lang} → {target_lang}")
        print(f"📚 应用领域: {domain}")
        print(f"🎨 期望风格: {tone}")
        if user_glossary:
            print(f"📖 术语表: {len(user_glossary.split(chr(10)))} 条")
        print(f"{'='*60}\n")
        
        # 使用外部模板加载 Meta-Prompt
        system_prompt = get_translation_meta_prompt(
            source_lang, target_lang, domain, tone, user_glossary
        )
        
        try:
            # 调用 LLM
            content = self._call_llm(system_prompt)
            
            # 提取并解析 JSON
            content = self._extract_json(content)
            optimized = self._parse_and_validate(content, TranslationPrompt)
            
            print("✅ 翻译 Prompt 优化完成！")
            print(f"{'='*60}\n")
            
            return optimized
            
        except Exception as e:
            self._handle_error(e, "翻译")
