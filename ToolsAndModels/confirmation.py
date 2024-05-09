from llm.model import llm
from langchain_core.prompts import  ChatPromptTemplate
from langchain.chains import LLMChain
from langchain_core.tools import Tool
from Redis.redis import getData

def confirmation(user_query):

    # details_order = [
    #     {"food_name": "momo", "price": 12, "address": "Kapan"},
    #     {"food_name": "Burger", "price": 13, "address": "Balaju"},
    #     {"food_name": "pizza", "price": 14, "address": "Kalopul"},
    #     {"food_name": "chowmin", "price": 15, "address": "Ratopul"},
    #     {"food_name": "pasta", "price": 16, "address": "Setopul"}
    # ]

    with open(r"ToolsAndModels\sender.txt", 'r') as file:
        senderId = file.read()
    
    details_order = getData(senderId)

    
    template = """You are an assistant at ABC restaurant. Your task is to thanks and return receipt when the user has completed the order. Use this tool only when the user has finished or confirms the order.    
    Given a JSON that contains address, and food orders that contains name, quantity and price for single quantity. The json is given in three backticks. 
    Make sure to add total price in the output.
    ```{details_order}```
    ##User query is: ``{user_query}``
    The output should be of JSON."""

    confim_prompt = ChatPromptTemplate.from_template(template=template)
    confirm_chain = LLMChain(llm=llm, prompt=confim_prompt)
    response = confirm_chain.run({"user_query": user_query, "details_order": details_order})
    return response


#print(conformation("I have finished my order"))

confirmation_tool = Tool(
    name="confirmation",
    func=confirmation,
    description="A tool that is used to say thank you and  generate the receipt  when the user finishes or confirms the order"
)

if __name__ == "__main__":
    print(confirmation("My order has finished."))

#print(confirmation_tool)
# conf_prompt = ChatPromptTemplate.from_messages(
#     [
#         (
#             "system",
#             "You are a smart helpful assistant. Use the tool for providing order details for the user after the order has finished or confirmed.",
#         ),
#         ("placeholder", "{chat_history}"),
#         ("human", "{input}"),
#         ("placeholder","{tool_names}"),
#         ("placeholder","{tool}"),
#         ("placeholder", "{agent_scratchpad}"),
#     ]
# )
# #print(conf_prompt)
# agent = create_tool_calling_agent(llm, [confirmation_tool], conf_prompt)
# #print(agent)

# agent_executor = AgentExecutor(tools=[confirmation_tool], agent=agent)
# print(agent_executor.invoke({"input": "I have completed my order"}))