# 📈 Quote Drift Tracker

## 🧠 Overview

**Quote Drift Tracker** is a Python-based application designed to analyze MEV (Maximal Extractable Value) and HFT (High-Frequency Trading) dynamics on the Solana blockchain through Jupiter DEX quote monitoring.  
The application continuously monitors Jupiter DEX quote latency and price drift to identify potential front-running opportunities and trading inefficiencies.

It operates by making concurrent API requests to Jupiter’s quote endpoint, tracking response times, price movements, and calculating statistical metrics to detect patterns that could indicate MEV opportunities.

---
