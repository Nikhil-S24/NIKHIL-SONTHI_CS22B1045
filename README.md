# 📊 Gemscap Quant Analytics Dashboard

A real-time quantitative analytics system for pair trading (**BTCUSDT** & **ETHUSDT**).  
Streams tick data from **Binance WebSocket**, stores it in a database, computes advanced analytics  
(Hedge Ratio, Kalman Filter, Theil–Sen Regression, Z-Score, ADF Test, Rolling Correlation),  
and visualizes results interactively using **Streamlit**.

---
## 🎥 Project Demo

Watch the complete project demo video below:  
📁 [Project Demo](https://drive.google.com/drive/u/1/folders/1b1uqepbtSHbnMMzJ0Y5UgJiTLWbAaMLQ)

## 🎯 Objective
Design and implement a complete analytical app demonstrating an end-to-end workflow —  
from **real-time data ingestion and storage** to **quantitative analytics and visualization**.  

This project fulfills that goal by:
- Collecting live Binance tick data
- Storing it in SQLite/MySQL
- Computing OLS, Kalman hedge ratios
- Performing mean-reversion analytics
- Displaying live dashboards with alerts and CSV export

---

## ⚙️ Setup & Execution

### 1️⃣ Clone and enter the project
```bash
git clone https://github.com/<Nikhil-S24>/gemscap-quant-analytics.git
cd gemscap-quant-analytics


2️⃣ Install dependencies
pip install -r requirements.txt

3️⃣ Run the full application
python app.py


➡️ This starts both the data ingestion service and the Streamlit dashboard.
Open your browser at http://localhost:8501
 to view the dashboard.

To stop, press Ctrl + C in the terminal.

Methodology & Analytics

Data Ingestion:
backend/data_ingestion.py connects to Binance’s WebSocket and continuously stores tick data.

Storage:
Ticks are persisted in a SQLite or MySQL database for later analysis.

Analytics (backend/analytics.py):

Static Hedge Ratio (OLS) — linear regression of BTC on ETH.

Dynamic Hedge Ratio (Kalman Filter) — time-varying hedge ratio adapting to market changes.

Robust Hedge Ratio (Theil–Sen) — resistant to outliers.

Spread & Z-Score — mean-reversion indicators.

Rolling Correlation — monitors pair relationship stability.

ADF Test — checks for spread stationarity.

Frontend (frontend/app.py):
Interactive Streamlit dashboard showing:

Live BTC/ETH prices

Static vs dynamic hedge ratio chart

Spread & Z-score visualization

Rolling correlation chart

Real-time alerts when |Z| > 2

CSV export of analytics data

Binance WebSocket API
   ↓
Data Ingestion (backend/data_ingestion.py)
   ↓
Database (SQLite / MySQL)
   ↓
Analytics Engine (OLS / Kalman / Theil–Sen)
   ↓
Streamlit Frontend (frontend/app.py)
   ↓
Alerts & CSV Export

gemscap-quant-analytics/
├── app.py                     # Single-command launcher
├── backend/
│   ├── data_ingestion.py      # WebSocket ingestion
│   ├── analytics.py           # OLS, Kalman analytics
│   └── storage.py             # Database helpers
├── frontend/
│   └── app.py                 # Streamlit dashboard
├── architecture.drawio
├── architecture.png
├── requirements.txt
└── README.md


This project was developed with limited assistance from ChatGPT (OpenAI) for:

scaffolding backend/frontend structure

refining Kalman regression code

debugging Streamlit integration

formatting documentation and README