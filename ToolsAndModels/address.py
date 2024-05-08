from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.chains import LLMChain, create_tagging_chain_pydantic
from langchain_core.tools import Tool
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from pydantic import BaseModel, Field
from langchain.memory import ChatMessageHistory
memory = ChatMessageHistory(session_id="test-session")
from langchain.chains import ConversationChain
from llm.model import llm
from Redis.redis import setData, getData, deleteData, flushAll
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser, PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.chains import LLMChain, create_tagging_chain_pydantic
from langchain_core.tools import Tool
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from pydantic import BaseModel, Field
from langchain.memory import ChatMessageHistory
memory = ChatMessageHistory(session_id="test-session")
from langchain.chains import ConversationChain

from llm.model import llm
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser, PydanticOutputParser


class address(BaseModel):
    address:str=Field(description="This is the address of the customers in case of delivery.")
                                                                                              
parser = PydanticOutputParser(pydantic_object=address)

# address_chain=create_tagging_chain_pydantic(address,llm)

# def ask_user():
#     ask_for=['service']
#     first_prompt = ChatPromptTemplate.from_template(
#         f'''You are a smart waiter at a restaurant. First  you should ask the user in conversational ways whether the user's order is delivery or dine-in.
#         Don not ask addtional information just ask whether the order is delivery or dine-in.
#         # Example:"Would you like to have a dine-in or delivery?"
#         # ask_for:{ask_for}
#         '''
#     )   
#     chain = LLMChain(llm=llm, prompt=first_prompt, verbose=False)
#     conv = chain.run(ask_for=ask_for) 
#     return conv

def ask_services():
    # service_type=input(ask_user())
    # partial_variables={"format_instructions": parser.get_format_instructions()
    
    
    first_prompt1 = PromptTemplate(
        template= """ You are a smart assistant waiter in a ABC restaurant. When the user says he wants delivery, Ask him what his delivery address is.
       Provide staright forward answer related to the user query given in three backticks do not ask any unwanted additional information.
       ```{input}``` 
      """,
        input_variables=["input"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    
    chain = LLMChain(llm = llm, prompt=first_prompt1, verbose=False)
    convs = chain.run()
    return convs


def record_address(user_input):
    # user_input = input(ask_services())
    chain=create_tagging_chain_pydantic(address,llm)
    response=chain.run(user_input)
    print(response.address)
    return response

address_tool=Tool(
    name='deliveryaddress',
    func=record_address,
    description= " You are a smart assistant waiter in a ABC restaurant. When the user says he wants delivery, Ask him what his delivery address is.\
       Provide staright forward answer given do not ask any unwanted additional information.\ "
)


# address_prompt = ChatPromptTemplate.from_messages(
#      [
#     (
#         "system", 
#         "You are a smart assistant waiter in a ABC restaurant. Use the tool to answer the user query related to delivery"
       
#     ),
#     ("human","{input}"),
#     ("placeholder","{agent_scratchpad}"),
#     ("placeholder","{tool_names}"),
#     ("placeholder","{tools}"),
#     ]
# )

# memory = ChatMessageHistory(session_id="test-session")
# tools = [address_tool]
# agent = create_tool_calling_agent(llm, tools, address_prompt)

# agent_executor = AgentExecutor( tools = tools, agent= agent,return_immediate_steps = False)
# agent_with_chat_history = RunnableWithMessageHistory(
#     agent_executor,
#     # This is needed because in most real world scenarios, a session id is needed
#     # It isn't really used here because we are using a simple in memory ChatMessageHistory
#     lambda session_id: memory,
#     input_messages_key="input",
#     history_messages_key="chat_history",
# )
# # agent_ou = agent_executor.invoke({"input":"I want delivery."})

# agent_output = agent_with_chat_history.invoke({"input":"I have finished ordering and i want dinein."},
#     config={"configurable": {"session_id": "<foo>"}},
#                                )
# agent_output