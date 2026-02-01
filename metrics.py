"""
评估指标计算模块
实现 Accuracy / BLEU / ROUGE 等自动化评估指标
"""
import jieba
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from rouge_score import rouge_scorer
from sklearn.metrics import accuracy_score
from typing import List


class MetricsCalculator:
    """自动化评估指标计算器"""
    
    @staticmethod
    def calculate_accuracy(predictions: List[str], references: List[str]) -> float:
        """
        分类任务：计算准确率
        
        Args:
            predictions: 模型预测结果列表，如 ['Positive', 'Negative', 'Positive']
            references: 标准参考答案列表，如 ['Positive', 'Positive', 'Positive']
            
        Returns:
            准确率 (0-100)
            
        Example:
            >>> calc = MetricsCalculator()
            >>> calc.calculate_accuracy(['A', 'B', 'A'], ['A', 'A', 'A'])
            66.67
        """
        if len(predictions) != len(references):
            raise ValueError(f"预测结果数量 ({len(predictions)}) 与参考答案数量 ({len(references)}) 不一致")
        
        # 清洗数据：去除空格、转小写，防止因格式问题导致误判
        clean_preds = [str(p).strip().lower() for p in predictions]
        clean_refs = [str(r).strip().lower() for r in references]
        
        # 使用 sklearn 计算准确率
        score = accuracy_score(clean_refs, clean_preds)
        return round(score * 100, 2)
    
    @staticmethod
    def calculate_rouge(prediction: str, reference: str, lang: str = "zh") -> dict:
        """
        摘要任务：计算 ROUGE 分数
        
        Args:
            prediction: 模型生成的摘要
            reference: 人工撰写的参考摘要
            lang: 语言类型，"zh" 为中文（需要分词），"en" 为英文
            
        Returns:
            包含 ROUGE-1, ROUGE-2, ROUGE-L 的字典
            
        Example:
            >>> calc = MetricsCalculator()
            >>> calc.calculate_rouge("我喜欢AI", "我超级喜欢AI", lang="zh")
            {'rouge1': 75.0, 'rouge2': 50.0, 'rougeL': 75.0}
        """
        # 中文需要分词，否则 ROUGE 计算不准
        if lang == "zh":
            pred_tokens = " ".join(jieba.cut(prediction))
            ref_tokens = " ".join(jieba.cut(reference))
            # 中文不需要 stemmer（词干提取是英文特有的）
            use_stemmer = False
        else:
            pred_tokens = prediction
            ref_tokens = reference
            # 英文使用 stemmer
            use_stemmer = True
        
        # 使用 rouge_scorer 计算
        scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=use_stemmer)
        scores = scorer.score(ref_tokens, pred_tokens)
        
        # 返回 F1 分数 (0-100)
        return {
            'rouge1': round(scores['rouge1'].fmeasure * 100, 2),
            'rouge2': round(scores['rouge2'].fmeasure * 100, 2),
            'rougeL': round(scores['rougeL'].fmeasure * 100, 2)
        }
    
    @staticmethod
    def calculate_bleu(prediction: str, reference: str, lang: str = "zh") -> float:
        """
        翻译任务：计算 BLEU 分数
        
        Args:
            prediction: 模型生成的翻译结果
            reference: 人工翻译的参考译文
            lang: 语言类型，"zh" 为中文（需要分词），"en" 为英文
            
        Returns:
            BLEU 分数 (0-100)
            
        Example:
            >>> calc = MetricsCalculator()
            >>> calc.calculate_bleu("I love AI", "I love AI very much", lang="en")
            54.32
        """
        # 中文需要分词
        if lang == "zh":
            pred_tokens = list(jieba.cut(prediction))
            ref_tokens = [list(jieba.cut(reference))]  # reference 需要是 list of list
        else:
            pred_tokens = prediction.split()
            ref_tokens = [reference.split()]
        
        # 使用平滑函数，防止句子太短导致分数为 0
        smooth = SmoothingFunction().method1
        
        try:
            score = sentence_bleu(ref_tokens, pred_tokens, smoothing_function=smooth)
        except ZeroDivisionError:
            # 如果预测为空或完全不匹配
            score = 0.0
        
        return round(score * 100, 2)
    
    @staticmethod
    def get_metric_interpretation(metric_name: str, score: float) -> tuple[str, str, str]:
        """
        根据指标分数给出解释和建议
        
        Args:
            metric_name: 指标名称 ("accuracy", "rouge", "bleu")
            score: 分数 (0-100)
            
        Returns:
            (等级, 颜色, 建议文本)
        """
        if score >= 80:
            level = "优异"
            color = "success"
            advice = "表现非常好！继续保持。"
        elif score >= 60:
            level = "良好"
            color = "info"
            advice = "表现不错，可以尝试微调 Prompt 以进一步提升。"
        elif score >= 40:
            level = "及格"
            color = "warning"
            advice = "基本达标，建议优化 Prompt 的结构或增加更多约束条件。"
        else:
            level = "需改进"
            color = "error"
            advice = "与参考答案差异较大，建议重新设计 Prompt 或检查参考答案是否合理。"
        
        # 针对不同指标的具体建议
        specific_advice = {
            "accuracy": {
                "low": "分类不准确。尝试：1) 增加标签定义的详细程度 2) 提供更多示例 3) 强化思维链引导",
                "medium": "分类基本正确。可以：1) 优化标签判断标准 2) 增加边界案例的说明",
                "high": "分类准确！Prompt 设计合理。"
            },
            "rouge": {
                "low": "摘要覆盖度不足。尝试：1) 明确信息提取规则 2) 强调关键词保留 3) 调整摘要长度",
                "medium": "摘要质量尚可。可以：1) 优化输出格式 2) 增加关注点的优先级排序",
                "high": "摘要质量优秀！关键信息覆盖完整。"
            },
            "bleu": {
                "low": "翻译与参考译文差异较大。尝试：1) 强化术语表 2) 明确风格要求 3) 使用三步翻译法",
                "medium": "翻译基本准确。可以：1) 增加领域专业术语 2) 优化表达的地道性",
                "high": "翻译质量很高！与参考译文高度一致。"
            }
        }
        
        # 根据分数选择具体建议
        if score >= 60:
            specific = specific_advice.get(metric_name, {}).get("high", advice)
        elif score >= 40:
            specific = specific_advice.get(metric_name, {}).get("medium", advice)
        else:
            specific = specific_advice.get(metric_name, {}).get("low", advice)
        
        return level, color, specific


# 测试代码
if __name__ == "__main__":
    calc = MetricsCalculator()
    
    print("=" * 60)
    print("测试 Accuracy (分类任务)")
    print("=" * 60)
    acc = calc.calculate_accuracy(['Positive', 'Negative', 'Positive'], ['Positive', 'Positive', 'Positive'])
    print(f"准确率: {acc}%")
    print(f"解释: {calc.get_metric_interpretation('accuracy', acc)}")
    
    print("\n" + "=" * 60)
    print("测试 ROUGE (摘要任务)")
    print("=" * 60)
    rouge = calc.calculate_rouge("我喜欢人工智能技术", "我非常喜欢人工智能和机器学习技术", lang="zh")
    print(f"ROUGE 分数: {rouge}")
    print(f"解释: {calc.get_metric_interpretation('rouge', rouge['rougeL'])}")
    
    print("\n" + "=" * 60)
    print("测试 BLEU (翻译任务)")
    print("=" * 60)
    bleu = calc.calculate_bleu("I love AI", "I love artificial intelligence", lang="en")
    print(f"BLEU 分数: {bleu}")
    print(f"解释: {calc.get_metric_interpretation('bleu', bleu)}")
