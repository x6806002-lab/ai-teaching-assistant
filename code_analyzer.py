import ast


def extract_keywords(code_snippet: str):
    """
    从代码中提取更丰富的关键词，包括：
    1. 导入的模块/函数/类名 (如 pandas, train_test_split)
    2. 方法调用 (如 df.groupby, model.fit)
    3. 属性访问 (如 df.shape, model.coef_)
    4. 类实例化 (如 LogisticRegression())
    """
    try:
        tree = ast.parse(code_snippet)
    except SyntaxError:
        return []

    keywords = set()
    # 定义我们自己的模块前缀，用于过滤
    self_module_prefixes = ('code_analyzer', 'knowledge_graph', 'nlp_processor', 'data_loader', 'weight_analyzer',
                            'main')

    for node in ast.walk(tree):
        # --- 1. 提取 import 的模块/函数/类名 ---
        if isinstance(node, ast.ImportFrom):
            if node.module:
                for alias in node.names:
                    keywords.add(alias.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                keywords.add(alias.name)

        # --- 2. 提取方法调用 (如 df.groupby(), model.fit()) ---
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                # 这是一个方法调用，我们关心方法名本身，例如 'groupby'
                method_name = node.func.attr
                keywords.add(method_name)
            elif isinstance(node.func, ast.Name):
                # 这是一个直接的函数或类调用，例如 'print' 或 'LogisticRegression'
                func_name = node.func.id
                keywords.add(func_name)

        # --- 3. 提取属性访问 (如 df.shape, model.coef_) ---
        if isinstance(node, ast.Attribute):
            # 我们关心属性名本身，例如 'shape' 或 'coef_'
            attr_name = node.attr
            keywords.add(attr_name)

    # --- 4. 过滤和清理 ---
    filtered_keywords = set()
    for kw in keywords:
        # 过滤掉我们自己模块的函数
        is_self_module = any(kw.startswith(prefix) for prefix in self_module_prefixes)
        # 过滤掉Python内置的通用函数和属性
        is_builtin_or_common = kw in ('print', 'str', 'len', 'list', 'dict', 'int', 'float', 'range', 'enumerate',
                                      'self', 'cls')
        # 确保是合法的Python标识符，过滤掉操作符等
        is_valid_identifier = kw.isidentifier()

        if not is_self_module and not is_builtin_or_common and is_valid_identifier:
            filtered_keywords.add(kw)

    return list(filtered_keywords)

