import streamlit as st
import sys
import os
import pandas as pd
import networkx as nx
from typing import Dict, List, Any
import matplotlib.pyplot as plt
import seaborn as sns

# 确保工作目录正确
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

from main import generate_teaching_resource, initialize_system

# 页面配置
st.set_page_config(
    page_title="AI教学助手",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.8rem;
        color: #2ca02c;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #e0e0e0;
        padding-bottom: 0.5rem;
    }
    .subsection-header {
        font-size: 1.3rem;
        color: #ff7f0e;
        margin-top: 1.5rem;
        margin-bottom: 0.8rem;
    }
    .keyword-chip {
        display: inline-block;
        background-color: #e3f2fd;
        color: #1976d2;
        padding: 0.3rem 0.8rem;
        margin: 0.2rem;
        border-radius: 1rem;
        font-size: 0.9rem;
        font-weight: 500;
        border: 1px solid #bbdefb;
    }
    .importance-high {
        color: #d32f2f;
        font-weight: bold;
        background-color: #ffebee;
        padding: 0.2rem 0.5rem;
        border-radius: 0.3rem;
    }
    .importance-medium {
        color: #f57c00;
        font-weight: bold;
        background-color: #fff3e0;
        padding: 0.2rem 0.5rem;
        border-radius: 0.3rem;
    }
    .importance-low {
        color: #388e3c;
        background-color: #e8f5e8;
        padding: 0.2rem 0.5rem;
        border-radius: 0.3rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #007bff;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


# 初始化系统
@st.cache_resource
def init_system():
    """初始化系统（缓存）"""
    try:
        initialize_system()
        return True
    except Exception as e:
        st.error(f"系统初始化失败: {e}")
        return False


def create_keyword_length_chart(keywords):
    """创建关键词长度分布图"""
    if not keywords:
        return None

    lengths = [len(kw) for kw in keywords]
    length_counts = {}
    for length in lengths:
        length_counts[length] = length_counts.get(length, 0) + 1

    # 创建简单的条形图数据
    chart_data = {
        '关键词长度': list(length_counts.keys()),
        '数量': list(length_counts.values())
    }

    return chart_data


def create_dimension_scores_chart(dimension_scores):
    """创建维度得分图表"""
    if not dimension_scores:
        return None

    # 排序数据
    sorted_scores = sorted(dimension_scores.items(), key=lambda x: x[1], reverse=True)

    chart_data = {
        '维度': [item[0] for item in sorted_scores],
        '得分': [item[1] for item in sorted_scores]
    }

    return chart_data


def display_analysis_result(result):
    """显示完整的分析结果"""
    if not result:
        st.error("❌ 没有分析结果")
        return

    # 分析概览
    st.markdown("---")
    st.markdown('<h2 class="section-header">📊 分析概览</h2>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            "提取关键词",
            len(result.get('analyzed_keywords', [])),
            delta="✅" if result.get('analyzed_keywords') else "❌"
        )
    with col2:
        knowledge_count = result.get('knowledge_importance', {}).get('total_analyzed', 0)
        st.metric(
            "知识点数量",
            knowledge_count,
            delta="✅" if knowledge_count > 0 else "❌"
        )
    with col3:
        top_dim = result.get('literacy_analysis', {}).get('top_dimension', {}).get('name', '无')
        st.metric("主要能力维度", top_dim)
    with col4:
        has_error = 'error' in result and result['error']
        st.metric(
            "分析状态",
            "❌ 失败" if has_error else "✅ 成功",
            delta="有错误" if has_error else "无错误"
        )

    # 错误信息
    if 'error' in result and result['error']:
        st.markdown(f'<div class="error-box">❌ 错误信息: {result["error"]}</div>', unsafe_allow_html=True)

    # 分析摘要
    if result.get('summary'):
        st.markdown('<div class="success-box">📋 分析摘要<br>{}</div>'.format(result['summary'].replace('\n', '<br>')),
                    unsafe_allow_html=True)

    # 关键词分析
    st.markdown("---")
    st.markdown('<h2 class="section-header">🔍 关键词分析</h2>', unsafe_allow_html=True)

    keywords = result.get('analyzed_keywords', [])
    if keywords:
        # 关键词统计
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown('<h3 class="subsection-header">提取的关键词</h3>', unsafe_allow_html=True)

            # 关键词云显示
            keyword_text = " ".join([f"<span class='keyword-chip'>{kw}</span>" for kw in keywords])
            st.markdown(keyword_text, unsafe_allow_html=True)

            # 关键词表格
            keywords_df = pd.DataFrame({
                '序号': range(1, len(keywords) + 1),
                '关键词': keywords,
                '长度': [len(kw) for kw in keywords]
            })
            st.dataframe(keywords_df, use_container_width=True)

        with col2:
            st.markdown('<h3 class="subsection-header">关键词统计</h3>', unsafe_allow_html=True)

            # 关键词长度分布
            chart_data = create_keyword_length_chart(keywords)
            if chart_data:
                st.write("**关键词长度分布:**")
                chart_df = pd.DataFrame(chart_data)
                st.bar_chart(chart_df.set_index('关键词长度'))

            # 基本统计
            st.write("**基本统计:**")
            lengths = [len(kw) for kw in keywords]
            st.write(f"- 总数: {len(keywords)}")
            st.write(f"- 平均长度: {sum(lengths) / len(lengths):.1f}")
            st.write(f"- 最短: {min(lengths)}")
            st.write(f"- 最长: {max(lengths)}")
    else:
        st.markdown('<div class="warning-box">⚠️ 没有提取到关键词</div>', unsafe_allow_html=True)

    # 知识重要性分析
    st.markdown("---")
    st.markdown('<h2 class="section-header">📊 知识重要性分析</h2>', unsafe_allow_html=True)

    importance = result.get('knowledge_importance', {})
    if importance and importance.get('total_analyzed', 0) > 0:
        # 权重汇总
        if importance.get('weight_summary'):
            summary = importance['weight_summary']
            if summary.get('count', 0) > 0:
                st.markdown('<h3 class="subsection-header">权重汇总</h3>', unsafe_allow_html=True)

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("分析指标数", summary['count'])
                with col2:
                    st.metric("总权重", f"{summary['total_weight']:.4f}")
                with col3:
                    st.metric("涉及指标", len(summary['indicators']))

                if summary['indicators']:
                    with st.expander("📌 查看涉及的具体指标"):
                        for indicator in summary['indicators']:
                            st.write(f"• {indicator}")

        # 重点知识
        if importance.get('important_knowledge'):
            st.markdown('<h3 class="subsection-header">🎯 重点学习内容</h3>', unsafe_allow_html=True)

            for i, knowledge in enumerate(importance['important_knowledge'][:5], 1):
                with st.expander(f"{i}. {knowledge['keyword']} ({knowledge['knowledge_domain']})"):
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.write(knowledge['description'])
                        if 'indicator_name' in knowledge:
                            st.write(f"**相关指标:** {knowledge['indicator_name']}")
                    with col2:
                        importance_class = {
                            '高': 'importance-high',
                            '中高': 'importance-medium',
                            '中': 'importance-low',
                            '低': 'importance-low'
                        }.get(knowledge['importance'], 'importance-low')

                        st.markdown(
                            f'<p class="{importance_class}">{knowledge["importance"]}</p>',
                            unsafe_allow_html=True
                        )
                        st.write(f"权重: {knowledge['weight_score']:.4f}")

        # 次要知识
        if importance.get('secondary_knowledge'):
            st.markdown('<h3 class="subsection-header">📚 次要学习内容</h3>', unsafe_allow_html=True)

            for knowledge in importance['secondary_knowledge'][:3]:
                with st.expander(f"📖 {knowledge['keyword']}"):
                    st.write(knowledge['description'])
                    st.write(f"**重要性:** {knowledge['importance']}")

        # 学习建议
        if importance.get('learning_suggestions'):
            st.markdown('<h3 class="subsection-header">💡 学习建议</h3>', unsafe_allow_html=True)
            for suggestion in importance['learning_suggestions']:
                st.write(suggestion)
    else:
        st.markdown('<div class="warning-box">⚠️ 知识重要性分析为空</div>', unsafe_allow_html=True)

    # 素养能力分析
    st.markdown("---")
    st.markdown('<h2 class="section-header">🧠 素养能力分析</h2>', unsafe_allow_html=True)

    literacy = result.get('literacy_analysis', {})
    if literacy and literacy.get('top_dimension', {}).get('name') != '无':
        # 主要能力维度
        top_dim = literacy['top_dimension']
        st.markdown('<h3 class="subsection-header">🎯 主要能力维度</h3>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.metric("能力维度", top_dim['name'])
        with col2:
            st.metric("综合得分", f"{top_dim['score']:.4f}")

        # 各维度得分
        if literacy.get('dimension_scores'):
            st.markdown('<h3 class="subsection-header">📊 各维度得分</h3>', unsafe_allow_html=True)

            # 创建DataFrame
            scores_df = pd.DataFrame(
                list(literacy['dimension_scores'].items()),
                columns=['维度', '得分']
            )
            scores_df = scores_df.sort_values('得分', ascending=False)

            # 显示表格
            st.dataframe(scores_df, use_container_width=True)

            # 显示柱状图
            st.write("**各维度得分对比:**")
            st.bar_chart(scores_df.set_index('维度'))

        # 分析总结
        if literacy.get('analysis_summary'):
            st.markdown('<h3 class="subsection-header">📝 分析总结</h3>', unsafe_allow_html=True)
            st.info(literacy['analysis_summary'])
    else:
        st.markdown('<div class="warning-box">⚠️ 素养能力分析为空</div>', unsafe_allow_html=True)

    # 知识图谱
    st.markdown("---")
    st.markdown('<h2 class="section-header">🕸️ 知识图谱</h2>', unsafe_allow_html=True)

    graph = result.get('knowledge_graph', {})
    if graph.get('nodes'):
        st.markdown('<h3 class="subsection-header">🔗 知识关联网络</h3>', unsafe_allow_html=True)

        # 显示节点信息
        nodes_df = pd.DataFrame(graph['nodes'])
        if not nodes_df.empty:
            st.write(f"**知识图谱包含 {len(nodes_df)} 个节点，{len(graph.get('edges', []))} 条边**")

            # 检查可用的列
            available_columns = nodes_df.columns.tolist()
            st.write(f"**节点数据列:** {', '.join(available_columns)}")

            # 节点类型分布（如果有type列）
            if 'type' in nodes_df.columns:
                type_counts = nodes_df['type'].value_counts()
                st.write("**节点类型分布:**")
                type_df = pd.DataFrame({
                    '类型': type_counts.index,
                    '数量': type_counts.values
                })
                st.bar_chart(type_df.set_index('类型'))

            # 显示节点表格（只显示存在的列）
            display_columns = []
            if 'id' in nodes_df.columns:
                display_columns.append('id')
            if 'type' in nodes_df.columns:
                display_columns.append('type')
            if 'domains' in nodes_df.columns:
                display_columns.append('domains')

            # 如果没有标准列，显示前几列
            if not display_columns:
                display_columns = available_columns[:3]  # 显示前3列

            st.write("**节点信息:**")
            st.dataframe(nodes_df[display_columns], use_container_width=True)

        # 显示边信息
        if graph.get('edges'):
            edges_df = pd.DataFrame(graph['edges'])
            if not edges_df.empty:
                st.write("**关系连接:**")
                # 检查边数据的列
                edge_columns = edges_df.columns.tolist()
                st.write(f"**边数据列:** {', '.join(edge_columns)}")
                st.dataframe(edges_df, use_container_width=True)

        # 显示知识路径
        if graph.get('paths'):
            st.markdown('<h3 class="subsection-header">🛤️ 知识路径</h3>', unsafe_allow_html=True)
            for i, path in enumerate(graph['paths'][:3], 1):
                st.write(f"**路径 {i}:** {' → '.join(path)}")
    else:
        st.markdown('<div class="warning-box">⚠️ 知识图谱为空</div>', unsafe_allow_html=True)

    # 原始代码
    st.markdown("---")
    with st.expander("📄 查看原始代码"):
        st.code(result.get('original_code', ''), language='python')


# 侧边栏
st.sidebar.title("🤖 AI教学助手")
st.sidebar.markdown("---")

# 系统状态
system_ready = init_system()

if system_ready:
    st.sidebar.success("✅ 系统已就绪")
else:
    st.sidebar.error("❌ 系统初始化失败")
    st.stop()

st.sidebar.markdown("### 📚 功能说明")
st.sidebar.info("""
本系统基于专家知识库和教学语料库，为Python代码提供个性化的教学资源分析。

**主要功能：**
- 🔍 关键词智能提取
- 📊 知识重要性分析
- 🧠 素养能力评估
- 🕸️ 知识图谱可视化
""")

# 主界面
st.markdown('<h1 class="main-header">🤖 AI智能教学助手</h1>', unsafe_allow_html=True)
st.markdown("---")

# 代码输入区域
st.markdown('<h2 class="section-header">📝 代码输入</h2>', unsafe_allow_html=True)

input_method = st.radio("选择输入方式:", ["📝 文本输入", "📁 文件上传"], horizontal=True)

if input_method == "📝 文本输入":
    user_code = st.text_area(
        "请输入Python代码:",
        height=300,
        placeholder="在这里输入您的Python代码...",
        help="支持所有Python语法，系统会自动提取关键词并分析"
    )
else:
    uploaded_file = st.file_uploader(
        "上传Python文件 (.py)",
        type=['py'],
        help="上传.py文件，系统会自动读取内容"
    )
    if uploaded_file is not None:
        user_code = uploaded_file.read().decode('utf-8')
        st.code(user_code, language='python')
    else:
        user_code = ""

# 分析按钮
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    analyze_button = st.button(
        "🔍 开始分析",
        type="primary",
        use_container_width=True,
        help="点击开始分析代码并生成教学资源"
    )

# 分析结果
if analyze_button or 'analysis_result' in st.session_state:
    if not user_code.strip():
        st.error("⚠️ 请输入或上传代码后再进行分析！")
    else:
        with st.spinner("🔄 正在分析代码，生成教学资源..."):
            try:
                # 生成教学资源
                result = generate_teaching_resource(user_code)

                # 保存到会话状态
                st.session_state.analysis_result = result
                st.session_state.analyzed = True

                # 显示成功消息
                st.success("✅ 分析完成！")

                # 显示完整分析结果
                display_analysis_result(result)

            except Exception as e:
                st.error(f"❌ 分析过程中出现错误: {e}")
                st.exception(e)

# 显示已保存的分析结果
elif 'analyzed' in st.session_state and st.session_state.analyzed:
    result = st.session_state.analysis_result
    display_analysis_result(result)

    # 重新分析按钮
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 重新分析", use_container_width=True):
            st.session_state.analyzed = False
            st.rerun()

# 页脚
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; padding: 20px;'>
    <p>🤖 AI教学助手 © 2024 | 基于专家知识库的智能教学系统</p>
    <p>帮助理解代码，提升学习效率 📚</p>
</div>
""", unsafe_allow_html=True)
