from langchain.memory import ConversationBufferMemory
memory=ConversationBufferMemory()
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.chains import LLMChain, create_tagging_chain_pydantic
from langchain_core.tools import Tool
from langchain.memory import ConversationBufferMemory
from pydantic import BaseModel, Field
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

from llm.model import llm


class address(BaseModel):
    address:str=Field(description="This is the address of the customers in case of delivery.")
                                                                                              

# address_chain=create_tagging_chain_pydantic(address,llm)

def ask_user():
    ask_for=['service']
    first_prompt = ChatPromptTemplate.from_template(
        f'''You are a smart waiter at a restaurant. First  you should ask the user in conversational ways whether the user's order is delivery or dine-in.
        Don not ask addtional information just ask whether the order is delivery or dine-in.
        # Example:"Would you like to have a dine-in or delivery?"
        # ask_for:{ask_for}
        '''
    )   
    chain = LLMChain(llm=llm, prompt=first_prompt, verbose=True,memory=memory)
    conv = chain.run(ask_for=ask_for) 
    return conv

def ask_services():
    service_type=input(ask_user())
    first_prompt1 = ChatPromptTemplate.from_template(
       f""" You are a smart assistant waiter in a ABC restaurant.After the order, the user is asked whether he/she wants  delivery or dine-in.Your role is mentioned below:
       
        If the user wants delivery then tell them to provide their delivery address(only in case of delivery) 
       
        If the user wants dine-in then do nothing simply say thank you and enjoy the meal in our restaurant. 
        
        
       Provide staright forward answer related to whether the order is to be deliver or dine-in and do not ask any unwanted additional information
       
       # ask_for :{service_type}
      """     
      
    )


    chain = LLMChain(llm = llm, prompt=first_prompt1, verbose=True,memory=memory)
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
    "You are a smart assistant waiter in a ABC restaurant.After the order, the user is asked whether he/she wants  delivery or dine-in.Your role is mentioned below:\
        If the user wants delivery then tell them to provide their delivery address(only in case of delivery)\
        If the user wants dine-in then do nothing simply say thank you .\
       Provide staright forward answer related to whether the order is to be deliver or dine-in and do not ask any unwanted additional information"  
)


# address_prompt = ChatPromptTemplate.from_messages(
#      [
#     (
#         "system", 
#         "You are a smart assistant waiter in a ABC restaurant.After the order, the user is asked whether he/she wants  delivery or dine-in.Your role is mentioned below:\
#         If the user wants delivery then tell them to provide their delivery address(only in case of delivery)\
#         If the user wants dine-in then do nothing simply say thank you .\
#        Provide staright forward answer related to whether the order is to be deliver or dine-in and do not ask any unwanted additional information"
       
#     ),
#     ("human","{input}"),
#     ("placeholder","{agent_scratchpad}"),
#     ("placeholder","{tool_names}"),
#     ("placeholder","{tools}"),
#     ]
# )

# agent = create_tool_calling_agent(llm, address_tool, address_prompt)
# agent_executor = AgentExecutor( tools = address_tool, agent= agent,return_immediate_steps = False)

