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


def ask_user():
    ask_for=['service']
    first_prompt = ChatPromptTemplate.from_template(
        f'''You are a smart waiter at a restaurant. First  you should ask the user in conversational ways whether the user's order is delivery or dine-in.
        Don not ask addtional information just ask whether the order is delivery or dine-in.
        # Example:"Would you like to have a dine-in or delivery?"
        # ask_for:{ask_for}
        '''
    )   
    chain = LLMChain(llm=llm, prompt=first_prompt, verbose=True)
    conv = chain.run(ask_for=ask_for) 
    return conv

def ask_services():
    service_type=input(ask_user())
    # partial_variables={"format_instructions": parser.get_format_instructions()
    
    
    first_prompt1 = PromptTemplate(
        template= f""" You are a smart assistant waiter in a ABC restaurant.After the order, the user is asked whether he/she wants  delivery or dine-in.Your role is mentioned below:
       
        If the user wants delivery then tell them to provide their delivery address(only in case of delivery) 
       
        If the user wants dine-in then do nothing simply say thank you and enjoy the meal in our restaurant. 
        
        
       Provide staright forward answer related to whether the order is to be deliver or dine-in and do not ask any unwanted additional information
       
       # ask_for :{service_type}
      """     ,
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    
    chain = LLMChain(llm = llm, prompt=first_prompt1, verbose=True)
    convs = chain.run(ask_for=service_type)
    return convs


def record_address(user_input):
    user_input=input(ask_services())
    chain=create_tagging_chain_pydantic(address,llm)
    response=chain.run(user_input)
    return response

address_tool=Tool(
    name='deliveryaddress',
    func=record_address,
    description=
    "You are a smart assistant waiter in a ABC restaurant. When the user says he has finished his ordering, ask the  whether he/she wants  delivery or dine-in.Your role is mentioned below:\
        If the user wants delivery then tell them to provide their delivery address(only in case of delivery)\
        If the user wants dine-in then do nothing simply say thank you .\
       Provide staright forward answer related to whether the order is to be deliver or dine-in and do not ask any unwanted additional information"  
)


address_prompt = ChatPromptTemplate.from_messages(
     [
    (
        "system", 
        "You are a smart assistant waiter in a ABC restaurant.After the order, the user is asked whether he/she wants  delivery or dine-in.Your role is mentioned below:\
        If the user wants delivery then tell them to provide their delivery address(only in case of delivery)\
        If the user wants dine-in then do nothing simply say thank you .\
       Provide staright forward answer related to whether the order is to be deliver or dine-in and do not ask any unwanted additional information"
       
    ),
    ("human","{input}"),
    ("placeholder","{agent_scratchpad}"),
    ("placeholder","{tool_names}"),
    ("placeholder","{tools}"),
    ]
)

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

agent_with_chat_history.invoke({"input":"I have finished the order."},
    config={"configurable": {"session_id": "<foo>"}},
                               )