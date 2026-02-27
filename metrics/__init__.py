"""
评估指标计算模块（包版本）

说明：原先位于项目根目录的 metrics.py 已迁移为 metrics/ 包，
以保持 `from metrics import MetricsCalculator` 的导入方式不变。

实现 Accuracy / BLEU / ROUGE 等自动化评估指标。
"""

from typing import List

import jieba
from nltk.translate.bleu_score import SmoothingFunction, sentence_bleu
from rouge_score import rouge_scorer
from rouge_score.tokenizers import Tokenizer
from sklearn.metrics import accuracy_score


class ChineseTokenizer(Tokenizer):
    """中文分词器，用于 ROUGE 计算"""

    def tokenize(self, text):
        """使用 jieba 进行中文分词"""
        return list(jieba.cut(text))


class MetricsCalculator:
    """自动化评估指标计算器"""

    @staticmethod
    def calculate_accuracy(predictions: List[str], references: List[str]) -> float:
        """分类任务：计算准确率 (0-100)"""
        if len(predictions) != len(references):
            raise ValueError(
                f"预测结果数量 ({len(predictions)}) 与参考答案数量 ({len(references)}) 不一致"
            )

        clean_preds = [str(p).strip().lower() for p in predictions]
        clean_refs = [str(r).strip().lower() for r in references]

        score = accuracy_score(clean_refs, clean_preds)
        return round(score * 100, 2)

    @staticmethod
    def calculate_rouge(prediction: str, reference: str, lang: str = "zh") -> dict:
        """摘要任务：计算 ROUGE 分数，返回 F1 (0-100)"""
        if lang == "zh":
            scorer = rouge_scorer.RougeScorer(
                ["rouge1", "rouge2", "rougeL"],
                use_stemmer=False,
                tokenizer=ChineseTokenizer(),
            )
        else:
            scorer = rouge_scorer.RougeScorer(
                ["rouge1", "rouge2", "rougeL"], use_stemmer=True
            )

        scores = scorer.score(reference, prediction)

        return {
            "rouge1": round(scores["rouge1"].fmeasure * 100, 2),
            "rouge2": round(scores["rouge2"].fmeasure * 100, 2),
            "rougeL": round(scores["rougeL"].fmeasure * 100, 2),
        }

    @staticmethod
    def calculate_bleu(prediction: str, reference: str, lang: str = "zh") -> float:
        """翻译任务：计算 BLEU (0-100)"""
        if lang == "zh":
            pred_tokens = list(jieba.cut(prediction))
            ref_tokens = [list(jieba.cut(reference))]
        else:
            pred_tokens = prediction.split()
            ref_tokens = [reference.split()]

        smooth = SmoothingFunction().method1

        try:
            score = sentence_bleu(ref_tokens, pred_tokens, smoothing_function=smooth)
        except ZeroDivisionError:
            score = 0.0

        return round(score * 100, 2)

    @staticmethod
    def get_metric_interpretation(metric_name: str, score: float) -> tuple[str, str, str]:
        """根据指标分数给出解释和建议"""
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

        specific_advice = {
            "accuracy": {
                "low": "分类不准确。尝试：1) 增加标签定义 2) 提供更多示例 3) 强化思维链引导",
                "medium": "分类基本正确。可以：1) 优化标签判断标准 2) 增加边界案例的说明",
                "high": "分类准确！Prompt 设计合理。",
            },
            "rouge": {
                "low": "摘要覆盖度不足。尝试：1) 明确信息提取规则 2) 强调关键词保留 3) 调整摘要长度",
                "medium": "摘要质量尚可。可以：1) 优化输出格式 2) 增加关注点的优先级排序",
                "high": "摘要质量优秀！关键信息覆盖完整。",
            },
            "bleu": {
                "low": "翻译与参考译文差异较大。尝试：1) 强化术语表 2) 明确风格要求 3) 使用三步翻译法",
                "medium": "翻译基本准确。可以：1) 增加领域专业术语 2) 优化表达的地道性",
                "high": "翻译质量很高！与参考译文高度一致。",
            },
        }

        if score >= 60:
            specific = specific_advice.get(metric_name, {}).get("high", advice)
        elif score >= 40:
            specific = specific_advice.get(metric_name, {}).get("medium", advice)
        else:
            specific = specific_advice.get(metric_name, {}).get("low", advice)

        return level, color, specific
