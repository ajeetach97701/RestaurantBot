from llm.model import llm
from langchain.schema.runnable import RunnableMap
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from Redis.redis import setData, getData
from langchain.vectorstores.milvus import Milvus
from dotenv import load_dotenv
load_dotenv()
import os
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_core.tools import Tool

from database import vector_store

def order_item(query):
    extract_template = """
    You are a virtual Restaurant Waiter. Your task is to check if the given food_name is present in the context or not. 
    If the food is available in the context and has multiple foods for it, show the user with all the available food names with its price.
    The output should be of JSON FORMAT without any backticks which is given in four backticks return only :
    If not tell them that the option is not available and ask them if they would like to order something else?
    Context is given in three backticks: ```{context}```
    User provided food name is given in double backticks: ``{query}``

    The following JSON response should be in four fields,
    dict('itemsname':all available names in list, 'price':all available prices, 'quantity':quantity mentioned in the query, 'message':available options with prices if available, not available if not)
    if quanity is not mentioned, set default to 1
    """

    prompt = PromptTemplate.from_template(extract_template)
    chain = RunnableMap(
        {
            'query':lambda x: x['query'],
            'context': lambda x: vector_store.similarity_search(x['query'],k=8)
        }
    ) | prompt | llm | JsonOutputParser()

    result = chain.invoke({'query':query})

    if len(result['itemsname']) == 0 or len(result['itemsname']) > 1:
        return result['message']
    else:
        senderId = "10"
        if getData(senderId) is None:
            setData(senderId, {result['itemsname'][0]: result['quantity']})
            print(getData(senderId))
        else:
            a = getData(senderId)
            a[result['itemsname'][0]] = result['quantity']
            setData(senderId, a)
            print(getData(senderId))
        return "What else would you like to order?"

order_tool = Tool(
    name = "Ordertool",
    func=order_item,
    description="A tool that is used to take food order from the user and checks food availability"
)
