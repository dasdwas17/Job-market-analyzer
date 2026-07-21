import os
import sys
import tempfile
import json
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from utils.db_helper import (
    Base, Company, Job, Skill, JobSkill,
    get_engine, get_session, init_db,
    generate_job_id, generate_company_id,
    validate_job_data, upsert_company, upsert_job,
    mark_inactive_jobs, _guess_skill_category
)


TEST_DB_DIR = tempfile.mkdtemp(prefix='job_test_')
TEST_DB_PATH = os.path.join(TEST_DB_DIR, 'test_jobs.db')


def setup_module():
    init_db(TEST_DB_PATH)


def get_test_session():
    engine = get_engine(TEST_DB_PATH)
    Session = sessionmaker(bind=engine)
    return Session()


def make_company_data(name='测试科技公司', size='100-499人', industry='互联网'):
    return {
        'company_id': generate_company_id('boss', name),
        'company_name': name,
        'company_size': size,
        'company_type': '民营',
        'industry': industry,
    }


def make_job_data(job_name='数据分析师', city='北京', salary_min=15000, salary_max=25000,
                  company_id=None, source='boss', job_url='https://www.zhipin.com/job/123'):
    return {
        'job_id': generate_job_id(source, job_url, '测试科技公司'),
        'job_name': job_name,
        'salary': '15-25K·14薪',
        'salary_min': salary_min,
        'salary_max': salary_max,
        'salary_median': (salary_min + salary_max) / 2,
        'salary_months': 14,
        'city': city,
        'experience': '3-5年',
        'education': '本科',
        'job_type': '全职',
        'job_description': '负责数据分析工作',
        'benefits': '五险一金,年终奖,双休',
        'work_mode': '全职',
        'extra_json': {'hot': True, 'recruit_count': 3},
        'company_id': company_id,
        'source': source,
        'job_url': job_url,
        'is_active': 1,
    }


# ==================== 表结构测试 ====================

def test_tables_created():
    session = get_test_session()
    try:
        tables = [row[0] for row in session.execute(text("SELECT name FROM sqlite_master WHERE type='table'")).fetchall()]
        assert 'companies' in tables, f'companies表未创建, 现有: {tables}'
        assert 'jobs' in tables, f'jobs表未创建, 现有: {tables}'
        assert 'skills' in tables, f'skills表未创建, 现有: {tables}'
        assert 'job_skills' in tables, f'job_skills表未创建, 现有: {tables}'
        print('[PASS] test_tables_created')
    finally:
        session.close()


def test_foreign_keys_enabled():
    session = get_test_session()
    try:
        result = session.execute(text('PRAGMA foreign_keys')).fetchone()
        assert result[0] == 1, f'外键未启用, 值为: {result[0]}'
        print('[PASS] test_foreign_keys_enabled')
    finally:
        session.close()


# ==================== 外键约束测试 ====================

def test_job_company_fk_restrict():
    session = get_test_session()
    try:
        company_data = make_company_data(name='FK测试公司')
        company_id = upsert_company(session, company_data)
        session.commit()

        job_data = make_job_data(job_name='测试岗位', company_id=company_id)
        upsert_job(session, job_data, skills=['Python', 'SQL'])
        session.commit()

        try:
            session.execute(text('DELETE FROM companies WHERE id = :cid'), {'cid': company_id})
            session.commit()
            assert False, '应该无法删除有岗位关联的公司(RESTRICT)'
        except IntegrityError:
            session.rollback()
            print('[PASS] test_job_company_fk_restrict')
    finally:
        session.close()


def test_job_skill_cascade_delete():
    session = get_test_session()
    try:
        company_data = make_company_data(name='级联测试公司')
        company_id = upsert_company(session, company_data)

        job_url = 'https://www.zhipin.com/job/cascade_test'
        job_data = make_job_data(
            job_name='级联测试岗',
            company_id=company_id,
            job_url=job_url
        )
        job_data['job_id'] = generate_job_id('boss', job_url, '级联测试公司')
        upsert_job(session, job_data, skills=['Python', 'SQL', 'Excel'])
        session.commit()

        skill_count = session.query(JobSkill).filter_by(job_id=job_data['job_id']).count()
        assert skill_count == 3, f'技能关联数应为3, 实际{skill_count}'

        session.execute(text('DELETE FROM jobs WHERE job_id = :jid'), {'jid': job_data['job_id']})
        session.commit()

        skill_count_after = session.query(JobSkill).filter_by(job_id=job_data['job_id']).count()
        assert skill_count_after == 0, f'级联删除后技能应为0, 实际{skill_count_after}'
        print('[PASS] test_job_skill_cascade_delete')
    finally:
        session.close()


