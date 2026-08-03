"""数据适配器抽象基类"""
from abc import ABC, abstractmethod

from job_market_analyzer.schema import JobItem


class BaseAdapter(ABC):
    """数据源适配器基类，用户继承此类实现 fetch_jobs()"""

    @abstractmethod
    def fetch_jobs(self, **kwargs) -> list[JobItem]:
        """获取岗位数据，返回 JobItem 列表"""
