"""配置加载器：CLI > yaml > 默认值"""
import copy
from pathlib import Path

import yaml

_DEFAULTS = {
    "data": {
        "source": "demo",
        "csv_path": "data/sample/jobs.csv",
        "sqlite_path": "data/jobs.db",
    },
    "analysis": {
        "salary": {
            "bins": [0, 10, 15, 20, 25, 30, 40, 50, 100],
            "percentiles": [25, 50, 75, 90],
        },
        "skill": {
            "min_frequency": 0.05,
            "top_n": 20,
        },
        "competitive": {
            "weights": {
                "job_density": 0.4,
                "salary_level": 0.3,
                "education_relaxation": 0.3,
            },
        },
    },
    "visualization": {
        "theme": "plotly_white",
        "color_scale": "Viridis",
        "chart_width": 1200,
        "output_dir": "output/reports",
    },
    "resume": {
        "user_skills": [],
        "user_experience": "",
        "user_education": "",
        "target_city": "",
        "target_salary": "",
    },
}


class Config:
    """配置对象"""

    def __init__(self, data: dict):
        self.data = data["data"]
        self.analysis = data["analysis"]
        self.visualization = data["visualization"]
        self.resume = data["resume"]

    @classmethod
    def load(cls, config_path: str = "config.yaml", **cli_overrides) -> "Config":
        """加载配置，优先级：CLI参数 > config.yaml > 内置默认值"""
        # 1. 深拷贝默认值
        cfg = copy.deepcopy(_DEFAULTS)

        # 2. 如果 config.yaml 存在，合并覆盖
        if Path(config_path).exists():
            with open(config_path, "r", encoding="utf-8") as f:
                user_cfg = yaml.safe_load(f)
            if user_cfg:
                cfg = cls._deep_merge(cfg, user_cfg)

        # 3. CLI 参数最高优先级
        if cli_overrides:
            cli_cfg = {}
            for key, val in cli_overrides.items():
                if val is None:
                    continue
                # 映射 CLI 参数名到配置路径
                if key == "source":
                    cli_cfg.setdefault("data", {})["source"] = val
                elif key == "csv_path":
                    cli_cfg.setdefault("data", {})["csv_path"] = val
                elif key in ("user_skills", "user_experience", "user_education",
                             "target_city", "target_salary"):
                    cli_cfg.setdefault("resume", {})[key] = val
            if cli_cfg:
                cfg = cls._deep_merge(cfg, cli_cfg)

        return cls(cfg)

    @staticmethod
    def _deep_merge(base: dict, override: dict) -> dict:
        """递归合并字典"""
        for key, val in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(val, dict):
                base[key] = Config._deep_merge(base[key], val)
            else:
                base[key] = val
        return base
