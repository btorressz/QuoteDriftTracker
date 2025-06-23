"""
Web interface for Jupiter Quote Tracker
"""

from flask import Flask, render_template, jsonify, request
import asyncio
import threading
import json
import time
from datetime import datetime
from quote_tracker import QuoteTracker
from demo_mode import DemoQuoteTracker
from config import Config
from models import QuoteData

app = Flask(__name__)

# Global state
tracker_instance = None
tracker_thread = None
tracker_running = False
latest_quotes = []
latest_stats = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/start', methods=['POST'])
def start_tracker():
    global tracker_instance, tracker_thread, tracker_running, latest_quotes, latest_stats
    
    data = request.get_json()
    
    # Create configuration
    config = Config(
        input_mint=data.get('input_mint', 'So11111111111111111111111111111111111111112'),
        output_mint=data.get('output_mint', 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v'),
        amount=int(data.get('amount', 1000000)),
        frequency=float(data.get('frequency', 2.0)),
        duration=int(data.get('duration', 300)),  # 5 minutes default
        concurrent_requests=int(data.get('concurrent_requests', 2)),
        latency_injection=float(data.get('latency_injection', 0.0)),
        slippage_bps=int(data.get('slippage_bps', 50))
    )
    
    demo_mode = data.get('demo_mode', True)
    
    # Initialize tracker
    if demo_mode:
        tracker_instance = DemoQuoteTracker(config)
    else:
        tracker_instance = QuoteTracker(config)
    
    # Clear previous data
    latest_quotes.clear()
    latest_stats.clear()
    
    # Start tracker in separate thread
    tracker_running = True
    tracker_thread = threading.Thread(target=run_tracker_thread, args=(demo_mode,))
    tracker_thread.start()
    
    return jsonify({'status': 'started', 'demo_mode': demo_mode})

@app.route('/api/stop', methods=['POST'])
def stop_tracker():
    global tracker_running, tracker_instance
    
    tracker_running = False
    if tracker_instance:
        tracker_instance.running = False
    
    return jsonify({'status': 'stopped'})

@app.route('/api/data')
def get_data():
    global latest_quotes, latest_stats
    
    # Get recent quotes (last 50)
    recent_quotes = latest_quotes[-50:] if len(latest_quotes) > 50 else latest_quotes
    
    # Format quotes for web display
    formatted_quotes = []
    for quote in recent_quotes:
        formatted_quotes.append({
            'timestamp': datetime.fromtimestamp(quote.timestamp).strftime('%H:%M:%S'),
            'latency': round(quote.latency * 1000, 1),  # Convert to ms
            'output_amount': quote.output_amount,
            'success': quote.success,
            'error': quote.error
        })
    
    # Calculate drift for recent quotes
    if len(recent_quotes) > 1:
        for i in range(1, len(formatted_quotes)):
            if recent_quotes[i].success and recent_quotes[i-1].success:
                prev_amount = recent_quotes[i-1].output_amount
                curr_amount = recent_quotes[i].output_amount
                drift = ((curr_amount - prev_amount) / prev_amount) * 100
                formatted_quotes[i]['drift'] = round(drift, 4)
                formatted_quotes[i]['is_mev'] = abs(drift) > 0.01
            else:
                formatted_quotes[i]['drift'] = 0
                formatted_quotes[i]['is_mev'] = False
    
    return jsonify({
        'quotes': formatted_quotes,
        'stats': latest_stats,
        'running': tracker_running
    })

@app.route('/api/status')
def get_status():
    return jsonify({
        'running': tracker_running,
        'total_quotes': len(latest_quotes),
        'stats': latest_stats
    })

def run_tracker_thread(demo_mode):
    """Run tracker in separate thread"""
    global tracker_instance, latest_quotes, latest_stats, tracker_running
    
    async def tracker_coroutine():
        if demo_mode:
            await run_demo_tracker()
        else:
            await run_live_tracker()
    
    # Run the async tracker
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(tracker_coroutine())
    finally:
        loop.close()

async def run_demo_tracker():
    """Run demo tracker and collect data"""
    global tracker_instance, latest_quotes, latest_stats, tracker_running
    
    await tracker_instance.initialize() if hasattr(tracker_instance, 'initialize') else None
    
    tracker_instance.running = True
    tracker_instance.start_time = time.time()
    
    # Create worker tasks
    workers = [
        asyncio.create_task(demo_worker_wrapper(i)) 
        for i in range(tracker_instance.config.concurrent_requests)
    ]
    
    # Stats reporting task
    stats_task = asyncio.create_task(stats_reporter())
    
    try:
        # Run until stopped
        while tracker_running and tracker_instance.running:
            await asyncio.sleep(1)
            
        # Stop all tasks
        tracker_instance.running = False
        for worker in workers:
            worker.cancel()
        stats_task.cancel()
        
        await asyncio.gather(*workers, stats_task, return_exceptions=True)
        
    except Exception as e:
        print(f"Demo tracker error: {e}")

async def demo_worker_wrapper(worker_id):
    """Wrapper for demo worker that updates global state"""
    global latest_quotes
    
    interval = 1.0 / (tracker_instance.config.frequency / tracker_instance.config.concurrent_requests)
    
    while tracker_instance.running and tracker_running:
        try:
            quote = await tracker_instance.get_demo_quote()
            latest_quotes.append(quote)
            tracker_instance.total_requests += 1
            
            # Keep only last 1000 quotes in memory
            if len(latest_quotes) > 1000:
                latest_quotes = latest_quotes[-500:]
            
            await asyncio.sleep(interval)
            
        except Exception as e:
            print(f"Worker {worker_id} error: {e}")
            await asyncio.sleep(1)

async def run_live_tracker():
    """Run live tracker with Jupiter API"""
    global tracker_instance, latest_quotes, latest_stats, tracker_running
    
    await tracker_instance.initialize()
    
    tracker_instance.running = True
    tracker_instance.start_time = time.time()
    
    # Create worker tasks
    workers = [
        asyncio.create_task(live_worker_wrapper(i)) 
        for i in range(tracker_instance.config.concurrent_requests)
    ]
    
    # Stats reporting task
    stats_task = asyncio.create_task(stats_reporter())
    
    try:
        # Run until stopped
        while tracker_running and tracker_instance.running:
            await asyncio.sleep(1)
            
        # Stop all tasks
        tracker_instance.running = False
        for worker in workers:
            worker.cancel()
        stats_task.cancel()
        
        await asyncio.gather(*workers, stats_task, return_exceptions=True)
        
    finally:
        await tracker_instance.cleanup()

async def live_worker_wrapper(worker_id):
    """Wrapper for live worker that updates global state"""
    global latest_quotes
    
    interval = 1.0 / (tracker_instance.config.frequency / tracker_instance.config.concurrent_requests)
    
    while tracker_instance.running and tracker_running:
        try:
            quote = await tracker_instance.get_quote()
            latest_quotes.append(quote)
            tracker_instance.total_requests += 1
            
            # Keep only last 1000 quotes in memory
            if len(latest_quotes) > 1000:
                latest_quotes = latest_quotes[-500:]
            
            await asyncio.sleep(interval)
            
        except Exception as e:
            print(f"Worker {worker_id} error: {e}")
            await asyncio.sleep(1)

async def stats_reporter():
    """Report statistics periodically"""
    global latest_stats, latest_quotes
    
    while tracker_running and tracker_instance.running:
        try:
            if latest_quotes:
                successful_quotes = [q for q in latest_quotes if q.success]
                
                if len(successful_quotes) > 1:
                    # Calculate basic stats
                    latencies = [q.latency for q in successful_quotes]
                    output_amounts = [q.output_amount for q in successful_quotes]
                    
                    # Calculate drifts
                    drifts = []
                    for i in range(1, len(successful_quotes)):
                        prev_amount = successful_quotes[i-1].output_amount
                        curr_amount = successful_quotes[i].output_amount
                        drift = ((curr_amount - prev_amount) / prev_amount) * 100
                        drifts.append(drift)
                    
                    latest_stats = {
                        'total_requests': len(latest_quotes),
                        'successful_requests': len(successful_quotes),
                        'success_rate': round((len(successful_quotes) / len(latest_quotes)) * 100, 1),
                        'avg_latency_ms': round(sum(latencies) / len(latencies) * 1000, 1),
                        'min_price': round(min(output_amounts) / 1_000_000, 4),
                        'max_price': round(max(output_amounts) / 1_000_000, 4),
                        'mev_opportunities': len([d for d in drifts if abs(d) > 0.01]),
                        'max_drift': round(max(drifts, key=abs) if drifts else 0, 4),
                        'avg_drift': round(sum(drifts) / len(drifts) if drifts else 0, 4),
                        'runtime': round(time.time() - tracker_instance.start_time, 1)
                    }
        
        except Exception as e:
            print(f"Stats reporter error: {e}")
        
        await asyncio.sleep(2)  # Update every 2 seconds

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)