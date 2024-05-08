from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_core.tools import Tool

from llm.model import llm
from Redis.redis import getData, setData, deleteData, flushAll



def calculate_receipt(user_query):
    # order_details = [
    # {"food_name": "Pizza", "price": 10.99},
    # {"food_name": "Burger", "price": 5.99},
    # {"food_name": "Salad", "price": 7.5},
    # {"food_name": "Pasta", "price": 8.75},
    # {"food_name": "Steak", "price": 15.99},
    # {"food_name": "Sushi", "price": 12.5}
    # ]
    with open('sender.txt', "r") as file:
        senderId = file.read()
    order_details = getData(senderId).get('order')
    print(order_details)
    template = """You are an assistant at ABC restaurant. Your task is to return receipt or order detials to the user. Use this tool only when the user asks for receipt/bill or if he asks for what his orders are.    
    Given a dictionary containing itemname with quantity and price, fetch all the price and quantity and add all the prices multiplied with its quantity to return a total price. The list is given in three backticks. 
    ```{order_details}```
    ##User query is: ``{user_query}``
    The output should be of JSON.
    Make sure to include the order details in JSON output as well."""

    total_price_calculator_prompt = PromptTemplate(input_variables=["user_query"], template=template)
    total_price_calculator_chain = LLMChain(llm = llm, prompt=total_price_calculator_prompt)
    total_sum = total_price_calculator_chain.run({"user_query":user_query, "order_details": order_details})
    print("receipt_tool")
    # return order_details
    return total_sum


receipt_tool = Tool(
        name = "ReceiptCalculator",
        func= calculate_receipt,
        description = "A tool that returns total price when the user asks for receipt or bill."
    )



# if __name__ == "__main__":
#     calculate_receipt(user_query="I need my receipt")
    # uvicorn.run(app = app, host = "127.0.0.1", port = 5556)
    
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