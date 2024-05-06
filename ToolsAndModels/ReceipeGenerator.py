import os
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_core.runnables import RunnableMap, RunnablePassthrough
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import CSVLoader
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain.agents import AgentExecutor, create_tool_calling_agent, initialize_agent, AgentType
from langchain.tools.retriever import create_retriever_tool
from langchain_text_splitters import  RecursiveCharacterTextSplitter
from langchain.chains import LLMChain, create_tagging_chain_pydantic
from langchain_core.tools import Tool
from langchain.memory import ConversationBufferMemory
from pydantic import BaseModel, Field
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from llm.model import llm
from database import vector_store








# 1. Create a tool
def recipe(user_input):
    
    recipe_retriever = vector_store.as_retriever(search_type = 'mmr', k= 5)
    recipe_template = """### Instruction ###
        You are a good Virtual Assistant . When a user asks you about recipe/ingredients or price of a particular item you have to answer him the recipe or price of the food item based on the context and make sure
        to provide all the details.
        Context is given in triple back ticks: ```{context}```
        Question is given in double back ticks:  ``{question}``
        If the question is out of context, do not provide the wrong answer just say I am sorry i can't answer to that question.
        ### Your Response must be in JSON FORMAT and similar to like this:
        We have multiple options for Sandwich: 
        1.Chicken Breast Sandwich Recipe: "Marinate chicken breasts in olive oil, lemon juice, garlic, and herbs. Grill until cooked through. Toast sandwich buns and assemble with grilled chicken, lettuce, tomato, and mayonnaise. Optionally, add toppings like avocado or bacon. Serve warm for a delicious and wholesome Chicken Breast Sandwich."
    """
    prompt_recipe = PromptTemplate(
        input_variables=["context","question"],
        template=recipe_template
    ) 
    recipe_chain = (
        {"context":recipe_retriever, "question":RunnablePassthrough()}
        | prompt_recipe
        | llm
        | JsonOutputParser()
    )
    print("recipe tool")
    return recipe_chain.invoke(user_input)

recipe_tool = Tool(
    name = "RecipeTool",
    func = recipe,
    description="A Tool that returns recipe of a food"
    
)
