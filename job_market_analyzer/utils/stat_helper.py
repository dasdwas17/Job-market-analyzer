"""统计工具函数"""
import numpy as np


def normalize(data: list[float] | np.ndarray) -> np.ndarray:
    """Min-Max 归一化到 [0, 1]"""
    arr = np.array(data, dtype=float)
    if len(arr) == 0:
        return arr
    min_val, max_val = arr.min(), arr.max()
    if max_val == min_val:
        return np.zeros_like(arr)
    return (arr - min_val) / (max_val - min_val)


def bin_values(data: list[float], bins: list[float]) -> tuple[list[str], list[int]]:
    """将数据分箱，返回 (标签, 计数)"""
    arr = np.array(data, dtype=float)
    counts, _ = np.histogram(arr, bins=bins)
    labels = [f"{bins[i]}-{bins[i+1]}K" for i in range(len(bins) - 1)]
    return labels, counts.tolist()


def safe_percentile(data: list[float], q: float) -> float | None:
    """安全百分位计算，空数据返回 None"""
    if not data:
        return None
    return float(np.percentile(data, q))
