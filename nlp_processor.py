from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd


def find_relevant_text(query: str, corpus: list, top_n=1):
    """
    兼容旧版本的函数，在纯文本列表中查找。
    """
    if not corpus:
        return "暂无相关知识库内容。"

    vectorizer = TfidfVectorizer()
    try:
        tfidf_matrix = vectorizer.fit_transform([query] + corpus)
    except ValueError:
        return "暂无相关知识库内容。"

    cosine_similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

    if cosine_similarities.max() == 0:
        return "未在知识库中找到高度相关的内容。"

    related_docs_indices = cosine_similarities.argsort()[:-top_n - 1:-1]
    return corpus[related_docs_indices[0]]


def find_relevant_text_advanced(keyword: str, corpus: list):
    """增强版文本搜索，支持更精确的匹配"""
    if not corpus:
        return "未在知识库中找到高度相关的内容。"

    # 1. 精确匹配
    for item in corpus:
        if keyword.lower() == item['关键词'].lower().strip():
            return {
                "content": item['详细描述'],
                "match_type": "精确匹配",
                "knowledge_domain": item['知识领域'],
                "confidence": 1.0
            }

    # 2. 包含匹配（优先匹配包含关键词的词条）
    best_match = None
    best_score = 0

    for item in corpus:
        item_keyword = item['关键词'].lower().strip()

        # 检查关键词是否包含词条
        if keyword.lower() in item_keyword:
            score = len(keyword) / len(item_keyword)
            if score > best_score:
                best_score = score
                best_match = {
                    "content": item['详细描述'],
                    "match_type": "包含匹配",
                    "knowledge_domain": item['知识领域'],
                    "confidence": score,
                    "matched_keyword": item['关键词']
                }

        # 检查词条是否包含关键词
        elif item_keyword in keyword.lower():
            score = len(item_keyword) / len(keyword)
            if score > best_score:
                best_score = score
                best_match = {
                    "content": item['详细描述'],
                    "match_type": "被包含匹配",
                    "knowledge_domain": item['知识领域'],
                    "confidence": score,
                    "matched_keyword": item['关键词']
                }

    if best_match and best_score > 0.3:  # 降低阈值
        return best_match

    # 3. 知识领域匹配
    for item in corpus:
        if keyword.lower() in item['知识领域'].lower():
            return {
                "content": f"在'{item['知识领域']}'领域中找到了相关概念：{item['详细描述']}",
                "match_type": "领域匹配",
                "knowledge_domain": item['知识领域'],
                "confidence": 0.5
            }

    return {
        "content": "未在知识库中找到高度相关的内容。",
        "match_type": "无匹配",
        "knowledge_domain": "未知",
        "confidence": 0.0
    }
