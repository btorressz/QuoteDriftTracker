"""
Quote Tracker - Core functionality for tracking Jupiter API quotes
"""

import asyncio
import aiohttp
import time
import json
from datetime import datetime
from typing import List, Dict, Optional
from data_analyzer import DataAnalyzer
from utils import calculate_drift, format_number
from config import Config
from models import QuoteData

class QuoteTracker:
    """Main class for tracking Jupiter quote latency and drift"""
    
    def __init__(self, config: Config):
        self.config = config
        self.quotes: List[QuoteData] = []
        self.analyzer = DataAnalyzer()
        self.session: Optional[aiohttp.ClientSession] = None
        self.running = False
        
        # Jupiter API configuration
        self.base_url = "https://quote-api.jup.ag/v6"
        self.quote_endpoint = f"{self.base_url}/quote"
        
        # Statistics tracking
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.start_time = None
        
    async def initialize(self):
        """Initialize HTTP session and other resources"""
        timeout = aiohttp.ClientTimeout(total=10, connect=5)
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=30)
        
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'User-Agent': 'Jupiter-Quote-Tracker/1.0'
            }
        )
        
    async def cleanup(self):
        """Clean up resources"""
        if self.session:
            await self.session.close()
            
    async def get_quote(self) -> QuoteData:
        """Get a single quote from Jupiter API"""
        request_time = time.time()
        
        # Apply artificial latency injection if configured
        if self.config.latency_injection > 0:
            await asyncio.sleep(self.config.latency_injection)
        
        params = {
            'inputMint': self.config.input_mint,
            'outputMint': self.config.output_mint,
            'amount': str(self.config.amount),
            'slippageBps': str(self.config.slippage_bps),
            'onlyDirectRoutes': 'false',
            'asLegacyTransaction': 'false'
        }
        
        try:
            async with self.session.get(self.quote_endpoint, params=params) as response:
                response_time = time.time()
                latency = response_time - request_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    quote_data = QuoteData(
                        timestamp=request_time,
                        request_time=request_time,
                        response_time=response_time,
                        latency=latency,
                        output_amount=int(data.get('outAmount', 0)),
                        price_impact_pct=float(data.get('priceImpactPct', 0)),
                        route_plan=data.get('routePlan', []),
                        success=True
                    )
                    
                    self.successful_requests += 1
                    return quote_data
                    
                else:
                    error_text = await response.text()
                    
                    # Handle rate limiting
                    if response.status == 429:
                        await asyncio.sleep(2)  # Wait longer for rate limit
                    
                    quote_data = QuoteData(
                        timestamp=request_time,
                        request_time=request_time,
                        response_time=response_time,
                        latency=latency,
                        output_amount=0,
                        price_impact_pct=0.0,
                        route_plan=[],
                        success=False,
                        error=f"HTTP {response.status}: {error_text}"
                    )
                    
                    self.failed_requests += 1
                    return quote_data
                    
        except Exception as e:
            response_time = time.time()
            latency = response_time - request_time
            
            quote_data = QuoteData(
                timestamp=request_time,
                request_time=request_time,
                response_time=response_time,
                latency=latency,
                output_amount=0,
                price_impact_pct=0.0,
                route_plan=[],
                success=False,
                error=str(e)
            )
            
            self.failed_requests += 1
            return quote_data
            
    async def quote_worker(self, worker_id: int):
        """Worker coroutine for making quote requests"""
        interval = 1.0 / (self.config.frequency / self.config.concurrent_requests)
        
        while self.running:
            try:
                quote = await self.get_quote()
                self.quotes.append(quote)
                self.total_requests += 1
                
                # Print real-time updates
                if quote.success:
                    drift = 0.0
                    if len(self.quotes) > 1:
                        prev_quote = next((q for q in reversed(self.quotes[:-1]) if q.success), None)
                        if prev_quote:
                            drift = calculate_drift(prev_quote.output_amount, quote.output_amount)
                    
                    print(f"Worker {worker_id:2d} | "
                          f"Amount: {format_number(quote.output_amount):>12} | "
                          f"Latency: {quote.latency*1000:6.1f}ms | "
                          f"Drift: {drift:+7.4f}% | "
                          f"Success: {self.successful_requests:4d} | "
                          f"Failed: {self.failed_requests:3d}")
                else:
                    print(f"Worker {worker_id:2d} | ERROR: {quote.error}")
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                print(f"Worker {worker_id} error: {e}")
                await asyncio.sleep(1)
                
    def print_statistics(self):
        """Print real-time statistics"""
        if not self.quotes:
            return
            
        successful_quotes = [q for q in self.quotes if q.success]
        if len(successful_quotes) < 2:
            return
            
        # Calculate basic statistics
        output_amounts = [q.output_amount for q in successful_quotes]
        latencies = [q.latency for q in successful_quotes]
        
        # Calculate drifts
        drifts = []
        for i in range(1, len(successful_quotes)):
            drift = calculate_drift(successful_quotes[i-1].output_amount, 
                                  successful_quotes[i].output_amount)
            drifts.append(drift)
        
        if drifts:
            elapsed = time.time() - self.start_time
            print(f"\n📊 Statistics (Runtime: {elapsed:.1f}s)")
            print(f"   Total Requests: {self.total_requests}")
            print(f"   Success Rate: {(self.successful_requests/self.total_requests)*100:.1f}%")
            print(f"   Avg Latency: {sum(latencies)/len(latencies)*1000:.1f}ms")
            print(f"   Output Amount Range: {min(output_amounts):,} - {max(output_amounts):,}")
            print(f"   Max Drift: {max(drifts, key=abs):+.4f}%")
            print(f"   Avg Drift: {sum(drifts)/len(drifts):+.4f}%")
            print(f"   Drift StdDev: {self.analyzer.calculate_std_dev(drifts):.4f}%")
            print("-" * 60)
    
    async def statistics_reporter(self):
        """Coroutine for periodic statistics reporting"""
        while self.running:
            await asyncio.sleep(10)  # Report every 10 seconds
            self.print_statistics()
            
    async def front_running_simulator(self):
        """Simulate front-running scenarios based on quote timing"""
        print("\n🏎️  Front-Running Simulation Starting...")
        
        while self.running:
            await asyncio.sleep(5)  # Check every 5 seconds
            
            if len(self.quotes) < 10:
                continue
                
            # Get recent successful quotes
            recent_quotes = [q for q in self.quotes[-20:] if q.success]
            if len(recent_quotes) < 5:
                continue
                
            # Find quotes with significant advantages
            for i in range(1, len(recent_quotes)):
                current = recent_quotes[i]
                previous = recent_quotes[i-1]
                
                # Calculate timing advantage
                timing_advantage = previous.latency - current.latency
                
                # Calculate price advantage
                price_drift = calculate_drift(previous.output_amount, current.output_amount)
                
                # Simulate front-running opportunity
                if timing_advantage > 0.05 and abs(price_drift) > 0.01:  # 50ms advantage, 0.01% drift
                    profit_potential = abs(price_drift) * self.config.amount
                    
                    print(f"🎯 Front-Run Opportunity Detected!")
                    print(f"   Timing Advantage: {timing_advantage*1000:.1f}ms")
                    print(f"   Price Drift: {price_drift:+.4f}%")
                    print(f"   Potential Profit: {profit_potential:.0f} units")
                    print(f"   Timestamp: {datetime.fromtimestamp(current.timestamp).strftime('%H:%M:%S.%f')[:-3]}")
                    
    async def run(self):
        """Main execution method"""
        await self.initialize()
        
        self.running = True
        self.start_time = time.time()
        
        try:
            # Create worker tasks
            workers = [
                asyncio.create_task(self.quote_worker(i)) 
                for i in range(self.config.concurrent_requests)
            ]
            
            # Create monitoring tasks
            stats_task = asyncio.create_task(self.statistics_reporter())
            frontrun_task = asyncio.create_task(self.front_running_simulator())
            
            # Run for specified duration
            await asyncio.sleep(self.config.duration)
            
            # Stop all tasks
            await self.stop()
            
            # Cancel tasks
            for worker in workers:
                worker.cancel()
            stats_task.cancel()
            frontrun_task.cancel()
            
            # Wait for tasks to complete
            await asyncio.gather(*workers, stats_task, frontrun_task, return_exceptions=True)
            
            # Final analysis and export
            await self.finalize_analysis()
            
        finally:
            await self.cleanup()
            
    async def stop(self):
        """Stop the tracking process"""
        self.running = False
        
    async def finalize_analysis(self):
        """Perform final analysis and export results"""
        print("\n🔬 Performing Final Analysis...")
        
        # Analyze all collected data
        analysis_results = self.analyzer.analyze_quotes(self.quotes)
        
        # Print final statistics
        print(f"\n📋 Final Results:")
        print(f"   Total Quotes Collected: {len(self.quotes)}")
        print(f"   Successful Quotes: {len([q for q in self.quotes if q.success])}")
        print(f"   Failed Quotes: {len([q for q in self.quotes if not q.success])}")
        
        if analysis_results:
            print(f"   Average Latency: {analysis_results['avg_latency']*1000:.1f}ms")
            print(f"   Maximum Drift: {analysis_results['max_drift']:+.4f}%")
            print(f"   Average Drift: {analysis_results['avg_drift']:+.4f}%")
            print(f"   Drift Standard Deviation: {analysis_results['drift_std_dev']:.4f}%")
            print(f"   Quote Variance: {analysis_results['price_variance']:.2f}")
            print(f"   Front-Run Opportunities: {analysis_results['frontrun_opportunities']}")
        
        # Export to CSV
        await self.export_to_csv()
        
    async def export_to_csv(self):
        """Export collected data to CSV file"""
        import csv
        from datetime import datetime
        
        print(f"💾 Exporting data to {self.config.output_file}...")
        
        # Filter out failed requests for cleaner CSV export
        successful_quotes = [q for q in self.quotes if q.success]
        
        if not successful_quotes:
            print("⚠️ No successful quotes to export. All requests failed.")
            return
        
        with open(self.config.output_file, 'w', newline='') as csvfile:
            fieldnames = [
                'datetime', 'timestamp', 'latency_ms', 'output_amount', 
                'price_usdc', 'price_impact_pct', 'drift_pct', 'is_mev_opportunity'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            previous_amount = None
            
            for quote in successful_quotes:
                drift_pct = 0.0
                if previous_amount:
                    drift_pct = calculate_drift(previous_amount, quote.output_amount)
                
                is_mev = abs(drift_pct) > 0.01  # MEV opportunity threshold
                
                writer.writerow({
                    'datetime': datetime.fromtimestamp(quote.timestamp).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                    'timestamp': quote.timestamp,
                    'latency_ms': round(quote.latency * 1000, 2),
                    'output_amount': quote.output_amount,
                    'price_usdc': round(quote.output_amount / 1_000_000, 6),  # Convert to USDC
                    'price_impact_pct': round(quote.price_impact_pct, 4),
                    'drift_pct': round(drift_pct, 4),
                    'is_mev_opportunity': is_mev
                })
                
                previous_amount = quote.output_amount
        
        print(f"✅ Data exported successfully! {len(successful_quotes)} successful quotes saved.")
