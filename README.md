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
