from typing import Optional
import math


def geo_score(distance_km: float, sigma: float = 5.0) -> float:
    """
    Distance decay function: returns in [0,1], closer => higher.
    sigma controls decay; smaller sigma => faster decay.
    """
    return math.exp(-(distance_km / sigma))


def normalize(value: Optional[float], min_v=0.0, max_v=1.0) -> float:
    if value is None:
        return 0.0
    val = max(min_v, min(max_v, float(value)))
    if max_v - min_v == 0:
        return 0.0
    return (val - min_v) / (max_v - min_v)


def final_score(semantic: float, geo: float, traffic: float, w_sem=0.5, w_geo=0.25, w_traffic=0.25) -> float:
    return w_sem * semantic + w_geo * geo + w_traffic * traffic
