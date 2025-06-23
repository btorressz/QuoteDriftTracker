# 📈 Quote Drift Tracker

## 🧠 Overview

**Quote Drift Tracker** is a Python-based application designed to analyze MEV (Maximal Extractable Value) and HFT (High-Frequency Trading) dynamics on the Solana blockchain through Jupiter DEX quote monitoring.  
The application continuously monitors Jupiter DEX quote latency and price drift to identify potential front-running opportunities and trading inefficiencies.

It operates by making concurrent API requests to Jupiter’s quote endpoint, tracking response times, price movements, and calculating statistical metrics to detect patterns that could indicate MEV opportunities.

---

## 🏗️ System Architecture

### 🔧 Core Architecture
- 🌀 **Asynchronous Python Application** – Built using `asyncio` for concurrent quote fetching  
- 🧩 **Modular Design** – Separated concerns across multiple modules (tracking, analysis, config, utils)  
- 📊 **Data-Driven Analysis** – Real-time statistical analysis of quote data and latency patterns  
- 🖥️ **CLI Interface** – Command-line interface for configurable execution parameters

  ### 🛠️ Technology Stack
- 🐍 **Python 3.11**
- 🌐 **aiohttp** – Async HTTP client for fetching quotes  
- 🌶️ **Flask** – Dashboard interface (optional)  
- 📐 **numpy** – For numerical computation  
- ⚙️ **asyncio** – For high-frequency concurrent requests

  ---

## 🧩 Key Components

### 1️⃣ Quote Tracker (`quote_tracker.py`)
- 🎯 **Purpose**: Fetch and store Jupiter quotes  
- 📦 **Responsibilities**:
  - Managing HTTP sessions & requests  
  - Tracking latency and response times  
  - Storing quote data in a structured format  
- 🌟 **Key Features**: Concurrent request handling, error tracking, performance monitoring  

### 2️⃣ Data Analyzer (`data_analyzer.py`)
- 📈 **Purpose**: Analyze collected quote data  
- 📊 **Responsibilities**:
  - Calculate price drift  
  - Identify MEV opportunities  
  - Compute averages, percentiles, success rates  
- 🧮 **Thresholds**:  
  - Drift: `0.01%`  
  - Latency advantage: `50ms`  

### 3️⃣ Configuration Management (`config.py`)
- ⚙️ **Purpose**: Centralized and validated settings  
- 🧵 **Defaults**:
  - Trading pair: `SOL → USDC`  
  - Swap amount: `1 SOL (1,000,000 lamports)`  
  - RPS: `5 requests/sec`  
  - Duration: `60 seconds`  
  - Workers: `10 concurrent`  
  - Slippage: `0.5%`  

### 4️⃣ Utilities (`utils.py`)
- 🛠️ **Purpose**: Helper functions  
- 🔢 **Functions**:
  - Price drift calculations  
  - Number formatting  
  - Percent formatting  

---

## 🔄 Data Flow

1. 🚀 **Initialization** – Load config & setup HTTP session  
2. 🔁 **Quote Fetching** – Concurrent calls to Jupiter API  
3. 📥 **Data Collection** – Capture times, prices, metadata  
4. 📉 **Real-Time Analysis** – Run statistical processing  
5. 📤 **Results Output** – Export to CSV with formatting  

---

### 🧾 Quote Data Structure

```python
@dataclass
class QuoteData:
    timestamp: float
    request_time: float
    response_time: float
    latency: float
    output_amount: int
    price_impact_pct: float
    route_plan: List[Dict]
    success: bool
    error: Optional[str]

