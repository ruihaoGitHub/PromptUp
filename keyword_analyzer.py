import jieba
import re
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from text2vec import SentenceModel

# 模型只加载一次，提速
model = SentenceModel("C:/Users/as/PycharmProjects/Prompt_contyibution/text2vec-model")

def analyze_keyword_contribution(prompt: str):

    # 分词 + Mask
    prompt_clean = re.sub(r'[^\w\u4e00-\u9fff]', ' ', prompt).strip()
    words = [w for w in jieba.lcut(prompt_clean) if len(w) > 1]
    mask_dict = {word: prompt.replace(word, "[MASK]") for word in words}

    # 向量
    def get_embedding(text):
        return model.encode(text)

    base_emb = get_embedding(prompt)
    base_emb_reshaped = base_emb.reshape(1, -1)

    # 相似度 & 贡献度
    result = {}
    for word, masked_prompt in mask_dict.items():
        mask_emb = get_embedding(masked_prompt).reshape(1, -1)
        sim = cosine_similarity(base_emb_reshaped, mask_emb)[0][0]
        contrib = round(1 - sim, 4)
        level = "高" if contrib >= 0.1 else "中" if contrib >= 0.05 else "低"

        result[word] = {
            "mask后相似度": round(sim, 4),
            "贡献度差值": contrib,
            "贡献度等级": level
        }

    # 排序成表格
    df = pd.DataFrame.from_dict(result, orient="index")
    df = df.sort_values("贡献度差值", ascending=False)
    return df