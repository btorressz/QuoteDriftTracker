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

The `QuoteData` structure is a container that stores detailed information about each individual quote received from the Jupiter API. Each quote record includes the following fields:

- **Timestamp**: The exact time (in seconds) when the quote was recorded.

- **Request Time**: The moment when the request to the Jupiter API was initiated.

- **Response Time**: The moment when the response was received from the Jupiter API.

- **Latency**: The total time it took (in seconds) between sending the request and receiving the response — a key metric for tracking speed and potential MEV timing advantages.

- **Output Amount**: The amount of the output token (e.g., USDC) that would be received from the trade at the quoted rate.

- **Price Impact Percentage**: A numerical value indicating how much the quote affects the market price — useful for understanding slippage and trade efficiency.

- **Route Plan**: A list of routes (with metadata) that Jupiter uses to execute the swap. This might include details like the DEXs involved or token paths taken.

- **Success**: A Boolean flag (`True` or `False`) indicating whether the quote request was successful.

- **Error** *(optional)*: If the quote failed, this field contains a description of the error for debugging or logging purposes.


---

## 🔌 External Dependencies

### 🌐 Jupiter API Integration
- **Endpoint**: [`https://quote-api.jup.ag/v6/quote`](https://quote-api.jup.ag/v6/quote)
- 🔍 **Purpose**: Real-time Solana DEX price quotes
- 📊 **Rate Limiting**: Configurable RPS and timeout control
- 🔁 **Error Handling**: Retry with exponential backoff

### 🪙 Token Configuration
- 💰 **Input Token**: `SOL` (`So11111111111111111111111111111111111112`)
- 💵 **Output Token**: `USDC` (`EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v`)
- 🧠 **Customizable**: Supports all SPL token pairs

  ---

  ## 🧾📜 LICENSE
  - This project is under the **MIT LICENSE**

  ---

  ## 📸 Screenshots
  
![Quote Drift Tracker Screenshot](https://github.com/btorressz/QuoteDriftTracker/blob/main/quotedrifttracker1.jpg?raw=true)


![Quote Drift Tracker Screenshot](https://github.com/btorressz/QuoteDriftTracker/blob/main/quotedrifttracker2.jpg?raw=true)


![Quote Drift Tracker Screenshot](https://github.com/btorressz/QuoteDriftTracker/blob/main/quotedrifttracker3.jpg?raw=true)


![Quote Drift Tracker Screenshot](https://github.com/btorressz/QuoteDriftTracker/blob/main/quotedrifttracker4.jpg?raw=true)




![Demo Screenshot](https://github.com/btorressz/QuoteDriftTracker/blob/main/demoscreenshot1.jpg?raw=true)


![Demo Screenshot](https://github.com/btorressz/QuoteDriftTracker/blob/main/demoscreenshot2.jpg?raw=true)


![Demo Screenshot](https://github.com/btorressz/QuoteDriftTracker/blob/main/demoscreenshot3.jpg?raw=true)





