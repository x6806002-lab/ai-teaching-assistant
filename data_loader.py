import csv
import pandas as pd
import networkx as nx
import os
from typing import Dict, List, Tuple, Optional


class DataLoader:
    """统一数据加载器"""

    def __init__(self):
        self.data = {}
        # 获取脚本所在目录作为基准目录
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"📁 数据加载器基准目录: {self.base_dir}")

    def _get_file_path(self, filename: str) -> str:
        """获取文件的完整路径"""
        # 在脚本所在目录中查找文件
        file_path = os.path.join(self.base_dir, filename)
        print(f"🔍 查找文件: {file_path}")
        return file_path

    def load_csv_with_encoding(self, file_path: str, encodings: List[str] = None) -> List[Dict]:
        """带编码检测的CSV加载"""
        if encodings is None:
            encodings = ['utf-8-sig', 'gbk', 'utf-8']

        # 获取完整路径
        full_path = self._get_file_path(file_path)

        # 检查文件是否存在
        if not os.path.exists(full_path):
            print(f"❌ 文件不存在: {full_path}")
            return []

        print(f"✅ 找到文件: {full_path}")

        for encoding in encodings:
            try:
                with open(full_path, 'r', encoding=encoding) as f:
                    reader = csv.DictReader(f)
                    data = list(reader)
                    print(f"✅ {file_path} 加载成功 ({encoding}): {len(data)} 条记录")
                    return data
            except UnicodeDecodeError:
                continue
            except Exception as e:
                print(f"❌ {file_path} 加载失败: {e}")
                return []

        print(f"❌ {file_path} 所有编码尝试失败")
        return []

    def load_keyword_mapping(self, file_path: str = 'keyword_mapping.csv') -> Dict[str, Dict]:
        """加载关键词映射"""
        data = self.load_csv_with_encoding(file_path)
        mapping = {}

        for row in data:
            keyword = row['关键词'].strip()
            mapping[keyword] = {
                'indicator_code': row['指标编码'],
                'weight': float(row['权重']),
                'parent_indicator': row['父级指标']
            }

        print(f"✅ 关键词映射加载: {len(mapping)} 个映射")
        return mapping

    def load_weight_data(self, file_path: str = 'weight.csv') -> pd.DataFrame:
        """加载权重数据"""
        try:
            full_path = self._get_file_path(file_path)
            if not os.path.exists(full_path):
                print(f"❌ 权重文件不存在: {full_path}")
                return pd.DataFrame()

            df = pd.read_csv(full_path, encoding='utf-8-sig')
            # 清理列名
            df.columns = df.columns.str.strip()
            print(f"✅ 权重数据加载: {len(df)} 条记录")
            return df
        except Exception as e:
            print(f"❌ 权重数据加载失败: {e}")
            return pd.DataFrame()

    def load_teaching_corpus(self, file_path: str = 'Teaching_corpus.csv') -> List[Dict]:
        """加载教学语料库"""
        data = self.load_csv_with_encoding(file_path)
        corpus = []

        for row in data:
            # 处理关键词（可能包含多个关键词，用逗号分隔）
            keywords = [k.strip() for k in row['关键词'].split(',')]

            corpus.append({
                'knowledge_domain': row['知识领域'].strip(),
                'keywords': keywords,
                'description': row['详细描述'].strip()
            })

        print(f"✅ 教学语料库加载: {len(corpus)} 条记录")
        return corpus

    def load_expert_knowledge(self, file_path: str = 'expert_knowledge.csv') -> nx.DiGraph:
        """加载专家知识库并构建知识图谱"""
        data = self.load_csv_with_encoding(file_path)
        G = nx.DiGraph()

        for row in data:
            head = row['head'].strip()
            tail = row['tail'].strip()
            relation = row['relation'].strip()

            # 添加节点
            if head not in G:
                G.add_node(head, type='concept')
            if tail not in G:
                G.add_node(tail, type='concept')

            # 添加边
            G.add_edge(head, tail, relation=relation)

        print(f"✅ 知识图谱构建: {G.number_of_nodes()} 节点, {G.number_of_edges()} 边")
        return G

    def load_all_data(self) -> Dict:
        """加载所有数据"""
        print("🚀 开始加载所有数据文件...")
        print(f"📁 当前工作目录: {os.getcwd()}")
        print(f"📁 脚本所在目录: {self.base_dir}")

        # 列出当前目录的文件
        print("📋 当前目录文件列表:")
        for file in os.listdir(self.base_dir):
            if file.endswith('.csv'):
                print(f"   - {file}")

        self.data = {
            'keyword_mapping': self.load_keyword_mapping(),
            'weight_df': self.load_weight_data(),
            'teaching_corpus': self.load_teaching_corpus(),
            'knowledge_graph': self.load_expert_knowledge()
        }

        # 构建权重映射字典
        weight_mapping = {}
        if not self.data['weight_df'].empty:
            for _, row in self.data['weight_df'].iterrows():
                weight_mapping[row['指标编码']] = {
                    'absolute_weight': row['绝对权重'],
                    'relative_weight': row['相对权重'],
                    'name': row['指标名称'],
                    'level': row['层级']
                }

        self.data['weight_mapping'] = weight_mapping

        print("✅ 所有数据加载完成！")
        return self.data


# 全局数据加载器实例
data_loader = DataLoader()


def load_all_data():
    """全局数据加载函数"""
    return data_loader.load_all_data()
