import os 
import time
import logging 
from typing import List, Optional, Union

from dotenv import load_dotenv

from flask import Blueprint, request, jsonify

from pinecone import Pinecone, ServerlessSpec

from langchain_groq import ChatGroq
from langchain.schema import Document 
from langchain.chains import RetrievalQA  
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain.text_splitter import RecursiveCharacterTextSplitter

from api.v1.models.mongo_db import mongodb
from api.v1.config.mongodb_config import MongoDBConfig
from api.v1.templates.utils import load_and_process_document
from api.v1.contants.http_status_codes import *
load_dotenv()

pincone_blueprint = Blueprint('pinecone', 
                              __name__, 
                              url_prefix='/api/v1/pinecone')

PINCONE_INDEX_NAME: str = "NerdmaAIReceptionist"

@pincone_blueprint.route('/rag_ai_agent', methods=['POST'])
def rag_ai_agent() -> None:

    query: str = request.get_json("query")
    top_k: int = request.get_json("topK")
    if top_k is None:
        top_k: int  = 2
    if query is None:
        return jsonify({"message": "Query is required"}), HTTP_400_BAD_REQUEST
    
    embeddings: OpenAIEmbeddings = OpenAIEmbeddings()
    index_name = PINCONE_INDEX_NAME
    
     
    vectorstore = PineconeVectorStore(index_name=index_name, 
                                      embedding=embeddings)
    
    vectorstore.similarity_search(query, 
                                  k = top_k)
    
    # completion llm  
    llm = ChatGroq(  
        temperature = 0, 
        model_name = 'mixtral-8x7b-32768',
        groq_api_key = os.getenv('GROQ_API_KEY')
    )  
    qa = RetrievalQA.from_chain_type(  
        llm=llm,  
        chain_type="stuff",  
        retriever=vectorstore.as_retriever()  
    )  
    answer = qa.run(query)  
    
    return jsonify({"answer": answer}), HTTP_200_OK


@pincone_blueprint.route('/create_search_index', methods=['POST'])
def create_search_index() -> None:
    
    pc = Pinecone(api_key= os.getenv('PINECONE_API_KEY'))  
    index_name = PINCONE_INDEX_NAME

    try: 
        existing_indexes: List[str] = [index_info["name"] for index_info in pc.list_indexes()]

        if index_name not in existing_indexes:
            pc.create_index(
                name=index_name,
                dimension=1536,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            )
            while not pc.describe_index(index_name).status["ready"]:
                time.sleep(1)

        index = pc.Index(index_name)
        return index 
    
    except Exception as e:
        print(f"An error occurred while creating the search index: {e}")
        return None
     
@pincone_blueprint.route('/create_embeddings', methods=['POST'])
def create_embeddings(file_path: str,
                       chunk_size: Optional[int] = 1000, 
                       chunk_overlap: Optional[int] = 20)-> List[Document]:
    
    mongodb_config: MongoDBConfig = MongoDBConfig()
    index_name: str = mongodb_config.vector_search_index_name
    
    embeddings: OpenAIEmbeddings = OpenAIEmbeddings()
 
    # Load document
    try: 
        documents = load_and_process_document(file_path)
    except Exception as e:
        print(f"An error occurred while loading and processing the document: {e}")
        return None
    
    try: 
        # Split document into chunks of text
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        docs = text_splitter.split_documents(documents)
        
        # Create a vector store
        docsearch = PineconeVectorStore.from_documents(docs, embeddings, index_name=index_name)
        return docsearch

    except Exception as e:
        print(f"An error occurred while creating the embeddings: {e}")
        return None
    
@pincone_blueprint.route('/delete_search_index', methods=['DELETE'])
def delete_search_index() -> Union[bool, None]:
  
    pc: Pinecone = Pinecone(api_key= os.getenv('PINECONE_API_KEY'))  
    index_name = PINCONE_INDEX_NAME

    try: 
        existing_indexes: List[str] = [index_info["name"] for index_info in pc.list_indexes()]

        if index_name in existing_indexes:
            pc.delete_index(index_name)
            while index_name in existing_indexes:
                time.sleep(1)
                existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]
        return True
     
    except Exception as e:
        print(f"An error occurred while deleting the search index: {e}")
        return None