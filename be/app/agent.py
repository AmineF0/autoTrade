from langchain.tools import Tool
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.schema import Document
from dotenv import load_dotenv
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.agents import initialize_agent
from langchain_core.prompts import ChatPromptTemplate
import os
from tools.rag_doc_tool import RAGTool
from tools.company_rag_tool import CompanyRagTool
from tools.wiki_tool import WikiTool
from tools.llm_law import RAGLawTool
from tools.sql_tool import SQLTool

# from tools.llm_input_parser import LLMInputTool as LLMInputParser
# from tools.llm_output_parser import LLMOutputTool as LLMOutputParser

from tools.prompts import PROMPTS
zero_shot_react_description = PROMPTS.zero_shot_react_description

load_dotenv()

class AIAssistant:
    def __init__(self,model_name="gpt-4o-mini",temperature=0):
        # llm
        self.model_name = model_name
        self.temperature = temperature
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # rags
        self.embedding_function = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))
        
        self.rag_doc = RAGTool(
            vectorstore_path="data/chroma/chroma_doc",
            embedding_function=self.embedding_function,
        )
        self.rag_doc_tool = self.rag_doc.create_tool()
        
        self.company_rag = CompanyRagTool(
            vectorstore_path="data/chroma/chroma_company",
            embedding_function=self.embedding_function,
        )
        self.company_rag_tool = self.company_rag.create_tool()
        
        self.loi = RAGLawTool(
            vectorstore_path="data/chroma/chroma_loi",
            embedding_function=self.embedding_function,
        )
        self.loi_tool = self.loi.create_tool()
        
        #wiki
        self.wiki = WikiTool()
        self.wiki_tool = self.wiki.create_tool()
        
        #sql
        self.sql = SQLTool()
        self.sql_tool = self.sql.create_tool()
        
        
        # define tools and agent
        self.tools = [
            self.rag_doc_tool,
            self.company_rag_tool,
            self.wiki_tool,
            self.loi_tool,
            self.sql_tool,
        ]
        
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent="zero-shot-react-description",
            verbose=True,
            handle_parsing_errors=True
        )
        
        
    def retrieve_and_answer(self, query, role='', k=5):
        
        self.template_structure = zero_shot_react_description["prompt_template"]
        self.prompt = ChatPromptTemplate.from_template(self.template_structure)
        
        fs = self.prompt.format_messages(question=query)
        return self.agent.run(fs)
        
        
         
if __name__ == '__main__':
    print('Testing AIAssistant')
    agent = AIAssistant()
    query = "Give me the names of sensors that are not respecting the limits and how we can improve them?"
    role = "assistant"
    response = agent.retrieve_and_answer(query, role)
    print(response)