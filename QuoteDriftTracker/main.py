#!/usr/bin/env python3
"""
Jupiter Quote Latency Drift Tracker
Main entry point for the MEV/HFT trading dynamics simulation
"""

import asyncio
import argparse
import sys
from datetime import datetime
from quote_tracker import QuoteTracker
from demo_mode import DemoQuoteTracker
from config import Config

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Jupiter Quote Latency Drift Tracker - Analyze MEV/HFT trading dynamics'
    )
    
    parser.add_argument(
        '--input-mint', 
        default='So11111111111111111111111111111111111112',  # SOL
        help='Input token mint address (default: SOL)'
    )
    
    parser.add_argument(
        '--output-mint',
        default='EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',  # USDC
        help='Output token mint address (default: USDC)'
    )
    
    parser.add_argument(
        '--amount',
        type=int,
        default=1000000,  # 1 SOL in lamports
        help='Swap amount in smallest unit (default: 1000000 lamports = 1 SOL)'
    )
    
    parser.add_argument(
        '--frequency',
        type=float,
        default=5.0,
        help='Requests per second (default: 5.0)'
    )
    
    parser.add_argument(
        '--duration',
        type=int,
        default=60,
        help='Test duration in seconds (default: 60)'
    )
    
    parser.add_argument(
        '--latency-injection',
        type=float,
        default=0.0,
        help='Artificial latency injection in seconds (default: 0.0)'
    )
    
    parser.add_argument(
        '--output-file',
        default=f'quote_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
        help='Output CSV file name'
    )
    
    parser.add_argument(
        '--concurrent-requests',
        type=int,
        default=10,
        help='Number of concurrent requests (default: 10)'
    )
    
    parser.add_argument(
        '--slippage-bps',
        type=int,
        default=50,
        help='Slippage in basis points (default: 50)'
    )
    
    parser.add_argument(
        '--demo-mode',
        action='store_true',
        help='Run in demo mode with simulated data'
    )
    
    return parser.parse_args()

async def main():
    """Main execution function"""
    args = parse_arguments()
    
    # Create configuration
    config = Config(
        input_mint=args.input_mint,
        output_mint=args.output_mint,
        amount=args.amount,
        frequency=args.frequency,
        duration=args.duration,
        latency_injection=args.latency_injection,
        output_file=args.output_file,
        concurrent_requests=args.concurrent_requests,
        slippage_bps=args.slippage_bps
    )
    
    print("🚀 Jupiter Quote Latency Drift Tracker Starting...")
    print(f"📊 Configuration:")
    print(f"   Input Token: {config.input_mint}")
    print(f"   Output Token: {config.output_mint}")
    print(f"   Amount: {config.amount}")
    print(f"   Frequency: {config.frequency} req/sec")
    print(f"   Duration: {config.duration} seconds")
    print(f"   Concurrent Requests: {config.concurrent_requests}")
    print(f"   Latency Injection: {config.latency_injection}s")
    print(f"   Output File: {config.output_file}")
    print("=" * 60)
    
    # Choose between demo mode and live mode
    if args.demo_mode:
        print("🎮 Running in DEMO MODE - Simulated MEV/HFT dynamics")
        tracker = DemoQuoteTracker(config)
        try:
            await tracker.run_demo()
        except KeyboardInterrupt:
            print("\n⏹️  Demo stopped by user")
    else:
        print("🌐 Running in LIVE MODE - Real Jupiter API data")
        tracker = QuoteTracker(config)
        try:
            await tracker.run()
            print("\n✅ Analysis completed successfully!")
            print(f"📁 Results saved to: {config.output_file}")
        except KeyboardInterrupt:
            print("\n⏹️  Analysis stopped by user")
            await tracker.stop()
        except Exception as e:
            print(f"\n❌ Error during analysis: {e}")
            if "rate limit" in str(e).lower():
                print("💡 Try using --demo-mode to see simulated MEV dynamics")
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
