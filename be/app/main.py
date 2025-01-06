import sys
import json
import asyncio
import time
import os
import logging
from pydantic import BaseModel
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException

from trader.trader import Trader, get_scoped_session
from time_series.predictor import Predictor
from social_media_analysis.reddit_sentiment_analysis import get_sentiment_analysis_for_stocks
from news.news_sentiment import NewsSentimentAnalyzer

from trader.llm_trader import LLMTrader

from context_generator import generate_context

if sys.platform.startswith('win'):
	asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
	level=getattr(logging, LOG_LEVEL, logging.INFO),
	format="%(asctime)s [%(levelname)s] %(message)s",
	handlers=[
		logging.StreamHandler(),
		logging.FileHandler("app.log")
	]
)

app = FastAPI()
app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

session = get_scoped_session("sqlite:///db.sqlite")

# modes : value, growth, momentum, defensive, ideal
profiles = {
	"Alice": "value",
	"Bob": "growth",
	"Charlie": "momentum",
	"David": "defensive",
	"Eve": "ideal"
}

llms = {}
 
for name, profile in profiles.items():
	if not session.query(Trader).filter(Trader.name == name).first():
		trader = Trader(name=name, balance=10_000)
		session.add(trader)
		session.commit()
	
	trader = session.query(Trader).filter(Trader.name == name).first()
	llms[name] = LLMTrader(trader, session, profile)

predictor = Predictor()
news_analyzer = NewsSentimentAnalyzer() 


@app.get("/")
async def root():
  # return everything in the database
  people_performance = {}
  for name, llm in llms.items():
    trader = session.query(Trader).filter(Trader.name == name).first()
    people_performance[name] = trader.get_performance_stats(session, predictor.get_current_prices())
  
  people_thoughts = {}
  for name, llm in llms.items():
    trader = session.query(Trader).filter(Trader.name == name).first()
    people_thoughts[name] = trader.get_thoughts()
  
  
  data = {
		"people": profiles,
		"people_performance": people_performance,
		"people_thoughts": people_thoughts,
		"current_prices": predictor.get_current_prices(),
		"data_and_forecast": predictor.data_and_forcast(),
	}
  
  return data


async def update_loop():
	while True:
		await asyncio.sleep(60*60)
		context = generate_context(predictor, news_analyzer)
		for name, llm in llms.items():
			llm.run_decision_making(session=session, context=context, market_data=context["current_prices"])
		

@app.on_event("startup")
async def startup_event():
	asyncio.create_task(update_loop())
	logging.info("Application startup complete")

@app.on_event("shutdown")
async def shutdown_event():
  logging.info("Application shutdown complete")



if __name__ == "__main__":
	import uvicorn
	uvicorn.run("app.main:app", host="0.0.0.0", port=8000, workers=1)
