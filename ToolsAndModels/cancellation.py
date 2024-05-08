from llm.model import llm
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnableMap
from Redis.redis import setData, getData, deleteData
from dotenv import load_dotenv
load_dotenv()
import os
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.tools import Tool

from database import vector_store

def cancel_item(query):
    template = """
   Analyze the query and extract the food items name and quantity.
   If the name of the food item matches similar to the provided context, replace the name with the exact name available in context.
   If it does not match, keep the name as it is without any modification.
   If you cannot analyze the quantity of the food item, set it to default -1.
   Provide the response in json format such as dict(foodname:quantity). Include all items.
   User query provided in double backticks: ``{query}``
   Context provided in triple backticks: ```{context}```
    """
    senderId = ''
    prompt = PromptTemplate.from_template(template)
    chain = RunnableMap(
        {
            'query':lambda x: x['query'],
            'context': lambda x: [i.page_content.split("Description")[0] for i in vector_store.similarity_search(x['query'],k=8)]
        }
    ) | prompt | llm | JsonOutputParser()

    result = chain.invoke({'query':query})

    with open(r"sender.txt", "r") as file:
        senderId = file.read()
    
    current_orders = getData(senderId).get('order')
    message = ""
    # print(current_orders)
    if not current_orders:
        message += "You have not ordered anything yet"
    else:
        for item, quantity in result.items():
            if item.lower() not in current_orders.keys():
                message += f"\nYou have not ordered {item}."
                continue
            current_quantity = current_orders[item.lower()]['quantity']
            if quantity == -1 or quantity==current_quantity:
                del current_orders[item.lower()]
                message += f"\nCompletely removed {item} from your order"
            elif quantity < current_quantity:
                current_quantity -= quantity
                current_orders[item.lower()]['quantity'] = current_quantity
                message += f"\nRemoved {quantity} {item} from your order"
            else:
                message += f"\n Order exceeded for {item}. You have ordered only {current_quantity} {item} upto now."
        
        a = getData(senderId)
        a['order'] = current_orders
        setData(senderId, a)
        print(getData(senderId))
    return message



cancel_tool = Tool(
    name = "Canceltool",
    func=cancel_item,
    description="A tool that is used to cancel or remove food order of the user."
)


if __name__ == "__main__":
    # print([i.page_content.split("Description")[0] for i in vector_store.similarity_search("cancel 2  fudge and  nachos")])
    # print([i.page_content.split("Description")[0] for i in vector_store.similarity_search("Cancel 10 nachos",k=8)])
    print(cancel_item("remove tuna from my order"))
    # print(vector_store.similarity_search('All items', k=30))