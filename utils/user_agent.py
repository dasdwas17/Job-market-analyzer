import random
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import USER_AGENTS


class UserAgentPool:
    def __init__(self):
        self.user_agents = USER_AGENTS
        self._index = 0

    def get_random(self):
        return random.choice(self.user_agents)

    def get_next(self):
        ua = self.user_agents[self._index % len(self.user_agents)]
        self._index += 1
        return ua

    def get_headers(self, referer=None):
        headers = {
            'User-Agent': self.get_random(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
        }
        if referer:
            headers['Referer'] = referer
        return headers


ua_pool = UserAgentPool()
