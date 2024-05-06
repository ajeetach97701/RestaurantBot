from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableMap
from langchain_core.prompts import ChatPromptTemplate
from database import vector_store
from llm.model import llm
from langchain_core.tools import Tool

parser = JsonOutputParser()
def get_suggestion(query):
    template = """
        You are provided Query in double backticks: ``{query}``.
        You are provided Context in triple backticks: ```{context}```
        The context contains information about the food items that are present in the restaurant.
        Match the prerequisite of the query with the given context and generate a suggestion to the user based on that.
        Provide only the name of food items with their prices In JSON FORMAT.
        If the query does not match with the available context, do not generate an answer.
    """
    prompt = ChatPromptTemplate.from_template(template)
    price_chain = RunnableMap(
        {
            'query': lambda x: x['query'],
            'context': lambda x: vector_store.similarity_search("All details and price of food item", k=30)
        }
    ) | prompt | llm | parser
    result = price_chain.invoke({'query':query})
    return result




suggestion_tool = Tool(
    name = "ApetizerSuggestionTool",
    func = get_suggestion,
    description="A tool that suggests food to the user."
    
)