# ==================== 幂等更新测试 ====================

def test_upsert_job_idempotent():
    session = get_test_session()
    try:
        company_data = make_company_data(name='幂等测试公司')
        company_id = upsert_company(session, company_data)

        job_url = 'https://www.zhipin.com/job/idempotent_test'
        job_data = make_job_data(
            job_name='幂等测试岗',
            company_id=company_id,
            job_url=job_url,
            salary_min=15000,
            salary_max=25000
        )
        job_data['job_id'] = generate_job_id('boss', job_url, '幂等测试公司')

        upsert_job(session, job_data, skills=['Python'])
        session.commit()

        job_count_before = session.query(Job).filter_by(job_id=job_data['job_id']).count()
        assert job_count_before == 1, f'第一次插入后应为1条, 实际{job_count_before}'

        job_data['salary_min'] = 20000
        job_data['salary_max'] = 30000
        job_data['salary_median'] = 25000
        upsert_job(session, job_data, skills=['Python', 'SQL'])
        session.commit()

        job_count_after = session.query(Job).filter_by(job_id=job_data['job_id']).count()
        assert job_count_after == 1, f'更新后仍应为1条(幂等), 实际{job_count_after}'

        job = session.query(Job).filter_by(job_id=job_data['job_id']).first()
        assert job.salary_min == 20000, f'薪资应更新为20000, 实际{job.salary_min}'
        assert job.salary_max == 30000, f'薪资应更新为30000, 实际{job.salary_max}'

        skill_count = session.query(JobSkill).filter_by(job_id=job_data['job_id']).count()
        assert skill_count == 2, f'技能应更新为2个, 实际{skill_count}'
        print('[PASS] test_upsert_job_idempotent')
    finally:
        session.close()


# ==================== is_active batch机制测试 ====================

def test_mark_inactive_jobs():
    session = get_test_session()
    try:
        company_data = make_company_data(name='Active测试公司')
        company_id = upsert_company(session, company_data)

        old_time = datetime(2026, 1, 1, 10, 0, 0)
        old_url = 'https://www.zhipin.com/job/old_job'
        old_job = make_job_data(
            job_name='旧岗位',
            company_id=company_id,
            job_url=old_url
        )
        old_job['job_id'] = generate_job_id('boss', old_url, 'Active测试公司')
        old_job['crawl_time'] = old_time
        old_job['is_active'] = 1
        upsert_job(session, old_job)
        session.commit()

        session.query(Job).filter_by(job_id=old_job['job_id']).update(
            {Job.crawl_time: old_time, Job.is_active: 1}
        )
        session.commit()

        batch_start = datetime(2026, 7, 21, 19, 0, 0)
        new_url = 'https://www.zhipin.com/job/new_job'
        new_job = make_job_data(
            job_name='新岗位',
            company_id=company_id,
            job_url=new_url
        )
        new_job['job_id'] = generate_job_id('boss', new_url, 'Active测试公司')
        new_job['crawl_time'] = batch_start + timedelta(minutes=5)
        upsert_job(session, new_job)
        session.commit()

        marked = mark_inactive_jobs(session, 'boss', batch_start)

        assert marked == 1, f'应标记1条旧岗位为inactive, 实际{marked}'

        old_job_obj = session.query(Job).filter_by(job_id=old_job['job_id']).first()
        assert old_job_obj.is_active == 0, f'旧岗位is_active应为0, 实际{old_job_obj.is_active}'

        new_job_obj = session.query(Job).filter_by(job_id=new_job['job_id']).first()
        assert new_job_obj.is_active == 1, f'新岗位is_active应为1, 实际{new_job_obj.is_active}'
        print('[PASS] test_mark_inactive_jobs')
    finally:
        session.close()


# ==================== 数据校验测试 ====================

def test_validate_salary_min_gt_max():
    job_data = make_job_data(salary_min=30000, salary_max=15000)
    errors = validate_job_data(job_data)
    assert len(errors) == 0, f'不应有必填错误: {errors}'
    assert job_data['salary_min'] is None, '异常min薪资应置为None'
    assert job_data['salary_max'] is None, '异常max薪资应置为None'
    assert job_data['salary_median'] is None, '异常median薪资应置为None'
    print('[PASS] test_validate_salary_min_gt_max')


