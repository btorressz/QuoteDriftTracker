"""
Demo mode for Jupiter Quote Tracker - simulates MEV/HFT dynamics
"""

import asyncio
import time
import random
from typing import List
from models import QuoteData
from data_analyzer import DataAnalyzer
from utils import calculate_drift, format_number

class DemoQuoteTracker:
    """Demo version that simulates Jupiter quote tracking"""
    
    def __init__(self, config):
        self.config = config
        self.quotes: List[QuoteData] = []
        self.analyzer = DataAnalyzer()
        self.running = False
        
        # Base price for simulation (USDC per SOL)
        self.base_price = 240.0  # ~$240 per SOL
        self.base_output = int(self.base_price * 1_000_000)  # Convert to micro-USDC
        
        # Statistics tracking
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.start_time = None
        
    def simulate_market_conditions(self) -> tuple:
        """Simulate realistic market conditions"""
        # Simulate price volatility (±0.1% typical)
        price_drift = random.gauss(0, 0.0005)  # Normal distribution around 0
        
        # Simulate network latency (50-300ms typical)
        base_latency = random.uniform(0.05, 0.3)
        
        # Add occasional spikes for MEV opportunities
        if random.random() < 0.05:  # 5% chance of MEV opportunity
            price_drift *= 5  # Amplify price movement
            
        # Simulate latency variations
        latency_variation = random.gauss(0, 0.02)
        actual_latency = max(0.01, base_latency + latency_variation)
        
        return price_drift, actual_latency
    
    async def get_demo_quote(self) -> QuoteData:
        """Generate a simulated quote"""
        request_time = time.time()
        
        # Apply artificial latency injection if configured
        if self.config.latency_injection > 0:
            await asyncio.sleep(self.config.latency_injection)
        
        # Simulate market conditions
        price_drift, network_latency = self.simulate_market_conditions()
        
        # Calculate simulated response time
        await asyncio.sleep(network_latency)
        response_time = time.time()
        
        # Calculate output amount with drift
        drift_multiplier = 1 + price_drift
        output_amount = int(self.base_output * drift_multiplier)
        
        # Simulate occasional failures (2% failure rate)
        if random.random() < 0.02:
            return QuoteData(
                timestamp=request_time,
                request_time=request_time,
                response_time=response_time,
                latency=response_time - request_time,
                output_amount=0,
                price_impact_pct=0.0,
                route_plan=[],
                success=False,
                error="Simulated network error"
            )
        
        # Simulate price impact
        price_impact = random.uniform(0.001, 0.005)  # 0.1% to 0.5%
        
        # Create successful quote
        quote_data = QuoteData(
            timestamp=request_time,
            request_time=request_time,
            response_time=response_time,
            latency=response_time - request_time,
            output_amount=output_amount,
            price_impact_pct=price_impact,
            route_plan=[{"swapInfo": {"inputMint": "So11111111111111111111111111111111111111112"}}],
            success=True
        )
        
        self.successful_requests += 1
        return quote_data
    
    async def demo_worker(self, worker_id: int):
        """Demo worker that simulates quote requests"""
        interval = 1.0 / (self.config.frequency / self.config.concurrent_requests)
        
        while self.running:
            try:
                quote = await self.get_demo_quote()
                self.quotes.append(quote)
                self.total_requests += 1
                
                # Print real-time updates
                if quote.success:
                    drift = 0.0
                    if len(self.quotes) > 1:
                        prev_quote = next((q for q in reversed(self.quotes[:-1]) if q.success), None)
                        if prev_quote:
                            drift = calculate_drift(prev_quote.output_amount, quote.output_amount)
                    
                    status = "🎯 MEV!" if abs(drift) > 0.01 else "📊 Normal"
                    print(f"Worker {worker_id:2d} | "
                          f"Amount: {format_number(quote.output_amount):>12} | "
                          f"Latency: {quote.latency*1000:6.1f}ms | "
                          f"Drift: {drift:+7.4f}% | "
                          f"{status}")
                else:
                    print(f"Worker {worker_id:2d} | ERROR: {quote.error}")
                    self.failed_requests += 1
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                print(f"Worker {worker_id} error: {e}")
                await asyncio.sleep(1)
    
    async def demo_front_running_simulator(self):
        """Simulate front-running detection in demo mode"""
        print("\n🏎️  Front-Running Simulation (Demo Mode)")
        
        while self.running:
            await asyncio.sleep(5)
            
            if len(self.quotes) < 10:
                continue
                
            # Analyze recent quotes for MEV opportunities
            recent_quotes = [q for q in self.quotes[-20:] if q.success]
            if len(recent_quotes) < 5:
                continue
                
            # Find simulated MEV opportunities
            for i in range(1, len(recent_quotes)):
                current = recent_quotes[i]
                previous = recent_quotes[i-1]
                
                timing_advantage = previous.latency - current.latency
                price_drift = calculate_drift(previous.output_amount, current.output_amount)
                
                # Detect significant opportunities
                if timing_advantage > 0.02 and abs(price_drift) > 0.01:
                    profit_potential = abs(price_drift) * self.config.amount / 100
                    
                    print(f"🎯 MEV Opportunity Detected! (Simulated)")
                    print(f"   Timing Advantage: {timing_advantage*1000:.1f}ms")
                    print(f"   Price Drift: {price_drift:+.4f}%")
                    print(f"   Potential Profit: ${profit_potential:.2f}")
    
    def print_demo_statistics(self):
        """Print demo statistics"""
        if not self.quotes:
            return
            
        successful_quotes = [q for q in self.quotes if q.success]
        if len(successful_quotes) < 2:
            return
            
        output_amounts = [q.output_amount for q in successful_quotes]
        latencies = [q.latency for q in successful_quotes]
        
        drifts = []
        for i in range(1, len(successful_quotes)):
            drift = calculate_drift(successful_quotes[i-1].output_amount, 
                                  successful_quotes[i].output_amount)
            drifts.append(drift)
        
        if drifts:
            elapsed = time.time() - self.start_time
            print(f"\n📊 Demo Statistics (Runtime: {elapsed:.1f}s)")
            print(f"   Simulated Requests: {self.total_requests}")
            print(f"   Success Rate: {(self.successful_requests/self.total_requests)*100:.1f}%")
            print(f"   Avg Latency: {sum(latencies)/len(latencies)*1000:.1f}ms")
            print(f"   Price Range: ${min(output_amounts)/1_000_000:.2f} - ${max(output_amounts)/1_000_000:.2f}")
            print(f"   Max Drift: {max(drifts, key=abs):+.4f}%")
            print(f"   MEV Opportunities: {len([d for d in drifts if abs(d) > 0.01])}")
            print("-" * 60)
    
    async def run_demo(self):
        """Run the demo simulation"""
        self.running = True
        self.start_time = time.time()
        
        print("🚀 Jupiter Quote Tracker - DEMO MODE")
        print("📊 Simulating MEV/HFT trading dynamics...")
        print("=" * 60)
        
        try:
            # Create worker tasks
            workers = [
                asyncio.create_task(self.demo_worker(i)) 
                for i in range(self.config.concurrent_requests)
            ]
            
            # Create monitoring tasks
            stats_task = asyncio.create_task(self.demo_statistics_reporter())
            frontrun_task = asyncio.create_task(self.demo_front_running_simulator())
            
            # Run for specified duration
            await asyncio.sleep(self.config.duration)
            
            # Stop all tasks
            self.running = False
            
            # Cancel tasks
            for worker in workers:
                worker.cancel()
            stats_task.cancel()
            frontrun_task.cancel()
            
            # Wait for tasks to complete
            await asyncio.gather(*workers, stats_task, frontrun_task, return_exceptions=True)
            
            # Final analysis
            await self.finalize_demo_analysis()
            
        except KeyboardInterrupt:
            print("\n⏹️  Demo stopped by user")
            self.running = False
    
    async def demo_statistics_reporter(self):
        """Report demo statistics periodically"""
        while self.running:
            await asyncio.sleep(10)
            self.print_demo_statistics()
    
    async def finalize_demo_analysis(self):
        """Perform final analysis of demo data"""
        print("\n🔬 Final Demo Analysis...")
        
        analysis_results = self.analyzer.analyze_quotes(self.quotes)
        
        print(f"\n📋 Demo Results:")
        print(f"   Total Simulated Quotes: {len(self.quotes)}")
        print(f"   Successful Quotes: {len([q for q in self.quotes if q.success])}")
        
        if analysis_results:
            print(f"   Average Latency: {analysis_results['avg_latency']*1000:.1f}ms")
            print(f"   Maximum Drift: {analysis_results['max_drift']:+.4f}%")
            print(f"   MEV Opportunities: {analysis_results['frontrun_opportunities']}")
            print(f"   Price Volatility: {analysis_results['price_volatility']:.2f}%")
        
        print("\n✅ Demo completed successfully!")
        print("🔄 Switch to live mode when Jupiter API rate limit resets")
        
        # Export demo data to CSV
        await self.export_demo_to_csv()
    
    async def export_demo_to_csv(self):
        """Export demo data to CSV file"""
        import csv
        from datetime import datetime
        
        successful_quotes = [q for q in self.quotes if q.success]
        
        if not successful_quotes:
            print("⚠️ No demo quotes to export.")
            return
        
        output_file = f"demo_{self.config.output_file}"
        print(f"💾 Exporting demo data to {output_file}...")
        
        with open(output_file, 'w', newline='') as csvfile:
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
                
                is_mev = abs(drift_pct) > 0.01
                
                writer.writerow({
                    'datetime': datetime.fromtimestamp(quote.timestamp).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                    'timestamp': quote.timestamp,
                    'latency_ms': round(quote.latency * 1000, 2),
                    'output_amount': quote.output_amount,
                    'price_usdc': round(quote.output_amount / 1_000_000, 6),
                    'price_impact_pct': round(quote.price_impact_pct, 4),
                    'drift_pct': round(drift_pct, 4),
                    'is_mev_opportunity': is_mev
                })
                
                previous_amount = quote.output_amount
        
        print(f"✅ Demo data exported! {len(successful_quotes)} quotes saved to {output_file}")