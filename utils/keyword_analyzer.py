"""关键词贡献度分析（后端逻辑）

通过对 Prompt 中的词做 Mask，并比较句向量相似度下降幅度，估计每个词的贡献度。
注意：首次调用会加载 `text2vec` 的 SentenceModel，可能较慢。
"""

import re
from typing import Optional

import jieba
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from text2vec import SentenceModel


_MODEL_NAME = "shibing624/text2vec-base-chinese"
_model: Optional[SentenceModel] = None


def _get_model() -> SentenceModel:
    global _model
    if _model is None:
        _model = SentenceModel(_MODEL_NAME)
    return _model


def analyze_keyword_contribution(prompt: str) -> pd.DataFrame:
    """分析 Prompt 中每个词的贡献度，返回按贡献度排序的 DataFrame。"""

    prompt_clean = re.sub(r"[^\w\u4e00-\u9fff]", " ", prompt).strip()
    words = [w for w in jieba.lcut(prompt_clean) if len(w) > 1]
    mask_dict = {word: prompt.replace(word, "[MASK]") for word in words}

    def get_embedding(text: str):
        return _get_model().encode(text)

    base_emb = get_embedding(prompt)
    base_emb_reshaped = base_emb.reshape(1, -1)

   # 第一步：计算所有词的贡献度，暂不判定等级
    result = {}
    for word, masked_prompt in mask_dict.items():
        mask_emb = get_embedding(masked_prompt).reshape(1, -1)
        sim = cosine_similarity(base_emb_reshaped, mask_emb)[0][0]
        contrib = round(1 - sim, 4)

        result[word] = {
            "mask后相似度": round(sim, 4),
            "贡献度差值": contrib
        }

    # 第二步：转换为DataFrame并按贡献度降序排序
    df = pd.DataFrame.from_dict(result, orient="index")
    df = df.sort_values("贡献度差值", ascending=False)

    # 第三步：按百分比划分等级（核心修改）
    total_words = len(df)
    if total_words == 0:  # 处理无有效词的边界情况
        return df

    # 计算各等级的分界索引
    high_threshold = int(total_words * 0.3)  # 前30%为高
    mid_threshold = int(total_words * 0.7)  # 30%-70%为中

    # 处理整除问题（比如总词数10→前3个高，4-7个中，8-10个低）
    # 为避免索引越界，用min确保不超过总长度
    high_threshold = min(high_threshold, total_words)
    mid_threshold = min(mid_threshold, total_words)

    # 批量赋值等级
    df["贡献度等级"] = "低"  # 先默认设为低
    df.iloc[:high_threshold, df.columns.get_loc("贡献度等级")] = "高"  # 前30%设为高
    df.iloc[high_threshold:mid_threshold, df.columns.get_loc("贡献度等级")] = "中"  # 30%-70%设为中

    return df
