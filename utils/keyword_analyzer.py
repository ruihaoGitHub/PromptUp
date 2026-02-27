"""关键词贡献度分析（后端逻辑）

通过对 Prompt 中的词做 Mask，并比较句向量相似度下降幅度，估计每个词的贡献度。
注意：首次调用会加载 `text2vec` 的 SentenceModel，可能较慢。
"""

import re
from functools import lru_cache
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


@lru_cache(maxsize=128)
def _analyze_keyword_contribution_cached(prompt: str) -> pd.DataFrame:
    """分析 Prompt 中每个词的贡献度（带缓存，避免 Streamlit rerun 重复计算）。"""

    prompt_clean = re.sub(r"[^\w\u4e00-\u9fff]", " ", prompt).strip()
    words_raw = [w for w in jieba.lcut(prompt_clean) if len(w) > 1]
    # 去重但保持顺序（避免重复 encode 同一个词）
    words = list(dict.fromkeys(words_raw))
    if not words:
        return pd.DataFrame(columns=["mask后相似度", "贡献度差值", "贡献度等级"])

    masked_prompts = [prompt.replace(word, "[MASK]") for word in words]

    model = _get_model()
    base_emb = model.encode(prompt).reshape(1, -1)
    masked_embs = model.encode(masked_prompts)

    # 批量计算相似度：shape -> (n_words,)
    sims = cosine_similarity(base_emb, masked_embs)[0]

    result = {
        word: {
            "mask后相似度": round(float(sim), 4),
            "贡献度差值": round(1 - float(sim), 4),
        }
        for word, sim in zip(words, sims)
    }

    df = pd.DataFrame.from_dict(result, orient="index")
    df = df.sort_values("贡献度差值", ascending=False)

    total_words = len(df)
    if total_words == 0:
        df["贡献度等级"] = []
        return df

    high_threshold = min(int(total_words * 0.3), total_words)
    mid_threshold = min(int(total_words * 0.7), total_words)

    df["贡献度等级"] = "低"
    df.iloc[:high_threshold, df.columns.get_loc("贡献度等级")] = "高"
    df.iloc[high_threshold:mid_threshold, df.columns.get_loc("贡献度等级")] = "中"
    return df


def analyze_keyword_contribution(prompt: str) -> pd.DataFrame:
    """分析 Prompt 中每个词的贡献度，返回按贡献度排序的 DataFrame。"""
    # 返回拷贝，避免调用方对 df 的修改污染缓存
    return _analyze_keyword_contribution_cached(prompt).copy()
