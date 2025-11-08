import ast
import re
from typing import List, Set, Dict
from collections import Counter


class KeywordExtractor:
    """关键词提取器"""

    def __init__(self, keyword_mapping: Dict[str, Dict]):
        self.keyword_mapping = keyword_mapping
        self.all_keywords = set(keyword_mapping.keys())

        # 按长度排序，优先匹配长的关键词
        self.sorted_keywords = sorted(self.all_keywords, key=len, reverse=True)

    def extract_from_code(self, code: str) -> List[str]:
        """从代码中提取关键词"""
        keywords = set()

        # 1. 从AST提取
        ast_keywords = self._extract_from_ast(code)
        keywords.update(ast_keywords)

        # 2. 从正则表达式提取（处理字符串中的关键词）
        regex_keywords = self._extract_with_regex(code)
        keywords.update(regex_keywords)

        # 3. 过滤和排序
        filtered_keywords = [kw for kw in keywords if kw in self.all_keywords]

        # 按权重排序
        weighted_keywords = []
        for kw in filtered_keywords:
            weight = self.keyword_mapping.get(kw, {}).get('weight', 0)
            weighted_keywords.append((kw, weight))

        weighted_keywords.sort(key=lambda x: x[1], reverse=True)

        return [kw for kw, _ in weighted_keywords]

    def _extract_from_ast(self, code: str) -> Set[str]:
        """从AST提取关键词"""
        keywords = set()

        try:
            tree = ast.parse(code)

            for node in ast.walk(tree):
                # 函数调用
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        keywords.add(node.func.id)
                    elif isinstance(node.func, ast.Attribute):
                        keywords.add(node.func.attr)

                # 导入
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        keywords.add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        keywords.add(node.module)
                    for alias in node.names:
                        keywords.add(alias.name)

                # 名称
                elif isinstance(node, ast.Name):
                    keywords.add(node.id)

        except SyntaxError:
            pass

        return keywords

    def _extract_with_regex(self, code: str) -> Set[str]:
        """使用正则表达式提取关键词"""
        keywords = set()

        # 提取字符串中的关键词
        string_pattern = r'["\']([^"\']+)["\']'
        strings = re.findall(string_pattern, code)

        for text in strings:
            for keyword in self.sorted_keywords:
                if keyword in text:
                    keywords.add(keyword)

        # 提取注释中的关键词
        comment_pattern = r'#.*$'
        comments = re.findall(comment_pattern, code, re.MULTILINE)

        for comment in comments:
            for keyword in self.sorted_keywords:
                if keyword in comment:
                    keywords.add(keyword)

        return keywords
