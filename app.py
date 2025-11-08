import streamlit as st
import sys
import os

# 设置页面配置
st.set_page_config(page_title="AI教学助手", page_icon="🤖")

st.title("🤖 AI智能教学助手")
st.write("中等复杂度测试版本")

# 测试所有依赖导入
dependencies = {
    'streamlit': 'st',
    'pandas': 'pd', 
    'numpy': 'np',
    'networkx': 'nx',
    'sklearn': 'sklearn',
    'matplotlib': 'plt',
    'seaborn': 'sns'
}

st.write("### 📦 依赖导入测试:")
all_success = True

for lib_name, import_name in dependencies.items():
    try:
        if lib_name == 'sklearn':
            import sklearn
            st.success(f"✅ {lib_name} 导入成功")
        elif lib_name == 'streamlit':
            st.success(f"✅ {lib_name} 导入成功")
        else:
            exec(f"import {import_name}")
            st.success(f"✅ {lib_name} 导入成功")
    except ImportError as e:
        st.error(f"❌ {lib_name} 导入失败: {e}")
        all_success = False

if all_success:
    st.success("🎉 所有依赖导入成功！")
    
    # 测试基本功能
    st.write("### 🧪 功能测试:")
    
    if st.button("测试数据处理"):
        import pandas as pd
        import numpy as np
        
        # 创建测试数据
        data = pd.DataFrame({
            'A': np.random.rand(5),
            'B': np.random.rand(5)
        })
        
        st.write("生成的测试数据:")
        st.dataframe(data)
        st.success("✅ 数据处理功能正常！")
    
    if st.button("测试网络图"):
        import networkx as nx
        import matplotlib.pyplot as plt
        
        # 创建简单网络
        G = nx.Graph()
        G.add_edges_from([('A', 'B'), ('B', 'C'), ('C', 'D'), ('D', 'A')])
        
        st.write(f"网络图创建成功！")
        st.write(f"- 节点数: {G.number_of_nodes()}")
        st.write(f"- 边数: {G.number_of_edges()}")
        st.success("✅ NetworkX 功能正常！")

# 显示系统信息
st.write("---")
st.write("### 🔧 系统信息:")
st.write(f"Python版本: {sys.version}")
st.write(f"当前工作目录: {os.getcwd()}")
st.write(f"当前目录文件:")
try:
    files = os.listdir('.')
    for file in files:
        st.write(f"- {file}")
except Exception as e:
    st.error(f"无法读取目录: {e}")
