from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import CSVLoader
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_text_splitters import  RecursiveCharacterTextSplitter
from dotenv import load_dotenv
load_dotenv()
import os
host = os.getenv('HOST')
port = os.getenv('PORT')

from langchain.vectorstores.milvus import Milvus

# loader = CSVLoader('ToolsAndModels\Datasets\menu.csv')
# docs = loader.load()
# text_splitter = RecursiveCharacterTextSplitter(chunk_size = 1000,chunk_overlap = 200)
# splits = text_splitter.split_documents(docs)
# embeddings = GoogleGenerativeAIEmbeddings(model = 'models/embedding-001')
embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
# vector_store = Chroma.from_documents(documents=splits, embedding=embeddings,collection_name='menu_data' ,persist_directory = './Chroma/')


# vector_store = Milvus.from_documents(docs,embeddings, connection_args={
#     'host':host,
#     'port':port
# }, collection_name="Food_Menu")

from langchain.vectorstores.milvus import Milvus
load_dotenv()
host = os.getenv('HOST')
port = os.getenv('PORT')
vector_store = Milvus(embeddings,connection_args={'host':host,'port':port},collection_name="Food_Menu")