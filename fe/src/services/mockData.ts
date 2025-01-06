import { ApiResponse } from '../types/api';

export const mockApiResponse: ApiResponse = {
  people: {
    "Alice": "value",
    "Bob": "growth",
    "Charlie": "momentum",
    "David": "defensive",
    "Eve": "ideal"
  },
  people_performance: {
    "Alice": {
      "current_balance": 92188.19995117188,
      "realized_profit": -7811.800048828125,
      "portfolio_value": 7198.729949951172,
      "total_equity": 99386.92990112305,
      "holdings": {
        "NVDA": 15,
        "TSLA": 4,
        "MSFT": 8
      },
      "holdings_value": {
        "NVDA": 2168.8499450683594,
        "TSLA": 1643.0799560546875,
        "MSFT": 3386.800048828125
      },
      "realized_profit_by_stock": {
        "NVDA": -2035.0,
        "TSLA": -2390.0,
        "MSFT": -3386.800048828125
      }
    },
    "Bob": {
      "current_balance": 1532.9998779296875,
      "realized_profit": -8467.000122070312,
      "portfolio_value": 8467.000122070312,
      "total_equity": 10000.0,
      "holdings": {
        "MSFT": 20
      },
      "holdings_value": {
        "MSFT": 8467.000122070312
      },
      "realized_profit_by_stock": {
        "MSFT": -8467.000122070312
      }
    },
    "Charlie": {
      "current_balance": 3649.7499084472656,
      "realized_profit": -6350.250091552734,
      "portfolio_value": 6350.250091552734,
      "total_equity": 10000.0,
      "holdings": {
        "MSFT": 15
      },
      "holdings_value": {
        "MSFT": 6350.250091552734
      },
      "realized_profit_by_stock": {
        "MSFT": -6350.250091552734
      }
    },
    "David": {
      "current_balance": 9576.649993896484,
      "realized_profit": -423.3500061035156,
      "portfolio_value": 423.3500061035156,
      "total_equity": 10000.0,
      "holdings": {
        "MSFT": 1
      },
      "holdings_value": {
        "MSFT": 423.3500061035156
      },
      "realized_profit_by_stock": {
        "MSFT": -423.3500061035156
      }
    },
    "Eve": {
      "current_balance": 3660.550079345703,
      "realized_profit": -6339.449920654297,
      "portfolio_value": 6339.449920654297,
      "total_equity": 10000.0,
      "holdings": {
        "NVDA": 15,
        "MSFT": 5,
        "TSLA": 5
      },
      "holdings_value": {
        "NVDA": 2168.8499450683594,
        "MSFT": 2116.750030517578,
        "TSLA": 2053.8499450683594
      },
      "realized_profit_by_stock": {
        "NVDA": -2168.8499450683594,
        "MSFT": -2116.750030517578,
        "TSLA": -2053.8499450683594
      }
    }
  },
  people_thoughts: {
    "Alice": [
      {
        "mode": "ideal",
        "stock": "MSFT",
        "confidence": 0.85,
        "timestamp": "2025-01-06T05:45:21.115715",
        "action": "BUY",
        "id": 1,
        "trader_id": 1,
        "quantity": 5,
        "reasoning": "MSFT has positive sentiment in Reddit posts and strong long-term forecasts. Current price is stable with potential for growth, making it a solid investment opportunity."
      }
    ],
    "Bob": [
      {
        "mode": "growth",
        "stock": "MSFT",
        "confidence": 0.85,
        "timestamp": "2025-01-06T06:28:53.582217",
        "action": "BUY",
        "id": 6,
        "trader_id": 2,
        "quantity": 5,
        "reasoning": "MSFT shows strong positive sentiment with all posts being positive and a solid upward price forecast for the next 7 days."
      }
    ],
    "Charlie": [
      {
        "mode": "momentum",
        "stock": "MSFT",
        "confidence": 0.85,
        "timestamp": "2025-01-06T06:28:58.375048",
        "action": "BUY",
        "id": 9,
        "trader_id": 3,
        "quantity": 10,
        "reasoning": "MSFT shows strong positive sentiment with all positive Reddit posts and no negative news."
      }
    ],
    "David": [
      {
        "mode": "defensive",
        "stock": "MSFT",
        "confidence": 0.7,
        "timestamp": "2025-01-06T07:26:39.943799",
        "action": "HOLD",
        "id": 36,
        "trader_id": 4,
        "quantity": 1,
        "reasoning": "MSFT has positive sentiment and consistent forecasts from both models."
      }
    ],
    "Eve": [
      {
        "mode": "ideal",
        "stock": "MSFT",
        "confidence": 0.65,
        "timestamp": "2025-01-06T06:29:11.553474",
        "action": "HOLD",
        "id": 13,
        "trader_id": 5,
        "quantity": 5,
        "reasoning": "MSFT has positive sentiment and a strong long-term forecast."
      }
    ]
  },
  current_prices: {
    "AMZN": 224.1999969482422,
    "MSFT": 423.3500061035156,
    "TSLA": 410.7699890136719,
    "NVDA": 144.58999633789062
  },
  data_and_forecast: {
    "NVDA": {
      "1h": {
        "forecast": {
          "LSTM_univariate": [125.46, 114.98, 107.36, 99.58, 93.55, 88.39, 83.82],
          "MLP_univariate": [142.80, 143.65, 143.76, 144.07, 144.55, 144.21, 144.05]
        }
      },
      "1d": {
        "forecast": {
          "LSTM_univariate": [133.74, 132.77, 132.10, 131.58, 131.11, 130.69, 130.34],
          "MLP_univariate": [138.48, 137.66, 137.00, 136.87, 137.04, 137.25, 137.21]
        }
      }
    }
  }
};