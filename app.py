import streamlit as st

st.set_page_config(page_title="AI教学助手", page_icon="🤖")

st.title("🤖 AI智能教学助手")
st.write("🧪 依赖测试阶段")

# 测试所有核心依赖
st.write("### 📦 依赖导入测试:")

dependencies = {  # ✅ 改为字典
    "pandas": "pd",
    "numpy": "np",
    "networkx": "nx",
    "sklearn": "sklearn",
    "matplotlib": "plt",
    "seaborn": "sns"
}

all_success = True

for lib_name, import_name in dependencies.items():  # ✅ 字典可以用.items()
    try:
        if lib_name == 'sklearn':
            import sklearn
            st.success(f"✅ {lib_name} 导入成功")
        else:
            exec(f"import {import_name}")
            st.success(f"✅ {lib_name} 导入成功")
    except ImportError as e:
        st.error(f"❌ {lib_name} 导入失败: {e}")
        all_success = False

if all_success:
    st.success("🎉 所有核心依赖导入成功！可以进入下一阶段。")
    if st.button("进入下一阶段测试"):
        st.info("下一步将测试数据文件和业务逻辑模块。")
else:
    st.error("⚠️ 部分依赖导入失败，需要检查 requirements.txt")
