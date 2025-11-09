from typing import Dict, List
import sys
import os

# 导入各个模块
from data_loader import load_all_data
from keyword_extractor import KeywordExtractor
from knowledge_analyzer import KnowledgeAnalyzer
from literacy_analyzer import LiteracyAnalyzer
from your_subdirectory.knowledge_graph import KnowledgeGraphBuilder

# 全局变量
LOADED_DATA = None
KEYWORD_EXTRACTOR = None
KNOWLEDGE_ANALYZER = None
LITERACY_ANALYZER = None
GRAPH_BUILDER = None


def initialize_system():
    """初始化系统"""
    global LOADED_DATA, KEYWORD_EXTRACTOR, KNOWLEDGE_ANALYZER, LITERACY_ANALYZER, GRAPH_BUILDER

    # 加载数据
    LOADED_DATA = load_all_data()

    # 初始化各个组件
    KEYWORD_EXTRACTOR = KeywordExtractor(LOADED_DATA['keyword_mapping'])
    KNOWLEDGE_ANALYZER = KnowledgeAnalyzer(
        LOADED_DATA['weight_df'],
        LOADED_DATA['teaching_corpus'],
        LOADED_DATA['keyword_mapping'],
        LOADED_DATA['weight_mapping']
    )
    LITERACY_ANALYZER = LiteracyAnalyzer(LOADED_DATA['weight_mapping'])
    GRAPH_BUILDER = KnowledgeGraphBuilder(LOADED_DATA['knowledge_graph'])

    print("✅ 系统初始化完成")


def generate_teaching_resource(code_snippet: str) -> Dict:
    """生成教学资源"""
    if not LOADED_DATA:
        initialize_system()

    try:
        # 1. 提取关键词
        keywords = KEYWORD_EXTRACTOR.extract_from_code(code_snippet)

        if not keywords:
            return {
                "analyzed_keywords": [],
                "knowledge_importance": KNOWLEDGE_ANALYZER._empty_result(),
                "literacy_analysis": LITERACY_ANALYZER._empty_result(),
                "knowledge_graph": {"nodes": [], "edges": [], "paths": []},
                "original_code": code_snippet,
                "error": "未提取到有效关键词"
            }

        # 2. 分析知识重要性
        knowledge_importance = KNOWLEDGE_ANALYZER.analyze_knowledge_importance(keywords)

        # 3. 分析素养能力
        literacy_analysis = LITERACY_ANALYZER.analyze_literacy(keywords, LOADED_DATA['keyword_mapping'])

        # 4. 构建知识图谱
        enhanced_graph = GRAPH_BUILDER.enhance_with_keywords(keywords, LOADED_DATA['teaching_corpus'])
        graph_data = GRAPH_BUILDER.visualize_knowledge_paths(keywords[0] if keywords else "")

        # 5. 组装结果
        result = {
            "analyzed_keywords": keywords,
            "knowledge_importance": knowledge_importance,
            "literacy_analysis": literacy_analysis,
            "knowledge_graph": graph_data,
            "original_code": code_snippet,
            "summary": generate_summary(keywords, knowledge_importance, literacy_analysis)
        }

        return result

    except Exception as e:
        return {
            "analyzed_keywords": [],
            "knowledge_importance": KNOWLEDGE_ANALYZER._empty_result() if KNOWLEDGE_ANALYZER else {},
            "literacy_analysis": LITERACY_ANALYZER._empty_result() if LITERACY_ANALYZER else {},
            "knowledge_graph": {"nodes": [], "edges": [], "paths": []},
            "original_code": code_snippet,
            "error": f"分析过程中出现错误: {str(e)}"
        }


def generate_summary(keywords: List[str], knowledge_importance: Dict, literacy_analysis: Dict) -> str:
    """生成分析摘要"""
    summary_parts = []

    summary_parts.append(f"从代码中提取了 {len(keywords)} 个关键词")

    if knowledge_importance.get('total_analyzed', 0) > 0:
        important_count = len(knowledge_importance.get('important_knowledge', []))
        summary_parts.append(f"识别出 {important_count} 个重点知识点")

    if literacy_analysis.get('top_dimension', {}).get('name') != '无':
        top_dim = literacy_analysis['top_dimension']
        summary_parts.append(f"主要能力维度：{top_dim['name']}")

    return "\n".join(summary_parts)


# 测试函数
if __name__ == "__main__":
    # 初始化系统
    initialize_system()

    # 测试代码
    test_code = """
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# 加载数据
data = pd.read_csv('data.csv')
X = data.drop('target', axis=1)
y = data['target']

# 分割数据
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# 训练模型
model = RandomForestClassifier()
model.fit(X_train, y_train)

# 预测和评估
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy}")
"""

    # 生成教学资源
    result = generate_teaching_resource(test_code)

    # 打印结果
    print("=" * 50)
    print("分析结果：")
    print("=" * 50)
    print(f"关键词：{result['analyzed_keywords']}")
    print(f"\n摘要：\n{result['summary']}")


