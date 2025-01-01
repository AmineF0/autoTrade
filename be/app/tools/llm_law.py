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

from tools.prompts import PROMPTS
loi_prompts = PROMPTS.loi

load_dotenv()
class RAGLawTool:
    def __init__(self, vectorstore_path, embedding_function, model_name="gpt-4o-mini"):
        # Initialize vector store
        self.vectorstore = Chroma(
            persist_directory=vectorstore_path,
            embedding_function=embedding_function
        )
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        # Define prompt template
        PROMPT_TEMPLATE = loi_prompts['prompt_template']
        self.prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    
    def retrieve_and_answer(self, query, k=3):
        print("Retrieving and answering question:", query)
        # Step 1: Perform similarity search
        results = self.vectorstore.similarity_search_with_score(query, k=k)
        # Step 2: Create context from retrieved documents
        context = "\n\n----\n\n".join(
                doc.page_content for doc, _score in results  # Limit text length
            )
        # Step 3: Format prompt with retrieved context
        prompt = self.prompt_template.format(context=context, question=query)
        # Step 4: Invoke LLM with the prompt
        response = self.llm.invoke(prompt)
        return response.content

    # Example: Define your RAG tool as a LangChain Tool
    def create_tool(self,):
        return Tool(
            name=loi_prompts['name'],
            func=lambda query: self.retrieve_and_answer(query),
            description=loi_prompts['description']
        )
