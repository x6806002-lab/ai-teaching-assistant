import networkx as nx
from typing import Dict, List, Tuple


class KnowledgeGraphBuilder:
    """知识图谱构建器"""

    def __init__(self, expert_knowledge_graph: nx.DiGraph):
        self.graph = expert_knowledge_graph
        self.enhanced_graph = None

    def enhance_with_keywords(self, keywords: List[str], teaching_corpus: List[Dict]) -> nx.DiGraph:
        """基于关键词增强知识图谱"""
        # 创建图的副本
        enhanced = self.graph.copy()

        # 添加关键词节点和边
        for keyword in keywords:
            # 查找相关的教学内容
            related_corpus = []
            for item in teaching_corpus:
                if keyword in item['keywords']:
                    related_corpus.append(item)

            # 添加关键词节点
            if keyword not in enhanced:
                enhanced.add_node(keyword,
                                  type='keyword',
                                  descriptions=[item['description'] for item in related_corpus],
                                  domains=list(set([item['knowledge_domain'] for item in related_corpus])))

            # 连接到相关知识领域
            for item in related_corpus:
                domain = item['knowledge_domain']
                if domain in enhanced:
                    enhanced.add_edge(keyword, domain, relation='belongs_to')

        self.enhanced_graph = enhanced
        return enhanced

    def get_related_knowledge(self, keyword: str, max_depth: int = 2) -> Dict:
        """获取相关知识"""
        if not self.enhanced_graph or keyword not in self.enhanced_graph:
            return {"nodes": [], "edges": [], "paths": []}

        # 获取子图
        subgraph = nx.ego_graph(self.enhanced_graph, keyword, radius=max_depth)

        # 提取节点和边
        nodes = []
        for node in subgraph.nodes():
            node_data = self.enhanced_graph.nodes[node]
            nodes.append({
                "id": node,
                "type": node_data.get('type', 'unknown'),
                "labels": node_data.get('labels', []),
                "descriptions": node_data.get('descriptions', []),
                "domains": node_data.get('domains', [])
            })

        edges = []
        for edge in subgraph.edges():
            edge_data = self.enhanced_graph.edges[edge]
            edges.append({
                "source": edge[0],
                "target": edge[1],
                "relation": edge_data.get('relation', 'related')
            })

        # 查找路径
        paths = []
        for target in subgraph.nodes():
            if target != keyword:
                try:
                    path = nx.shortest_path(self.enhanced_graph, keyword, target)
                    if len(path) > 1:
                        paths.append(path)
                except nx.NetworkXNoPath:
                    continue

        return {
            "nodes": nodes,
            "edges": edges,
            "paths": paths[:5]  # 限制路径数量
        }

    def visualize_knowledge_paths(self, keyword: str) -> Dict:
        """可视化知识路径"""
        related = self.get_related_knowledge(keyword)

        # 构建可视化数据
        visualization_data = {
            "nodes": [],
            "links": []
        }

        # 添加中心节点
        visualization_data["nodes"].append({
            "id": keyword,
            "label": keyword,
            "size": 30,
            "color": "#ff6b6b"
        })

        # 添加相关节点
        for node in related["nodes"]:
            if node["id"] != keyword:
                visualization_data["nodes"].append({
                    "id": node["id"],
                    "label": node["id"],
                    "size": 20,
                    "color": "#4ecdc4" if node["type"] == "keyword" else "#45b7d1"
                })

        # 添加连接
        for edge in related["edges"]:
            visualization_data["links"].append({
                "source": edge["source"],
                "target": edge["target"],
                "label": edge["relation"]
            })

        return visualization_data
