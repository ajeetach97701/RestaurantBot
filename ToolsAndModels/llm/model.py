import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()
llm = ChatOpenAI(temperature = 0, model_name = 'gpt-3.5-turbo')