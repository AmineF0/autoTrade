from langchain.tools import Tool

from langchain.utilities import SQLDatabase
from langchain.llms import OpenAI
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.agents.agent_types import AgentType
from langchain.chat_models import ChatOpenAI

import os
import re

from db.db import DB
db = DB()

import logging
logging.basicConfig(level=logging.INFO)

from tools.prompts import PROMPTS
sql_prompts = PROMPTS.sql

class SQLTool:
    def __init__(self, model_name="gpt-4o"):
        self.db = SQLDatabase.from_uri("sqlite:///data/db.sqlite3")
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        self.tool = create_sql_agent(
            db=self.db,
            llm=self.llm,
            verbose=False,
            agent_type="openai-tools",
            # agent_executor_kwargs={
            #     'handle_parsing_errors': True,
            #     # 'max_iterations': 5,  # Limit iterations
            #     'early_stopping_method': 'force'  # Force stop if stuck
            # }
        )

    def retrieve_and_answer(self, query):
        logging.info("Retrieving and answering question:", query)
        try:
            # Preprocessing to prevent repetitive queries
            sanitized_query = self._sanitize_query(query)
            
            # Add specific query routing
            if any(keyword in sanitized_query.lower() for keyword in ['non-compliant', 'sensor limits', 'out of range']):
                return self._analyze_sensor_compliance(sanitized_query)
            
            if any(keyword in sanitized_query.lower() for keyword in ['record', 'last', 'latest']):
                return self.db.get_last_record()
            
            if any(keyword in sanitized_query.lower() for keyword in ['average', 'mean', 'median', 'min', 'max', 'statistics']):
                return self.db.get_general_statistics()
            
            return self.tool.run(sanitized_query)
        
        except Exception as e:
            return f"Error in SQL query: {str(e)}. Please rephrase or be more specific."

    def _sanitize_query(self, query):
        # Remove potentially problematic characters or patterns
        return re.sub(r'[;\'"`]', '', query)

    def _analyze_sensor_compliance(self, query):
        return db.analyse_sensor_compliance(query)

    def create_tool(self):
        return Tool(
            name="Improved SQL Sensor Analysis",
            func=lambda query: self.retrieve_and_answer(query),
            description="Advanced SQL tool for sensor data analysis, compliance checking, and historical trends"
        )

if __name__ == "__main__":
    tool = SQLTool()
    tool.create_tool().run()