def test_validate_salary_out_of_range():
    job_data = make_job_data(salary_min=100, salary_max=999999)
    validate_job_data(job_data)
    assert job_data['salary_min'] is None, '薪资100应置为None'
    assert job_data['salary_max'] is None, '薪资999999应置为None'
    print('[PASS] test_validate_salary_out_of_range')


def test_validate_required_fields():
    job_data = {'job_id': '', 'job_name': '', 'city': '', 'source': ''}
    errors = validate_job_data(job_data)
    assert len(errors) == 4, f'应有4个必填错误, 实际{len(errors)}: {errors}'
    print('[PASS] test_validate_required_fields')


def test_validate_extra_json_serialization():
    job_data = make_job_data()
    job_data['extra_json'] = {'hot': True, 'recruit_count': 3}
    validate_job_data(job_data)
    assert isinstance(job_data['extra_json'], str), 'extra_json应被序列化为字符串'
    parsed = json.loads(job_data['extra_json'])
    assert parsed['hot'] == True
    assert parsed['recruit_count'] == 3
    print('[PASS] test_validate_extra_json_serialization')


# ==================== 技能字典测试 ====================

def test_skill_dict_initialized():
    session = get_test_session()
    try:
        skill_count = session.query(Skill).count()
        assert skill_count > 0, f'技能字典应已初始化, 实际{skill_count}条'

        python_skill = session.query(Skill).filter_by(skill_name='Python').first()
        assert python_skill is not None, 'Python技能应在字典中'
        assert python_skill.category == '编程语言', f'Python分类应为编程语言, 实际{python_skill.category}'
        print(f'[PASS] test_skill_dict_initialized (共{skill_count}个技能)')
    finally:
        session.close()


def test_guess_skill_category():
    assert _guess_skill_category('Python') == '编程语言'
    assert _guess_skill_category('Tableau') == 'BI工具'
    assert _guess_skill_category('机器学习') == '机器学习'
    assert _guess_skill_category('未知技能') == '其他'
    print('[PASS] test_guess_skill_category')


# ==================== NOT NULL约束测试 ====================

def test_job_not_null_constraints():
    session = get_test_session()
    try:
        invalid_job = Job(job_id=None, job_name='测试', city='北京', source='boss')
        session.add(invalid_job)
        try:
            session.commit()
            assert False, 'job_id为NULL时应报错'
        except IntegrityError:
            session.rollback()
        print('[PASS] test_job_not_null_constraints')
    finally:
        session.close()


# ==================== 复合索引测试 ====================

def test_composite_index_exists():
    engine = get_engine(TEST_DB_PATH)
    with engine.connect() as conn:
        indexes = conn.execute(text(
            "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='jobs'"
        )).fetchall()
        index_names = [idx[0] for idx in indexes]
        assert 'idx_city_exp_edu' in index_names, f'复合索引idx_city_exp_edu不存在: {index_names}'
        assert 'idx_city_salary' in index_names, f'复合索引idx_city_salary不存在: {index_names}'
        assert 'idx_source_crawl' in index_names, f'复合索引idx_source_crawl不存在: {index_names}'
        print(f'[PASS] test_composite_index_exists (索引: {index_names})')


def run_all_tests():
    print('=' * 60)
    print('数据库设计测试')
    print('=' * 60)

    print('[SETUP] 初始化测试数据库...')
    setup_module()
    print(f'[SETUP] 测试数据库: {TEST_DB_PATH}')

    tests = [
        test_tables_created,
        test_foreign_keys_enabled,
        test_job_company_fk_restrict,
        test_job_skill_cascade_delete,
        test_upsert_job_idempotent,
        test_mark_inactive_jobs,
        test_validate_salary_min_gt_max,
        test_validate_salary_out_of_range,
        test_validate_required_fields,
        test_validate_extra_json_serialization,
        test_skill_dict_initialized,
        test_guess_skill_category,
        test_job_not_null_constraints,
        test_composite_index_exists,
    ]

    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f'[FAIL] {test.__name__}: {e}')
            failed += 1

    print('=' * 60)
    print(f'结果: {passed} 通过, {failed} 失败, 共 {len(tests)} 项')
    print('=' * 60)
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
