from typing import Dict, List, Tuple
import pandas as pd


class KnowledgeAnalyzer:
    """知识重要性分析器"""

    def __init__(self, weight_df: pd.DataFrame, teaching_corpus: List[Dict],
                 keyword_mapping: Dict[str, Dict], weight_mapping: Dict[str, Dict]):
        self.weight_df = weight_df
        self.teaching_corpus = teaching_corpus
        self.keyword_mapping = keyword_mapping
        self.weight_mapping = weight_mapping

        # 构建关键词到教学内容的索引
        self._build_corpus_index()

    def _build_corpus_index(self):
        """构建教学内容索引"""
        self.corpus_index = {}

        for item in self.teaching_corpus:
            for keyword in item['keywords']:
                if keyword not in self.corpus_index:
                    self.corpus_index[keyword] = []
                self.corpus_index[keyword].append(item)

    def analyze_knowledge_importance(self, keywords: List[str]) -> Dict:
        """分析知识重要性"""
        if not keywords:
            return self._empty_result()

        # 1. 匹配教学内容
        matched_knowledge = self._match_teaching_content(keywords)

        # 2. 计算权重分数
        knowledge_with_weights = self._calculate_weights(matched_knowledge)

        # 3. 分类和排序
        important_knowledge, secondary_knowledge = self._categorize_knowledge(knowledge_with_weights)

        # 4. 生成学习建议
        suggestions = self._generate_suggestions(important_knowledge, secondary_knowledge)

        # 5. 计算权重汇总
        weight_summary = self._calculate_weight_summary(keywords)

        return {
            "important_knowledge": important_knowledge,
            "secondary_knowledge": secondary_knowledge,
            "learning_suggestions": suggestions,
            "weight_summary": weight_summary,
            "total_analyzed": len(knowledge_with_weights)
        }

    def _match_teaching_content(self, keywords: List[str]) -> List[Dict]:
        """匹配教学内容"""
        matched = []

        for keyword in keywords:
            if keyword in self.corpus_index:
                corpus_items = self.corpus_index[keyword]

                for item in corpus_items:
                    matched.append({
                        'keyword': keyword,
                        'knowledge_domain': item['knowledge_domain'],
                        'description': item['description'],
                        'corpus_item': item
                    })
            else:
                # 未找到匹配的内容
                matched.append({
                    'keyword': keyword,
                    'knowledge_domain': '未知领域',
                    'description': f'暂无关于"{keyword}"的详细教学内容',
                    'corpus_item': None
                })

        return matched

    def _calculate_weights(self, knowledge_list: List[Dict]) -> List[Dict]:
        """计算权重分数"""
        for knowledge in knowledge_list:
            keyword = knowledge['keyword']

            # 获取指标编码
            indicator_code = self.keyword_mapping.get(keyword, {}).get('indicator_code')

            if indicator_code and indicator_code in self.weight_mapping:
                weight_info = self.weight_mapping[indicator_code]
                knowledge['weight_score'] = weight_info['absolute_weight']
                knowledge['indicator_name'] = weight_info['name']
                knowledge['indicator_level'] = weight_info['level']
            else:
                knowledge['weight_score'] = 0.1
                knowledge['indicator_name'] = '未分类'
                knowledge['indicator_level'] = '未知'

            # 确定重要性等级
            knowledge['importance'] = self._get_importance_level(knowledge['weight_score'])

        # 按权重排序
        knowledge_list.sort(key=lambda x: x['weight_score'], reverse=True)
        return knowledge_list

    def _get_importance_level(self, weight_score: float) -> str:
        """根据权重分数确定重要性等级"""
        if weight_score >= 0.08:
            return '高'
        elif weight_score >= 0.05:
            return '中高'
        elif weight_score >= 0.03:
            return '中'
        else:
            return '低'

    def _categorize_knowledge(self, knowledge_list: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """分类知识点"""
        important = [k for k in knowledge_list if k['importance'] in ['高', '中高']]
        secondary = [k for k in knowledge_list if k['importance'] in ['中', '低']]

        return important[:5], secondary[:5]  # 限制数量

    def _generate_suggestions(self, important: List[Dict], secondary: List[Dict]) -> List[str]:
        """生成学习建议"""
        suggestions = []

        if important:
            suggestions.append("🎯 **重点学习内容（按重要性排序）：**")
            for i, knowledge in enumerate(important[:3], 1):
                domain = knowledge['knowledge_domain']
                keyword = knowledge['keyword']
                desc = knowledge['description'][:100] + "..."

                suggestions.append(f"{i}. **{keyword}** ({domain})")
                suggestions.append(f"   {desc}")

                # 根据知识领域添加特定建议
                if 'Numpy' in domain:
                    suggestions.append("   💡 建议结合数组操作实例进行练习")
                elif 'pandas' in domain:
                    suggestions.append("   💡 建议使用真实数据集进行数据处理练习")
                elif 'sklearn' in domain:
                    suggestions.append("   💡 建议理解算法原理后再进行代码实现")
                elif 'Matplotlib' in domain:
                    suggestions.append("   💡 建议多练习不同类型的图表绘制")

        if secondary:
            suggestions.append("\n📚 **次要学习内容：**")
            for knowledge in secondary[:2]:
                suggestions.append(f"• **{knowledge['keyword']}**: 了解基本概念和使用方法")

        # 通用学习建议
        suggestions.append("\n💡 **通用学习建议：**")
        suggestions.append("• 循序渐进，先掌握重点内容再扩展到次要内容")
        suggestions.append("• 结合实际项目或数据集进行练习")
        suggestions.append("• 查阅官方文档获取更详细的信息")
        suggestions.append("• 参与开源项目或在线课程加深理解")

        return suggestions

    def _calculate_weight_summary(self, keywords: List[str]) -> Dict:
        """计算权重汇总"""
        total_weight = 0
        matched_indicators = []
        indicator_details = []

        for keyword in keywords:
            if keyword in self.keyword_mapping:
                indicator_code = self.keyword_mapping[keyword]['indicator_code']

                if indicator_code in self.weight_mapping:
                    weight_info = self.weight_mapping[indicator_code]
                    total_weight += weight_info['absolute_weight']
                    matched_indicators.append(indicator_code)
                    indicator_details.append(
                        f"{weight_info['name']}({weight_info['relative_weight']})"
                    )

        return {
            "count": len(matched_indicators),
            "total_weight": round(total_weight, 4),
            "indicators": indicator_details
        }

    def _empty_result(self) -> Dict:
        """返回空结果"""
        return {
            "important_knowledge": [],
            "secondary_knowledge": [],
            "learning_suggestions": ["未检测到有效的关键词，请检查代码内容"],
            "weight_summary": {"count": 0, "total_weight": 0, "indicators": []},
            "total_analyzed": 0
        }
