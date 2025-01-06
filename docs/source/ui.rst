User Interface
==============

AUTOtrade's interface presents real-time monitoring of five AI traders (for a PoC), each employing distinct trading strategies powered by Large Language Models. Built with React and Vite, connected to a FastAPI backend, the system refreshes market analysis every 12 hours to maintain current trading insights.

Trading Profiles and Performance Display
-----------------------------------------

The interface showcases five virtual traders: Alice (value), Bob (growth), Charlie (momentum), David (defensive), and Eve (ideal). Each profile maintains its own portfolio and trading strategy.

.. figure:: /images/profiles.png
   :alt: Trading Profiles Interface
   :width: 60%
   :align: center

   Profiles

Portfolio Analytics Dashboard
------------------------------

Real-Time Portfolio Metrics
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The dashboard presents three financial indicators:

* Total Equity (e.g., $91,764.85)
* Realized Profit/Loss (e.g., $-8,235.15)
* Current Portfolio Value (e.g., $7,622.08)

Stock Performance Visualization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
For each tracked stock (e.g., AMZN, MSFT), the interface displays:

* Current price with percentage change (e.g., MSFT: $423.35, +3.15%)
* Historical price charts with interactive timelines
* Price projections with confidence intervals (0-100% scale)

.. figure:: /images/dashboard.png
   :alt: Portfolio Analytics
   :width: 70%
   :align: center

   Real-time portfolio analytics and stock projections

Holdings and Trade History
--------------------------

Current Portfolio Status
~~~~~~~~~~~~~~~~~~~~~~~~
Detailed position tracking showing:

* Stock holdings (e.g., NVDA: 15 shares, Value: $2,160.05)
* Realized P/L per position
* Total investment value per stock

Trading Activity Log
~~~~~~~~~~~~~~~~~~~~
A trade history including:

* Action taken (Buy/Hold/Sell)
* Stock symbol and quantity
* Confidence level (e.g., 85.0% for MSFT buy)
* AI reasoning for trades (e.g., "MSFT has positive sentiment in Reddit posts and strong long-term forecasts")

.. figure:: /images/holdings.png
   :alt: Holdings and Trade History
   :width: 80%
   :align: center

   Portfolio holdings and AI trading decisions

Technical Architecture
-----------------------

Backend Implementation
~~~~~~~~~~~~~~~~~~~~~~~
.. code-block:: python

    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Automated model updates
    async def update_loop():
        while True:
            await asyncio.sleep(60*60)
            context = generate_context(predictor, news_analyzer)
            for name, llm in llms.items():
                llm.run_decision_making(
                    session=session, 
                    context=context, 
                    market_data=context["current_prices"]
                )

The system features:

* Automated 12-hour model retraining
* Real-time WebSocket updates
* Performance-optimized caching
* Comprehensive logging system
* SQLite database for trade tracking