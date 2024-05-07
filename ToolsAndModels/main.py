import json
import uvicorn
from llm.model import llm
from fastapi import FastAPI
from order import order_tool
from food_fetch import food_tool
from address import address_tool
from suggestion import suggestion_tool
from ReceipeGenerator import recipe_tool
from  receiptGenerator import receipt_tool
from langchain.memory import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate
from Redis.redis import getData, setData, deleteData, flushAll
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.runnables.history import RunnableWithMessageHistory
 
tools = [
    receipt_tool,
    recipe_tool,
    food_tool,
    address_tool,
    suggestion_tool,
    order_tool,
]

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a waiter at a restaurant. You should have conversation with the user.\
            First greet the user and welcome the user to our restaurant and ask him if he would like to order something.\
            Look up for tools to answer the user query do not make up your own answers. Only use tools to answer the user query \
            Always return the output in JSON format with double quotation(\") but not single quotation(\') with no (\n) in the outputs",
        ),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
)

# # Construct the Tools agent
agent = create_tool_calling_agent(llm, tools, prompt)

agent_executor = AgentExecutor(
    tools= tools, 
    agent= agent, 
    max_iterations= 5, 
    return_intermediate_steps= False, 
    verbose=True, 
    early_stopping_method ='generate')

from langchain.memory import ChatMessageHistory
memory = ChatMessageHistory(session_id="test-session")
from langchain_core.runnables.history import RunnableWithMessageHistory

agent_with_chat_history = RunnableWithMessageHistory(
    agent_executor,
    # This is needed because in most real world scenarios, a session id is needed
    # It isn't really used here because we are using a simple in memory ChatMessageHistory
    lambda session_id: memory,
    input_messages_key="input",
    history_messages_key="chat_history",
)
# redis_data = {
#     "address": "",
#     "order":[]
# }

app = FastAPI()

@app.get("/restaurant/")
def stream(query: str, senderId: str):
    # if getData(senderId) is None: 
    #     setData(senderId, redis_data)
    print(getData(senderId))
    with open('sender.txt', 'w') as file:
        file.write(senderId)
    output= agent_with_chat_history.invoke({"input":query},config={"configurable": {"session_id": "<foo>"}},)
    return {"result":output.get('output')}
    
    
    # print(agent_output)
    # json.dumps(agent_output)
   
if __name__ == "__main__":
    uvicorn.run(app = app, host = "127.0.0.1", port = 5556)
    
    
# # agent_with_chat_history.invoke({"input":"Hello"},
#     config={"configurable": {"session_id": "<foo>"}},
# #                                )

# # agent_with_chat_history.invoke({"input":"I want to order a momo"},
# #     config={"configurable": {"session_id": "<foo>"}},
# #                                )
# # agent_with_chat_history.invoke({"input":"I want to have a delivery in Kapan"},
# #     config={"configurable": {"session_id": "<foo>"}},
# #     )
# # agent_with_chat_history.invoke({"input":"Suggest me some appetizers"},
# #     config={"configurable": {"session_id": "<foo>"}},
# #     )