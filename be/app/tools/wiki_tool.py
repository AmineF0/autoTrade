from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.tools import Tool
from tools.prompts import PROMPTS

wiki_prompts = PROMPTS.wikipedia
class WikiTool:
    def __init__(self):
        self.api_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=5000)
        self.tool = WikipediaQueryRun(api_wrapper=self.api_wrapper)
        
        
    def retrieve_and_answer(self, query):
        return self.tool.run(query)
    
    def create_tool(self):
        return Tool(
            name=wiki_prompts['name'],
            func=lambda query: self.retrieve_and_answer(query),
            description=wiki_prompts['description']
        )
    
