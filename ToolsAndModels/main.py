from langchain_core.runnables import RunnableMap
from langchain.memory import ChatMessageHistory
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
memory = ChatMessageHistory(session_id="test-session")

# # Construct the Tools agent
agent = create_tool_calling_agent(llm, tools, prompt)

agent_executor = AgentExecutor(
    tools= tools, 
    agent= agent, 
    max_iterations= 5, 
    return_intermediate_steps= False, 
    verbose=True, 
    early_stopping_method ='generate')


memory = ChatMessageHistory(session_id="test-session")
tools = [address_tool]
agent = create_tool_calling_agent(llm, tools, address_prompt)
agent_executor = AgentExecutor( tools = tools, agent= agent,return_immediate_steps = False)
agent_with_chat_history = RunnableWithMessageHistory(
    agent_executor,
    # This is needed because in most real world scenarios, a session id is needed
    # It isn't really used here because we are using a simple in memory ChatMessageHistory
    lambda session_id: memory,
    input_messages_key="input",
    history_messages_key="chat_history",
)
# agent_executor.invoke({"input":"I want to have a delivery in Kapan"})



while True:
    print(agent_with_chat_history.invoke({"input":"I want to have a delivery"},
        config={"configurable": {"session_id": "<foo>"}},
                               ))
    print(agent_with_chat_history.invoke({"input":"Do you have fried chicken sandwich?"},
        config={"configurable": {"session_id": "<foo>"}},
                               ))
    print(agent_with_chat_history.invoke({"input":"What is its price?"},
    config={"configurable": {"session_id": "<foo>"}},
                               ))
    
    agent_with_chat_history.invoke({"input":"I have finished the order."},
    config={"configurable": {"session_id": "<foo>"}},
                               )
    # (agent_with_chat_history.invoke({"input":"I want it delivered."},
    # config={"configurable": {"session_id": "<foo>"}},
    # ))
    break

