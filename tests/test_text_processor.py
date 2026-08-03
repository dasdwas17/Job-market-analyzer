# tests/test_text_processor.py
from job_market_analyzer.utils.text_processor import compute_tfidf_similarity, tokenize


class TestTokenize:
    def test_basic(self):
        tokens = tokenize("熟练掌握Python和SQL，熟悉Excel")
        assert "Python" in tokens
        assert "SQL" in tokens
        assert "Excel" in tokens

    def test_empty(self):
        assert tokenize("") == []

    def test_skill_extraction(self):
        tokens = tokenize("需要Python, Spark, Hadoop经验")
        assert "Python" in tokens
        assert "Spark" in tokens


class TestTfidfSimilarity:
    def test_identical(self):
        text1 = "熟练Python SQL数据分析"
        text2 = "熟练Python SQL数据分析"
        score = compute_tfidf_similarity(text1, text2)
        assert score > 0.9

    def test_different(self):
        text1 = "Python数据分析"
        text2 = "Java后端开发"
        score = compute_tfidf_similarity(text1, text2)
        assert score < 0.3
