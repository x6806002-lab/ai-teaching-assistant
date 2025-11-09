from typing import Dict, List, Tuple


class LiteracyAnalyzer:
    """素养能力分析器"""

    def __init__(self, weight_mapping: Dict[str, Dict]):
        self.weight_mapping = weight_mapping

    def analyze_literacy(self, keywords: List[str], keyword_mapping: Dict[str, Dict]) -> Dict:
        """分析素养能力"""
        if not keywords:
            return self._empty_result()

        # 1. 获取匹配的指标
        matched_indicators = self._get_matched_indicators(keywords, keyword_mapping)

        # 2. 计算维度得分
        dimension_scores = self._calculate_dimension_scores(matched_indicators)

        # 3. 找出主要维度
        top_dimension = self._get_top_dimension(dimension_scores)

        # 4. 生成分析总结
        analysis_summary = self._generate_analysis_summary(
            keywords, matched_indicators, dimension_scores, top_dimension
        )

        return {
            "top_dimension": top_dimension,
            "dimension_scores": dimension_scores,
            "matched_indicators": matched_indicators,
            "analysis_summary": analysis_summary,
            "detailed_analysis": self._generate_detailed_analysis(
                keywords, matched_indicators, self.weight_mapping
            )
        }

    def _get_matched_indicators(self, keywords: List[str], keyword_mapping: Dict[str, Dict]) -> List[str]:
        """获取匹配的指标编码"""
        indicators = []
        for keyword in keywords:
            if keyword in keyword_mapping:
                indicator = keyword_mapping[keyword]['indicator_code']
                if indicator not in indicators:
                    indicators.append(indicator)
        return indicators

    def _calculate_dimension_scores(self, matched_indicators: List[str]) -> Dict[str, float]:
        """计算各维度得分"""
        dimension_scores = {}

        for indicator in matched_indicators:
            if indicator in self.weight_mapping:
                weight_info = self.weight_mapping[indicator]
                level = weight_info['level']
                weight = weight_info['absolute_weight']

                if level not in dimension_scores:
                    dimension_scores[level] = 0
                dimension_scores[level] += weight

        return dimension_scores

    def _get_top_dimension(self, dimension_scores: Dict[str, float]) -> Dict:
        """获取最高分维度"""
        if not dimension_scores:
            return {"name": "无", "score": 0}

        top_level = max(dimension_scores.items(), key=lambda x: x[1])
        level_name = self._get_level_name(top_level[0])

        return {
            "name": level_name,
            "code": top_level[0],
            "score": round(top_level[1], 4)
        }

    def _get_level_name(self, level_code: str) -> str:
        """获取维度名称"""
        level_names = {
            'B1': '系统性认知',
            'B2': '构建式能力',
            'B3': '创造与思辨',
            'B4': '人本与责任',
            'C11': '数据与知识',
            'C12': '算法与模型',
            'C13': '算力与系统',
            'C14': '交叉与应用',
            'C15': '可信与安全',
            'C21': '问题抽象与定义',
            'C22': '分解与模块化',
            'C23': '工具选择与模型构建',
            'C24': '验证、评估与迭代',
            'C25': '结果解释与沟通'
        }
        return level_names.get(level_code, level_code)

    def _generate_analysis_summary(self, keywords: List[str], matched_indicators: List[str],
                                   dimension_scores: Dict[str, float], top_dimension: Dict) -> str:
        """生成分析总结"""
        summary_parts = []

        summary_parts.append(f"检测到 {len(keywords)} 个关键词，匹配 {len(matched_indicators)} 个能力指标")

        if top_dimension['name'] != '无':
            summary_parts.append(f"主要能力维度：{top_dimension['name']}（得分：{top_dimension['score']}）")

        if dimension_scores:
            summary_parts.append("各维度得分情况：")
            for level, score in sorted(dimension_scores.items(), key=lambda x: x[1], reverse=True):
                level_name = self._get_level_name(level)
                summary_parts.append(f"- {level_name}：{score:.4f}")

        return "\n".join(summary_parts)

    def _generate_detailed_analysis(self, keywords: List[str], matched_indicators: List[str],
                                    weight_mapping: Dict[str, Dict]) -> List[Dict]:
        """生成详细分析"""
        detailed = []

        for keyword in keywords:
            # 这里可以添加更详细的分析逻辑
            detailed.append({
                "keyword": keyword,
                "matched_indicator": None,
                "weight": 0,
                "description": f"关键词 {keyword} 的能力分析"
            })

        return detailed

    def _empty_result(self) -> Dict:
        """返回空结果"""
        return {
            "top_dimension": {"name": "无", "score": 0},
            "dimension_scores": {},
            "matched_indicators": [],
            "analysis_summary": "未检测到关键词，无法进行素养分析",
            "detailed_analysis": []
        }
