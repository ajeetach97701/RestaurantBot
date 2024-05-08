from llm.model import llm
from langchain.schema.runnable import RunnableMap
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from Redis.redis import setData, getData,flushAll
from dotenv import load_dotenv
load_dotenv()
from langchain_core.tools import Tool
from database import vector_store

redis_data = {
    "address": "",
    "order":{}
}

def order_item(query):
    extract_template = """
    You are a virtual Restaurant Waiter. Your task is to check if the given food_name is present in the context or not. 
    If the food is available in the context and has multiple foods for it, show the user with all the available food names (Keep food name exact from context) with its price.
    The output should be of JSON FORMAT without any backticks which is given in four backticks return only :
    If not tell them that the option is not available and ask them if they would like to order something else?
    Context is given in three backticks: ```{context}```
    User provided food name is given in double backticks: ``{query}``

    The following JSON response should be in four fields,
    dict('itemsname':all available names in list, 'price':all available prices in list, 'quantity':quantity mentioned in the query, 'message':available options with prices if available, not available if not)
    if quanity is not mentioned, set default to 1.
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
        with open(r"sender.txt", "r") as file:
            senderId = file.read()
        if getData(senderId) is None:
            setData(senderId, redis_data)
        a = getData(senderId)
        a.get('order')[result['itemsname'][0].lower()]={'quantity':result['quantity'], 'price':result['price'][0]}
        setData(senderId, a)
        print(getData(senderId))
        return senderId,"What else would you like to order?"

order_tool = Tool(
    name = "Ordertool",
    func=order_item,
    description="A tool that is used to take food order from the user and checks food availability"
)

if __name__ == "__main__":
    # flushAll()
    # order_item("I would like to order 2 nachos")
    # print(order_item(" yes order 2 nachos"))
    # print(vector_store.similarity_search("Order chocolate fudge",k=8))
    print(order_item("order 2 cookies and cream"))
    # 
    
