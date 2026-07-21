import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DB_PATH = os.path.join(BASE_DIR, 'data', 'jobs.db')

DATA_DIR = os.path.join(BASE_DIR, 'data')
RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw')
CLEANED_DATA_DIR = os.path.join(DATA_DIR, 'cleaned')

OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
REPORTS_DIR = os.path.join(OUTPUT_DIR, 'reports')
CHARTS_DIR = os.path.join(OUTPUT_DIR, 'charts')

REQUEST_DELAY = 5
PAGE_TIMEOUT = 30

MAX_RETRIES = 3

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
]

KEYWORDS = ['数据分析师', '数据运营', '商业分析', '数据产品经理']

CITIES = [
    {'name': '北京', 'code': '101010100', 'tier': '一线'},
    {'name': '上海', 'code': '101020100', 'tier': '一线'},
    {'name': '广州', 'code': '101280100', 'tier': '一线'},
    {'name': '深圳', 'code': '101280600', 'tier': '一线'},
    {'name': '成都', 'code': '101270100', 'tier': '新一线'},
    {'name': '杭州', 'code': '101210100', 'tier': '新一线'},
    {'name': '重庆', 'code': '101040100', 'tier': '新一线'},
    {'name': '武汉', 'code': '101200100', 'tier': '新一线'},
    {'name': '西安', 'code': '101110100', 'tier': '新一线'},
    {'name': '苏州', 'code': '101190400', 'tier': '新一线'},
    {'name': '郑州', 'code': '101180100', 'tier': '新一线'},
    {'name': '南京', 'code': '101190100', 'tier': '新一线'},
    {'name': '天津', 'code': '101030100', 'tier': '新一线'},
    {'name': '长沙', 'code': '101250100', 'tier': '新一线'},
    {'name': '东莞', 'code': '101281600', 'tier': '新一线'},
    {'name': '宁波', 'code': '101210400', 'tier': '新一线'},
    {'name': '佛山', 'code': '101280800', 'tier': '新一线'},
    {'name': '合肥', 'code': '101220100', 'tier': '新一线'},
    {'name': '青岛', 'code': '101120200', 'tier': '新一线'},
]

SKILL_KEYWORDS = [
    'Python', 'SQL', 'Excel', 'Tableau', 'Power BI', 'FineBI',
    'R', 'SPSS', 'SAS', 'Stata',
    'Hadoop', 'Spark', 'Hive', 'Flink', 'Kafka',
    'MySQL', 'Oracle', 'PostgreSQL', 'MongoDB', 'Redis',
    '机器学习', '深度学习', 'NLP', '数据挖掘',
    '统计学', '数学建模', '用户画像', '增长黑客',
    'ETL', '数据仓库', '数据中台',
    'Pandas', 'NumPy', 'Matplotlib', 'Seaborn', 'Scikit-learn',
    'Git', 'Linux', 'Docker',
    '数据可视化', '报表开发', 'BI',
    '业务分析', '商业智能', '用户分析', '运营分析',
    'AB测试', '漏斗分析', '留存分析',
]

LIVING_COST_INDEX = {
    '北京': 1.0,
    '上海': 0.98,
    '深圳': 0.95,
    '广州': 0.8,
    '杭州': 0.82,
    '成都': 0.65,
    '武汉': 0.62,
    '西安': 0.58,
    '重庆': 0.6,
    '苏州': 0.75,
    '南京': 0.72,
    '天津': 0.68,
    '长沙': 0.55,
    '郑州': 0.52,
    '东莞': 0.65,
    '宁波': 0.7,
    '佛山': 0.6,
    '合肥': 0.58,
    '青岛': 0.65,
}

CITY_TIER_MAP = {city['name']: city['tier'] for city in CITIES}

EXTRA_JSON_SCHEMA = {
    'hot': None,
    'recruit_count': None,
    'position_tags': None,
    'company_score': None,
    'interview_difficulty': None,
}

SKILL_CATEGORY_MAP = {
    '编程语言': ['Python', 'R', 'SQL', 'Java', 'Scala', 'Shell'],
    '数据库': ['MySQL', 'Oracle', 'PostgreSQL', 'MongoDB', 'Redis', 'Hive'],
    '大数据': ['Hadoop', 'Spark', 'Flink', 'Kafka', 'ETL', '数据仓库', '数据中台'],
    'BI工具': ['Tableau', 'Power BI', 'FineBI', 'Excel', 'BI', '数据可视化', '报表开发'],
    'Python库': ['Pandas', 'NumPy', 'Matplotlib', 'Seaborn', 'Scikit-learn'],
    '统计分析': ['SPSS', 'SAS', 'Stata', '统计学', '数学建模', 'AB测试', '漏斗分析', '留存分析'],
    '机器学习': ['机器学习', '深度学习', 'NLP', '数据挖掘'],
    '工具平台': ['Git', 'Linux', 'Docker'],
    '业务能力': ['用户画像', '增长黑客', '业务分析', '商业智能', '用户分析', '运营分析'],
}
