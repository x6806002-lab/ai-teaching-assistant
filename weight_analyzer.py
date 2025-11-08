import pandas as pd
from collections import defaultdict


def load_weight_system(csv_path: str):
    """加载素养权重体系，返回一个方便查询的字典"""
    try:
        df = pd.read_csv(csv_path, encoding='utf-8-sig')
        # 创建一个从指标编码到权重的映射
        weight_map = pd.Series(df['绝对权重'].values, index=df['指标编码']).to_dict()
        # 创建一个从指标编码到其所属一级指标的映射
        parent_map = pd.Series(df['层级'].values, index=df['指标编码']).to_dict()
        return weight_map, parent_map
    except Exception as e:
        print(f"加载权重体系失败: {e}")
        return {}, {}


def create_keyword_to_indicator_mapping(corpus: list):
    """
    根据语料库创建一个从关键词到素养指标的映射。
    这是一个关键步骤，我们假设'知识领域'可以映射到'一级指标'。
    """
    # 这是一个简化的映射，你可以根据你的研究进行精细化调整
    domain_to_indicator = {
        "Numpy基础": "C11", "Numpy统计": "C11", "Numpy数组创建": "C11", "Numpy随机数": "C11", "Numpy形状操作": "C11",
        "Numpy矩阵操作": "C11", "Numpy数学运算": "C11",
        "pandas与CSV": "C11", "pandas与Excel": "C11", "pandas与数据库": "C11", "DataFrame属性": "C11",
        "DataFrame索引": "C11", "pandas时间序列": "C11", "pandas日期时间": "C11", "pandas分组聚合": "C11",
        "pandas透视表": "C11", "pandas合并连接": "C11", "pandas去重": "C11", "pandas缺失值处理": "C11",
        "pandas独热编码": "C11", "pandas分位数": "C11",
        "sklearn数据集": "C11", "sklearn数据划分": "C11", "sklearn预处理": "C11", "sklearn评估": "C11",
        "分类模型评估指标": "C11", "回归模型评估指标": "C11",
        "sklearn聚类": "C12", "sklearn支持向量机": "C12", "sklearn逻辑回归": "C12", "sklearn线性回归": "C12",
        "sklearnK近邻": "C12", "sklearn朴素贝叶斯": "C12", "sklearn决策树": "C12", "sklearn随机森林": "C12",
        "sklearn梯度提升": "C12", "sklearn集成学习": "C12", "sklearn降维": "C12", "sklearn模型选择": "C12",
        "Matplotlib绘图": "C14", "seaborn绘图": "C14", "pyecharts绘图": "C14",
        "构建和训练深度学习模型": "C12", "深度学习优化器": "C12", "深度学习层": "C12", "深度学习正则化": "C12",
        "深度学习回调函数": "C12",
        "自然语言处理": "C12", "计算机视觉": "C12", "语音识别": "C12", "推荐系统": "C12", "强化学习": "C12",
        "数据隐私保护": "C15", "模型可解释性分析": "C15",
        "Python基础数据类型": "C21", "Python列表操作": "C22", "Python字典操作": "C22", "Python集合操作": "C22",
        "Python字符串操作": "C22", "Python条件语句": "C21", "Python循环语句": "C21", "Python函数定义": "C22",
        "Python文件操作": "C23", "Python异常处理": "C24", "Python模块导入": "C23",
        "GUI设计": "C25",
        "知识图谱": "C31", "关联规则挖掘": "C31", "频繁模式挖掘": "C31", "文本挖掘": "C31", "图像挖掘": "C31",
        "搜索算法": "C31", "知识表示": "C31", "智能体": "C31",
        "数据库操作": "C23", "NoSQL数据库": "C23", "数据存储": "C13", "大数据处理": "C13", "云计算服务": "C13",
        "容器化技术": "C13",
        "数据可视化": "C14", "报表生成": "C25", "自动化测试": "C24", "Web自动化": "C23", "API测试": "C23",
        "版本控制": "C23", "项目管理": "C25",
        "加密算法": "C15", "网络安全": "C15",
    }

    mapping = {}
    for item in corpus:
        domain = item.get('知识领域')
        keyword = item.get('关键词')
        if domain and keyword and domain in domain_to_indicator:
            mapping[keyword] = domain_to_indicator[domain]
    return mapping


def analyze_literacy(keywords: list, keyword_to_indicator_map: dict, weight_map: dict, parent_map: dict):
    """
    根据关键词分析其对应的AI素养权重。
    """
    # 按一级指标（B1, B2...）累加权重
    b_weights = defaultdict(float)
    # 记录匹配到的二级指标
    matched_c_indicators = set()

    for keyword in keywords:
        indicator = keyword_to_indicator_map.get(keyword)
        if indicator and indicator in weight_map:
            weight = weight_map[indicator]
            parent = parent_map.get(indicator)
            if parent:
                b_weights[parent] += weight
                matched_c_indicators.add(indicator)

    if not b_weights:
        return {"error": "未能将代码中的关键词与素养指标进行匹配。"}

    # 找到权重最高的一级指标
    top_b_indicator = max(b_weights.items(), key=lambda item: item[1])

    analysis_result = {
        "top_dimension": {
            "name": top_b_indicator[0],
            "score": round(top_b_indicator[1], 4)
        },
        "dimension_scores": {k: round(v, 4) for k, v in b_weights.items()},
        "matched_indicators": sorted(list(matched_c_indicators)),
        "analysis_summary": f"根据分析，您输入的代码主要体现了 '{top_b_indicator[0]}' 维度的素养，综合得分为 {round(top_b_indicator[1], 4)}。"
    }
    return analysis_result
