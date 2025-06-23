"""
Data Analyzer - Statistical analysis of quote data
"""

import numpy as np
from typing import List, Dict, Optional
from models import QuoteData
from utils import calculate_drift

class DataAnalyzer:
    """Analyzes quote data for latency drift and MEV opportunities"""
    
    def __init__(self):
        self.drift_threshold = 0.01  # 0.01% drift threshold for front-running
        self.latency_advantage_threshold = 0.05  # 50ms advantage threshold
        
    def analyze_quotes(self, quotes: List[QuoteData]) -> Optional[Dict]:
        """Perform comprehensive analysis on quote data"""
        if not quotes:
            return None
            
        successful_quotes = [q for q in quotes if q.success]
        if len(successful_quotes) < 2:
            return None
            
        # Extract data arrays
        output_amounts = [q.output_amount for q in successful_quotes]
        latencies = [q.latency for q in successful_quotes]
        timestamps = [q.timestamp for q in successful_quotes]
        
        # Calculate drifts
        drifts = []
        for i in range(1, len(successful_quotes)):
            drift = calculate_drift(successful_quotes[i-1].output_amount, 
                                  successful_quotes[i].output_amount)
            drifts.append(drift)
        
        if not drifts:
            return None
            
        # Calculate statistics
        results = {
            'total_quotes': len(quotes),
            'successful_quotes': len(successful_quotes),
            'failed_quotes': len(quotes) - len(successful_quotes),
            'success_rate': len(successful_quotes) / len(quotes) * 100,
            
            # Latency statistics
            'avg_latency': np.mean(latencies),
            'min_latency': np.min(latencies),
            'max_latency': np.max(latencies),
            'latency_std_dev': np.std(latencies),
            
            # Output amount statistics
            'avg_output_amount': np.mean(output_amounts),
            'min_output_amount': np.min(output_amounts),
            'max_output_amount': np.max(output_amounts),
            'output_amount_std_dev': np.std(output_amounts),
            
            # Drift statistics
            'avg_drift': np.mean(drifts),
            'min_drift': np.min(drifts),
            'max_drift': np.max(drifts),
            'drift_std_dev': np.std(drifts),
            'drift_variance': np.var(drifts),
            
            # Price variance and volatility
            'price_variance': np.var(output_amounts),
            'price_volatility': np.std(output_amounts) / np.mean(output_amounts) * 100,
            
            # MEV/Front-running analysis
            'frontrun_opportunities': self.analyze_frontrun_opportunities(successful_quotes),
            'latency_price_correlation': self.calculate_latency_price_correlation(successful_quotes),
            
            # Time-based analysis
            'duration': timestamps[-1] - timestamps[0],
            'avg_request_interval': self.calculate_avg_interval(timestamps),
            
            # Drift distribution
            'positive_drifts': len([d for d in drifts if d > 0]),
            'negative_drifts': len([d for d in drifts if d < 0]),
            'significant_drifts': len([d for d in drifts if abs(d) > self.drift_threshold]),
        }
        
        # Calculate percentiles
        results.update(self.calculate_drift_percentiles(drifts))
        results.update(self.calculate_latency_percentiles(latencies))
        
        return results
    
    def analyze_frontrun_opportunities(self, quotes: List[QuoteData]) -> int:
        """Analyze potential front-running opportunities"""
        opportunities = 0
        
        for i in range(1, len(quotes)):
            current = quotes[i]
            previous = quotes[i-1]
            
            # Calculate timing advantage
            timing_advantage = previous.latency - current.latency
            
            # Calculate price drift
            price_drift = calculate_drift(previous.output_amount, current.output_amount)
            
            # Check if this represents a front-running opportunity
            if (timing_advantage > self.latency_advantage_threshold and 
                abs(price_drift) > self.drift_threshold):
                opportunities += 1
                
        return opportunities
    
    def calculate_latency_price_correlation(self, quotes: List[QuoteData]) -> float:
        """Calculate correlation between latency and price changes"""
        if len(quotes) < 3:
            return 0.0
            
        latencies = []
        price_changes = []
        
        for i in range(1, len(quotes)):
            current = quotes[i]
            previous = quotes[i-1]
            
            latencies.append(current.latency)
            price_change = calculate_drift(previous.output_amount, current.output_amount)
            price_changes.append(abs(price_change))  # Use absolute value for volatility correlation
        
        if len(latencies) < 2:
            return 0.0
            
        correlation = np.corrcoef(latencies, price_changes)[0, 1]
        return correlation if not np.isnan(correlation) else 0.0
    
    def calculate_avg_interval(self, timestamps: List[float]) -> float:
        """Calculate average interval between requests"""
        if len(timestamps) < 2:
            return 0.0
            
        intervals = [timestamps[i] - timestamps[i-1] for i in range(1, len(timestamps))]
        return np.mean(intervals)
    
    def calculate_drift_percentiles(self, drifts: List[float]) -> Dict[str, float]:
        """Calculate drift percentiles"""
        if not drifts:
            return {}
            
        return {
            'drift_p10': np.percentile(drifts, 10),
            'drift_p25': np.percentile(drifts, 25),
            'drift_p50': np.percentile(drifts, 50),
            'drift_p75': np.percentile(drifts, 75),
            'drift_p90': np.percentile(drifts, 90),
            'drift_p95': np.percentile(drifts, 95),
            'drift_p99': np.percentile(drifts, 99),
        }
    
    def calculate_latency_percentiles(self, latencies: List[float]) -> Dict[str, float]:
        """Calculate latency percentiles"""
        if not latencies:
            return {}
            
        # Convert to milliseconds
        latencies_ms = [l * 1000 for l in latencies]
        
        return {
            'latency_p10_ms': np.percentile(latencies_ms, 10),
            'latency_p25_ms': np.percentile(latencies_ms, 25),
            'latency_p50_ms': np.percentile(latencies_ms, 50),
            'latency_p75_ms': np.percentile(latencies_ms, 75),
            'latency_p90_ms': np.percentile(latencies_ms, 90),
            'latency_p95_ms': np.percentile(latencies_ms, 95),
            'latency_p99_ms': np.percentile(latencies_ms, 99),
        }
    
    def calculate_std_dev(self, values: List[float]) -> float:
        """Calculate standard deviation with error handling"""
        if not values or len(values) < 2:
            return 0.0
        return float(np.std(values))
    
    def detect_price_anomalies(self, quotes: List[QuoteData], z_threshold: float = 2.0) -> List[Dict]:
        """Detect price anomalies using z-score analysis"""
        successful_quotes = [q for q in quotes if q.success]
        if len(successful_quotes) < 10:
            return []
            
        output_amounts = [q.output_amount for q in successful_quotes]
        mean_amount = np.mean(output_amounts)
        std_amount = np.std(output_amounts)
        
        anomalies = []
        
        for i, quote in enumerate(successful_quotes):
            z_score = abs(quote.output_amount - mean_amount) / std_amount
            
            if z_score > z_threshold:
                anomalies.append({
                    'timestamp': quote.timestamp,
                    'output_amount': quote.output_amount,
                    'z_score': z_score,
                    'deviation_pct': (quote.output_amount - mean_amount) / mean_amount * 100,
                    'latency_ms': quote.latency * 1000
                })
        
        return anomalies
    
    def calculate_mev_profitability(self, quotes: List[QuoteData], gas_cost: float = 0.01) -> Dict:
        """Calculate potential MEV profitability metrics"""
        successful_quotes = [q for q in quotes if q.success]
        if len(successful_quotes) < 2:
            return {}
            
        profitable_opportunities = 0
        total_potential_profit = 0.0
        
        for i in range(1, len(successful_quotes)):
            current = quotes[i]
            previous = quotes[i-1]
            
            # Calculate potential arbitrage profit
            price_diff = current.output_amount - previous.output_amount
            profit_potential = abs(price_diff) - gas_cost  # Subtract estimated gas cost
            
            if profit_potential > 0:
                profitable_opportunities += 1
                total_potential_profit += profit_potential
        
        return {
            'profitable_opportunities': profitable_opportunities,
            'total_potential_profit': total_potential_profit,
            'avg_profit_per_opportunity': total_potential_profit / max(profitable_opportunities, 1),
            'profitability_rate': profitable_opportunities / len(successful_quotes) * 100
        }
