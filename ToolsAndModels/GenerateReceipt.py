import os
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_core.runnables import RunnableMap, RunnablePassthrough
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import CSVLoader
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain.agents import AgentExecutor, create_tool_calling_agent, initialize_agent, AgentType
from langchain.tools.retriever import create_retriever_tool
from langchain_text_splitters import  RecursiveCharacterTextSplitter
from langchain.chains import LLMChain, create_tagging_chain_pydantic
from langchain_core.tools import Tool
from langchain.memory import ConversationBufferMemory
from pydantic import BaseModel, Field
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from llm.model import llm



def calculate_receipt(user_query):
    order_details = [
    {"food_name": "Pizza", "price": 10.99},
    {"food_name": "Burger", "price": 5.99},
    {"food_name": "Salad", "price": 7.5},
    {"food_name": "Pasta", "price": 8.75},
    {"food_name": "Steak", "price": 15.99},
    {"food_name": "Sushi", "price": 12.5}
    ]
    template = """You are an assistant at ABC restaurant. Your task is to return receipt to the user. Use this tool only when the user asks for receipt/bill.    
    Given a List containing food_name and price, fetch all the price and add all the prices to return a total price. The list is given in three backticks. 
    ```{order_details}```
    ##User query is: ``{user_query}``
    The output should be of JSON."""

    total_price_calculator_prompt = PromptTemplate(input_variables=["user_query"], template=template)
    total_price_calculator_chain = LLMChain(llm = llm, prompt=total_price_calculator_prompt)
    total_sum = total_price_calculator_chain.run({"user_query":user_query, "order_details": order_details})
    print("receipt_tool")
    return total_sum


receipt_tool = Tool(
        name = "ReceiptCalculator",
        func= calculate_receipt,
        description = "A tool that returns total price when the user asks for receipt or bill."
    )

# # memory = ConversationBufferMemory(memory_key = "chat_history", return_messages= True)


# prompt_receipt = ChatPromptTemplate.from_messages(
#     [
#         (
#             "system",
#             "You are a helpful assistant. Make sure to use the tool for providing receipt for the user.",
#         ),
#         ("placeholder", "{chat_history}"),
#         ("human", "{input}"),
#         ("placeholder", "{agent_scratchpad}"),
#     ]
# )

# # Construct the Tools agent
# # agent = create_tool_calling_agent(llm, receipt_tool, prompt_receipt)

# # agent_executor = AgentExecutor( tools = receipt_tool, agent= agent)
# # agent_executor.invoke({"input":"I need my receipt"})