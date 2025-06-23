"""
Utility functions for the Jupiter Quote Tracker
"""

import time
from typing import Union, List, Optional
from datetime import datetime, timezone

def calculate_drift(previous_amount: int, current_amount: int) -> float:
    """
    Calculate percentage drift between two amounts
    
    Args:
        previous_amount: Previous quote amount
        current_amount: Current quote amount
        
    Returns:
        Percentage drift (positive = increase, negative = decrease)
    """
    if previous_amount == 0:
        return 0.0
    
    return ((current_amount - previous_amount) / previous_amount) * 100

def format_number(number: Union[int, float], decimals: int = 0) -> str:
    """
    Format number with thousands separators
    
    Args:
        number: Number to format
        decimals: Number of decimal places
        
    Returns:
        Formatted number string
    """
    if decimals == 0:
        return f"{int(number):,}"
    else:
        return f"{number:,.{decimals}f}"

def format_percentage(value: float, decimals: int = 4) -> str:
    """
    Format percentage value with sign
    
    Args:
        value: Percentage value
        decimals: Number of decimal places
        
    Returns:
        Formatted percentage string with sign
    """
    return f"{value:+.{decimals}f}%"

def format_latency(latency_seconds: float) -> str:
    """
    Format latency in appropriate units
    
    Args:
        latency_seconds: Latency in seconds
        
    Returns:
        Formatted latency string
    """
    latency_ms = latency_seconds * 1000
    
    if latency_ms < 1:
        return f"{latency_ms*1000:.1f}μs"
    elif latency_ms < 1000:
        return f"{latency_ms:.1f}ms"
    else:
        return f"{latency_seconds:.2f}s"

def format_timestamp(timestamp: float, include_microseconds: bool = True) -> str:
    """
    Format timestamp for display
    
    Args:
        timestamp: Unix timestamp
        include_microseconds: Whether to include microseconds
        
    Returns:
        Formatted timestamp string
    """
    dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    
    if include_microseconds:
        return dt.strftime('%H:%M:%S.%f')[:-3]  # Remove last 3 digits of microseconds
    else:
        return dt.strftime('%H:%M:%S')

def calculate_statistics(values: List[float]) -> dict:
    """
    Calculate basic statistics for a list of values
    
    Args:
        values: List of numeric values
        
    Returns:
        Dictionary with statistical measures
    """
    if not values:
        return {}
    
    import numpy as np
    
    return {
        'count': len(values),
        'mean': np.mean(values),
        'median': np.median(values),
        'std_dev': np.std(values),
        'variance': np.var(values),
        'min': np.min(values),
        'max': np.max(values),
        'range': np.max(values) - np.min(values),
        'sum': np.sum(values)
    }

def convert_lamports_to_sol(lamports: int) -> float:
    """
    Convert lamports to SOL
    
    Args:
        lamports: Amount in lamports
        
    Returns:
        Amount in SOL
    """
    return lamports / 1_000_000_000

def convert_sol_to_lamports(sol: float) -> int:
    """
    Convert SOL to lamports
    
    Args:
        sol: Amount in SOL
        
    Returns:
        Amount in lamports
    """
    return int(sol * 1_000_000_000)

def convert_usdc_to_micro_usdc(usdc: float) -> int:
    """
    Convert USDC to micro-USDC (smallest unit)
    
    Args:
        usdc: Amount in USDC
        
    Returns:
        Amount in micro-USDC
    """
    return int(usdc * 1_000_000)

def convert_micro_usdc_to_usdc(micro_usdc: int) -> float:
    """
    Convert micro-USDC to USDC
    
    Args:
        micro_usdc: Amount in micro-USDC
        
    Returns:
        Amount in USDC
    """
    return micro_usdc / 1_000_000

def detect_outliers(values: List[float], z_threshold: float = 2.0) -> List[int]:
    """
    Detect outliers using z-score method
    
    Args:
        values: List of numeric values
        z_threshold: Z-score threshold for outlier detection
        
    Returns:
        List of indices of outlier values
    """
    if len(values) < 3:
        return []
    
    import numpy as np
    
    mean = np.mean(values)
    std_dev = np.std(values)
    
    if std_dev == 0:
        return []
    
    outliers = []
    for i, value in enumerate(values):
        z_score = abs(value - mean) / std_dev
        if z_score > z_threshold:
            outliers.append(i)
    
    return outliers

def calculate_moving_average(values: List[float], window_size: int) -> List[float]:
    """
    Calculate moving average
    
    Args:
        values: List of numeric values
        window_size: Size of moving window
        
    Returns:
        List of moving average values
    """
    if len(values) < window_size:
        return values[:]
    
    moving_averages = []
    for i in range(len(values) - window_size + 1):
        window = values[i:i + window_size]
        avg = sum(window) / window_size
        moving_averages.append(avg)
    
    return moving_averages

def estimate_gas_cost_sol(base_cost: float = 0.000005) -> float:
    """
    Estimate transaction gas cost in SOL
    
    Args:
        base_cost: Base transaction cost in SOL
        
    Returns:
        Estimated gas cost in SOL
    """
    # Simple estimation - in reality this would depend on current network conditions
    return base_cost

def calculate_profit_potential(
    price_difference: float, 
    amount: int, 
    gas_cost: float = 0.000005
) -> dict:
    """
    Calculate profit potential for MEV opportunity
    
    Args:
        price_difference: Price difference as percentage
        amount: Trade amount
        gas_cost: Estimated gas cost
        
    Returns:
        Dictionary with profit analysis
    """
    absolute_difference = abs(price_difference) / 100 * amount
    net_profit = absolute_difference - gas_cost
    
    return {
        'gross_profit': absolute_difference,
        'gas_cost': gas_cost,
        'net_profit': net_profit,
        'is_profitable': net_profit > 0,
        'profit_margin': net_profit / amount * 100 if amount > 0 else 0
    }

def format_duration(seconds: float) -> str:
    """
    Format duration in human readable format
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"

def validate_solana_address(address: str) -> bool:
    """
    Validate Solana address format
    
    Args:
        address: Address string to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        if len(address) < 32 or len(address) > 44:
            return False
        
        # Check if it contains only valid base58 characters
        valid_chars = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
        return all(c in valid_chars for c in address)
    except:
        return False

def create_progress_bar(current: int, total: int, width: int = 50) -> str:
    """
    Create a text-based progress bar
    
    Args:
        current: Current progress value
        total: Total value
        width: Width of progress bar in characters
        
    Returns:
        Progress bar string
    """
    if total == 0:
        return '[' + '=' * width + ']'
    
    progress = current / total
    filled = int(width * progress)
    bar = '=' * filled + '-' * (width - filled)
    percentage = progress * 100
    
    return f'[{bar}] {percentage:.1f}%'

def rate_limiter(calls_per_second: float):
    """
    Simple rate limiter decorator
    
    Args:
        calls_per_second: Maximum calls per second
        
    Returns:
        Decorator function
    """
    min_interval = 1.0 / calls_per_second
    last_called = [0.0]
    
    def decorator(func):
        def wrapper(*args, **kwargs):
            now = time.time()
            time_passed = now - last_called[0]
            
            if time_passed < min_interval:
                time.sleep(min_interval - time_passed)
            
            last_called[0] = time.time()
            return func(*args, **kwargs)
        
        return wrapper
    return decorator
