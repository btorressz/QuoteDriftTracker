"""
Data models for the Jupiter Quote Tracker
"""

from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class QuoteData:
    """Data structure for storing quote information"""
    timestamp: float
    request_time: float
    response_time: float
    latency: float
    output_amount: int
    price_impact_pct: float
    route_plan: List[Dict]
    success: bool
    error: Optional[str] = None