from langchain_core.runnables import RunnableMap, RunnablePassthrough
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import Tool
from llm.model import llm
from database import vector_store

def food_verify(user_input):
    print(user_input)
    # food_name_retriever = vector_store.as_retriever(search_type= 'mmr', kwargs=6)
    # food_name_retriever = vector_store.similarity_search(user_input)
    food_template = """You are a virtual Restaurant Waiter. Your task is to check if the given food_name is present in the context or not. 
    If the food is available in the context and has multiple foods for it, show the user with all the available food names with its price.
    The output should be of JSON FORMAT without any backticks which is given in four backticks return only :
    If the user asks for menu, show them top 5 data from context.
    If not tell them that the option is not available and ask them if they would like to order something else?
    Context is given in three backticks: ```{context}```
    User provided food name is given in double backticks: ``{input}``
    """
    prompt_recipe = PromptTemplate(
        input_variables=["context","input"],
        template=food_template
    )
    chain = RunnableMap({
        "context": lambda x: vector_store.similarity_search(x['input'], k=8),
        "input": lambda x: x['input']
    }) | prompt_recipe | llm | JsonOutputParser()

    return chain.invoke({"input":"I want to order a burger"})
# food_chain

food_tool = Tool(
    name = "FoodverifyTool",
    func = food_verify,
    description="A tool that checks for food availability in the context."
    
)



# food_prompt = ChatPromptTemplate.from_messages(
#     [
#     (
#         "assistant", 
#         "You are an restaurant waiter that verifies food name. Please use the tool for answering the questions.Do not look up for answer elsewhere only use the tool to look for answer ."
#     ),
#     ("human","{input}"),
#     ("placeholder","{agent_scratchpad}"),
#     ("placeholder","{tool_names}"),
#     ("placeholder","{tools}"),
#     ]
# )


# agent = create_tool_calling_agent(llm = llm, tools= [food_tool], prompt= food_prompt)
# agent_executor = AgentExecutor(
#     tools= [food_tool], 
#     agent= agent, 
#     max_iterations= 5, 
#     return_intermediate_steps= False, 
#     verbose=True, 
#     early_stopping_method ='generate')
# ag_response = agent_executor.invoke({"input":"I want to have a Sandwich?"})
