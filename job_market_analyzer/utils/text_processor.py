"""文本预处理工具：分词 + TF-IDF"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# 常见技能关键词表（用于从文本中提取技能）
_SKILL_KEYWORDS = {
    "Python", "Java", "JavaScript", "TypeScript", "Go", "Rust", "C++", "C#",
    "SQL", "MySQL", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch",
    "Spark", "Hadoop", "Hive", "Flink", "Kafka",
    "Excel", "Tableau", "PowerBI", "Power BI", "Superset",
    "Pandas", "NumPy", "Scikit-learn", "TensorFlow", "PyTorch", "Keras",
    "Docker", "Kubernetes", "AWS", "Azure", "GCP",
    "Linux", "Shell", "Git",
    "机器学习", "深度学习", "自然语言处理", "NLP", "计算机视觉",
    "数据分析", "数据挖掘", "商业分析", "ETL", "数仓",
    "HTML", "CSS", "React", "Vue", "Node",
    "Spring", "Django", "Flask", "FastAPI",
}


def tokenize(text: str) -> list[str]:
    """从文本中提取技能关键词"""
    if not text:
        return []
    # 在文本中搜索已知的技能关键词
    found = []
    text_lower = text.lower()
    for skill in _SKILL_KEYWORDS:
        if skill.lower() in text_lower:
            found.append(skill)
    return found


def compute_tfidf_similarity(text1: str, text2: str) -> float:
    """计算两段文本的 TF-IDF 余弦相似度 (0-1)"""
    if not text1 or not text2:
        return 0.0
    vectorizer = TfidfVectorizer()
    try:
        tfidf_matrix = vectorizer.fit_transform([text1, text2])
        sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return float(sim)
    except ValueError:
        return 0.0
