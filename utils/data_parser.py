import re
import jieba
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import SKILL_KEYWORDS


def parse_salary(salary_str):
    if not salary_str:
        return None, None, None, 12

    salary_str = salary_str.strip()
    months = 12

    months_match = re.search(r'(\d+)\s*薪', salary_str)
    if months_match:
        months = int(months_match.group(1))

    salary_str = re.sub(r'·\d+薪', '', salary_str).strip()

    if 'K' in salary_str or 'k' in salary_str:
        k_pattern = r'(\d+(?:\.\d+)?)\s*[-~至]\s*(\d+(?:\.\d+)?)\s*[Kk]'
        match = re.search(k_pattern, salary_str)
        if match:
            min_sal = float(match.group(1)) * 1000
            max_sal = float(match.group(2)) * 1000
            median = (min_sal + max_sal) / 2
            return min_sal, max_sal, median, months

        single_k = r'(\d+(?:\.\d+)?)\s*[Kk]'
        match = re.search(single_k, salary_str)
        if match:
            val = float(match.group(1)) * 1000
            return val, val, val, months

    if '元' in salary_str:
        yuan_pattern = r'(\d+)\s*[-~至]\s*(\d+)\s*元'
        match = re.search(yuan_pattern, salary_str)
        if match:
            min_sal = float(match.group(1))
            max_sal = float(match.group(2))
            median = (min_sal + max_sal) / 2
            return min_sal, max_sal, median, months

    if '万' in salary_str:
        wan_pattern = r'(\d+(?:\.\d+)?)\s*[-~至]\s*(\d+(?:\.\d+)?)\s*万'
        match = re.search(wan_pattern, salary_str)
        if match:
            min_sal = float(match.group(1)) * 10000
            max_sal = float(match.group(2)) * 10000
            median = (min_sal + max_sal) / 2
            return min_sal, max_sal, median, months

    num_pattern = r'(\d+)\s*[-~至]\s*(\d+)'
    match = re.search(num_pattern, salary_str)
    if match:
        min_sal = float(match.group(1))
        max_sal = float(match.group(2))
        if max_sal < 1000:
            min_sal *= 1000
            max_sal *= 1000
        median = (min_sal + max_sal) / 2
        return min_sal, max_sal, median, months

    return None, None, None, months


def extract_skills(text, skill_list=None):
    if not text:
        return []

    if skill_list is None:
        skill_list = SKILL_KEYWORDS

    text_lower = text.lower()
    found_skills = []

    for skill in skill_list:
        if skill.lower() in text_lower:
            found_skills.append(skill)

    return found_skills


def segment_text(text):
    if not text:
        return []

    words = jieba.lcut(text)
    stopwords = {'的', '了', '和', '是', '在', '有', '与', '等', '及', '对', '或', '以', '为', '中', '上', '下', '与', '将', '从'}
    filtered = [w for w in words if len(w) >= 2 and w not in stopwords]
    return filtered


def clean_experience(exp_str):
    if not exp_str:
        return ''

    exp_str = exp_str.strip()

    patterns = [
        (r'经验\s*不限', '经验不限'),
        (r'在校/应届|应届毕业生|应届生', '应届生'),
        (r'(\d+)-(\d+)\s*年', r'\1-\2年'),
        (r'(\d+)年以上', r'\1年以上'),
        (r'(\d+)年经验', r'\1年以上'),
    ]

    for pattern, replacement in patterns:
        if re.search(pattern, exp_str):
            if '\\1' in replacement:
                match = re.search(pattern, exp_str)
                if match:
                    return replacement.replace('\\1', match.group(1)).replace('\\2', match.group(2))
            else:
                return replacement

    return exp_str


def clean_education(edu_str):
    if not edu_str:
        return ''

    edu_str = edu_str.strip()

    edu_order = ['不限', '高中', '中专', '大专', '本科', '硕士', '博士', 'MBA']
    for edu in edu_order:
        if edu in edu_str:
            return edu

    return edu_str


def parse_company_size(size_str):
    if not size_str:
        return ''

    size_str = size_str.strip()

    size_patterns = [
        (r'0-20人|少于20人|小于20人', '0-20人'),
        (r'20-99人|20-99', '20-99人'),
        (r'100-499人|100-299人|300-499人', '100-499人'),
        (r'500-999人|500-999', '500-999人'),
        (r'1000-9999人|1000人以上|1000-5000人', '1000-9999人'),
        (r'10000人以上|万人以上', '10000人以上'),
    ]

    for pattern, standard in size_patterns:
        if re.search(pattern, size_str):
            return standard

    return size_str
