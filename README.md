# AUTOtrade

AUTOtrade is a Python-based trading assistant designed to empower investors with informed decision-making capabilities. By leveraging multiple data sources, the system performs comprehensive stock analysis through web scraping, sentiment analysis, and time series forecasting to generate actionable buy/sell recommendations.

The platform consolidates information from:
- **News outlets**
- **Reddit discussions**
- **Historical market data**

This multifaceted approach provides users with intuitive, data-driven market insights to optimize their trading strategies.

## Getting Started

You can run the project using the provided Docker Compose file for convenience or start each component manually by following these steps:

### Instructions

1. **Frontend** (Terminal 1)

```bash
   cd fe
   npm install
   npm run dev
```

2. **Backend** (Terminal 2)

```bash
   cd be
   ./init.bat
   cd app
   uvicorn main:app --host 0.0.0.0 --port 8000
```
