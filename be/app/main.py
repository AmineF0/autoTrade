import sys
import json
import asyncio
import time
import os
import logging
from pydantic import BaseModel
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from agent import AIAssistant
from fastapi.exceptions import HTTPException

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

##### Fast API #####

app = FastAPI()
app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

##### DB #####
from db.db import DB
db = DB()

##### Pydantic Models #####
class QueryInput(BaseModel):
	role: str
	query: str


##### REST API #####

@app.post("/query")
async def set_target(query: QueryInput):
  try:
    role = query.role
    query = query.query
    # TODO: Implement query execution
    agent = AIAssistant()
    response = agent.retrieve_and_answer(query, role)
    return {"status": "success",
				"response": response}
  except Exception as e:
    logging.error(str(e))
    return HTTPException(status_code=500, detail=str(e))
 
@app.get("/stats")
async def get_uptime_stats():
	"""Get system statistics"""
	try:
		stats = db.get_summary()
		return {"status": "success",
				"stats": stats}
	except Exception as e:
		logging.error(str(e))
		return HTTPException(status_code=500, detail=str(e))


##### Asyncio Tasks #####

async def update_loop():
	while True:
		db.add_record()
		await asyncio.sleep(60)

@app.on_event("startup")
async def startup_event():
	asyncio.create_task(update_loop())
	logging.info("Application startup complete")

@app.on_event("shutdown")
async def shutdown_event():
  db.close()
  logging.info("Application shutdown complete")



if __name__ == "__main__":
	import uvicorn
	uvicorn.run("app.main:app", host="0.0.0.0", port=8000, workers=1)
