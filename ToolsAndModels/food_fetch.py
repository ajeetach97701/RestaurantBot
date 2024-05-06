from langchain_core.runnables import RunnableMap, RunnablePassthrough
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import Tool
from llm.model import llm
from database import vector_store






def food_verify(user_input):
    food_name_retriever = vector_store.as_retriever(search_type = 'mmr', k= 5)
    food_template = """You are a virtual Restaurant Waiter. Your task is to check if the given food_name is present in the context or not. 
    If the food is available in the context and has multiple foods for it, show the user with all the available food names with its price.
    The output should be of JSON FORMAT without any backticks which is given in four backticks return only :
    If not tell them that the option is not available and ask them if they would like to order something else?
    Context is given in three backticks: ```{context}```
    User provided food name is given in double backticks: ``{input}``
    """
    prompt_recipe = PromptTemplate(
        input_variables=["context","input"],
        template=food_template
    ) 
    food_chain = (
        {"context":food_name_retriever, "input":RunnablePassthrough()}
        | prompt_recipe
        | llm
        | JsonOutputParser()
    )
    print("food tool")
    return food_chain.invoke(user_input)


food_tool = Tool(
    name = "FoodverifyTool",
    func = food_verify,
    description="A tool that checks for food availability in the context"
    
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
