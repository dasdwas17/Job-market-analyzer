from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Text, DateTime,
    ForeignKey, Index, UniqueConstraint, event
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import os
import sys
import logging
import json
import hashlib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import DB_PATH, EXTRA_JSON_SCHEMA, SKILL_CATEGORY_MAP

Base = declarative_base()
logger = logging.getLogger(__name__)


class Company(Base):
    __tablename__ = 'companies'

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(String(100), unique=True, nullable=False, index=True, comment='公司唯一ID')
    company_name = Column(String(200), nullable=False, index=True, comment='公司名称')
    company_size = Column(String(50), comment='公司规模')
    company_type = Column(String(100), comment='公司类型')
    industry = Column(String(100), index=True, comment='所属行业')
    created_at = Column(DateTime, default=datetime.now)

    jobs = relationship('Job', back_populates='company')


class Job(Base):
    __tablename__ = 'jobs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String(100), unique=True, nullable=False, index=True, comment='岗位唯一ID')
    job_name = Column(String(200), nullable=False, index=True, comment='岗位名称')

    salary = Column(String(100), comment='原始薪资字符串')
    salary_min = Column(Float, comment='薪资下限（元/月）')
    salary_max = Column(Float, comment='薪资上限（元/月）')
    salary_median = Column(Float, comment='薪资中位数（元/月）')
    salary_months = Column(Integer, default=12, comment='年薪月份数')

    city = Column(String(50), nullable=False, index=True, comment='城市')
    district = Column(String(50), comment='区域')

    experience = Column(String(50), index=True, comment='经验要求')
    education = Column(String(50), index=True, comment='学历要求')

    job_type = Column(String(50), comment='岗位类型：全职/兼职/实习')
    job_description = Column(Text, comment='岗位描述')
    benefits = Column(Text, comment='福利：五险一金/年终奖/双休等')
    work_mode = Column(String(20), comment='工作模式：全职/远程/混合办公')
    extra_json = Column(Text, comment='扩展字段JSON，遵循 EXTRA_JSON_SCHEMA')

    company_id = Column(Integer, ForeignKey('companies.id', ondelete='RESTRICT'), comment='公司ID')

    source = Column(String(50), nullable=False, index=True, comment='数据来源：boss/lagou/kanzhun')
    job_url = Column(String(500), comment='岗位链接')
    is_active = Column(Integer, default=1, comment='是否有效：1有效 0已下线')
    crawl_time = Column(DateTime, default=datetime.now, index=True, comment='抓取时间')
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    company = relationship('Company', back_populates='jobs')
    skills = relationship('JobSkill', back_populates='job', cascade='all, delete-orphan')

    __table_args__ = (
        Index('idx_city_exp_edu', 'city', 'experience', 'education'),
        Index('idx_city_salary', 'city', 'salary_median'),
        Index('idx_source_crawl', 'source', 'crawl_time'),
    )


class Skill(Base):
    __tablename__ = 'skills'

    skill_name = Column(String(100), primary_key=True, comment='技能名称')
    category = Column(String(50), comment='技能分类')
    created_at = Column(DateTime, default=datetime.now)


class JobSkill(Base):
    __tablename__ = 'job_skills'

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String(100), ForeignKey('jobs.job_id', ondelete='CASCADE'),
                    nullable=False, index=True, comment='岗位业务ID（非自增主键）')
    skill_name = Column(String(100), ForeignKey('skills.skill_name'),
                        nullable=False, index=True, comment='技能名称')
    created_at = Column(DateTime, default=datetime.now)

    job = relationship('Job', back_populates='skills')

    __table_args__ = (
        UniqueConstraint('job_id', 'skill_name', name='uix_job_skill'),
    )


def _enable_foreign_keys(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute('PRAGMA foreign_keys=ON')
    cursor.close()


def get_engine(db_path=None):
    if db_path is None:
        db_path = DB_PATH
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)
    engine = create_engine(f'sqlite:///{db_path}', echo=False)
    event.listen(engine, 'connect', _enable_foreign_keys)
    return engine


def get_session(db_path=None):
    engine = get_engine(db_path)
    Session = sessionmaker(bind=engine)
    return Session()


