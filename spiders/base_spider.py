import time
import random
import logging
import sys
import os
from abc import ABC, abstractmethod

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import REQUEST_DELAY, MAX_RETRIES
from utils.db_helper import get_session, Job

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class BaseSpider(ABC):
    def __init__(self, source_name):
        self.source = source_name
        self.logger = logging.getLogger(source_name)
        self.session = get_session()
        self.collected_count = 0

    def delay(self, min_delay=None, max_delay=None):
        if min_delay is None:
            min_delay = REQUEST_DELAY
        if max_delay is None:
            max_delay = REQUEST_DELAY * 2
        sleep_time = random.uniform(min_delay, max_delay)
        self.logger.debug(f'等待 {sleep_time:.1f} 秒')
        time.sleep(sleep_time)

    def save_job(self, job_data):
        try:
            existing = self.session.query(Job).filter_by(job_id=job_data.get('job_id')).first()
            if existing:
                self.logger.debug(f'岗位已存在: {job_data.get("job_id")}')
                return False

            job = Job(**job_data)
            self.session.add(job)
            self.session.commit()
            self.collected_count += 1
            return True
        except Exception as e:
            self.session.rollback()
            self.logger.error(f'保存岗位失败: {e}')
            return False

    def batch_save_jobs(self, job_list):
        new_jobs = []
        for job_data in job_list:
            try:
                existing = self.session.query(Job).filter_by(job_id=job_data.get('job_id')).first()
                if not existing:
                    new_jobs.append(Job(**job_data))
            except Exception as e:
                self.logger.error(f'检查岗位失败: {e}')

        if new_jobs:
            try:
                self.session.bulk_save_objects(new_jobs)
                self.session.commit()
                self.collected_count += len(new_jobs)
                self.logger.info(f'批量保存 {len(new_jobs)} 条新岗位')
            except Exception as e:
                self.session.rollback()
                self.logger.error(f'批量保存失败: {e}')

        return len(new_jobs)

    @abstractmethod
    def crawl(self, keyword, city, max_pages=10):
        pass

    def get_stats(self):
        return {
            'source': self.source,
            'collected_count': self.collected_count
        }
