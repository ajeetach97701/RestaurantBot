from langchain.memory import ChatMessageHistory
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.tools import Tool
from langchain.memory import ConversationBufferMemory
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.chains import ConversationChain
from llm.model import llm
from  GenerateReceipt import receipt_tool
from ReceipeGenerator import recipe_tool
from food_fetch import food_tool
from delivery import address_tool
from fastapi import FastAPI
import uvicorn
 
def chit_chat(user_query):
    first_prompt = ChatPromptTemplate.from_template(
       """You are a waiter at a restaurant. You should have conversation with the user.
        First greet the user and welcome the user to our restaurant and ask him if he would like to order something.
        Explain you need take the food order from the user.
        ### ask_for : ```food_name```
        Current conversation:
        {history}
        Human: {input}
        AI Assistant:
        # """
    )
    
    # info_chain = LLMChain(llm = llm, prompt=first_prompt, verbose=True)
    conversation_chain = ConversationChain(llm= llm, verbose = True,prompt = first_prompt, memory = ConversationBufferMemory(ai_prefix= "AI Assistant"))
    ai_chat = conversation_chain.run(user_query)
    print("Crete order tool")
    return ai_chat



chit_chat_tool = Tool(
        name = "ChitChatTool",
        func= chit_chat,
        description = "A tool that does conversation with the user, greets the user and has conversation with the user."
    )

tools = [
    receipt_tool,
    recipe_tool,
    food_tool,
    address_tool,
]

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a waiter at a restaurant. You should have conversation with the user.\
            First greet the user and welcome the user to our restaurant and ask him if he would like to order something.\
            Look up for tools to answer the user query do not make up your own answers. Only use tools to answer the user query",
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


app = FastAPI()


import json
@app.get("/restaurant/")
def stream(query: str):
    agent_output= agent_with_chat_history.invoke({"input":query},
        config={"configurable": {"session_id": "<foo>"}},
                                   )

    return agent
    
    
    print(agent_output)
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