def init_db(db_path=None):
    engine = get_engine(db_path)
    Base.metadata.create_all(engine)
    _init_skill_dict(engine)
    print(f'数据库已初始化: {db_path or DB_PATH}')


def _init_skill_dict(engine):
    from config.settings import SKILL_KEYWORDS
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        existing = {s.skill_name for s in session.query(Skill).all()}
        for category, skills in SKILL_CATEGORY_MAP.items():
            for skill_name in skills:
                if skill_name not in existing:
                    session.add(Skill(skill_name=skill_name, category=category))
                    existing.add(skill_name)
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f'初始化技能字典失败: {e}')
    finally:
        session.close()


def generate_job_id(source, job_url, company_name=''):
    raw = f'{source}_{job_url}_{company_name}'
    return hashlib.md5(raw.encode('utf-8')).hexdigest()


def generate_company_id(source, company_name, company_url=''):
    raw = f'{source}_{company_name}_{company_url}'
    return hashlib.md5(raw.encode('utf-8')).hexdigest()


def validate_job_data(job_data):
    errors = []
    required_fields = ['job_id', 'job_name', 'city', 'source']
    for field in required_fields:
        if not job_data.get(field):
            errors.append(f'必填字段缺失: {field}')

    salary_min = job_data.get('salary_min')
    salary_max = job_data.get('salary_max')
    if salary_min is not None and salary_max is not None:
        if salary_min > salary_max:
            logger.warning(f'薪资异常 min={salary_min} > max={salary_max}，置为NULL: {job_data.get("job_id")}')
            job_data['salary_min'] = None
            job_data['salary_max'] = None
            job_data['salary_median'] = None

    if salary_min is not None and (salary_min < 1000 or salary_min > 500000):
        logger.warning(f'薪资下限异常 {salary_min}，置为NULL: {job_data.get("job_id")}')
        job_data['salary_min'] = None
    if salary_max is not None and (salary_max < 1000 or salary_max > 500000):
        logger.warning(f'薪资上限异常 {salary_max}，置为NULL: {job_data.get("job_id")}')
        job_data['salary_max'] = None

    extra = job_data.get('extra_json')
    if isinstance(extra, dict):
        job_data['extra_json'] = json.dumps(extra, ensure_ascii=False)

    return errors


def upsert_company(session, company_data):
    company_id = company_data.get('company_id')
    if not company_id:
        return None

    existing = session.query(Company).filter_by(company_id=company_id).first()
    if existing:
        for key, value in company_data.items():
            if value is not None and hasattr(existing, key):
                setattr(existing, key, value)
        session.flush()
        return existing.id

    company = Company(**company_data)
    session.add(company)
    session.flush()
    return company.id


def upsert_job(session, job_data, skills=None):
    errors = validate_job_data(job_data)
    if errors:
        logger.error(f'数据校验失败: {errors}')
        return None

    job_id = job_data['job_id']
    existing = session.query(Job).filter_by(job_id=job_id).first()

    if existing:
        for key, value in job_data.items():
            if hasattr(existing, key):
                setattr(existing, key, value)
        existing.is_active = 1
        existing.crawl_time = datetime.now()
        session.flush()
        job_obj = existing
    else:
        job_obj = Job(**job_data)
        session.add(job_obj)
        session.flush()

    if skills:
        session.query(JobSkill).filter_by(job_id=job_id).delete()
        for skill_name in skills:
            if not session.query(Skill).filter_by(skill_name=skill_name).first():
                session.add(Skill(skill_name=skill_name, category=_guess_skill_category(skill_name)))
            session.add(JobSkill(job_id=job_id, skill_name=skill_name))

    return job_obj.id


def _guess_skill_category(skill_name):
    for category, skills in SKILL_CATEGORY_MAP.items():
        if skill_name in skills:
            return category
    return '其他'


def mark_inactive_jobs(session, source, batch_start_time):
    result = session.query(Job).filter(
        Job.source == source,
        Job.crawl_time < batch_start_time,
        Job.is_active == 1
    ).update({Job.is_active: 0})
    session.commit()
    logger.info(f'标记 {result} 条岗位为已下线 (source={source})')
    return result


if __name__ == '__main__':
    init_db()
