from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain.prompts import PromptTemplate

from langchain.chains import RetrievalQA
import re
# CHROMA Vector Databases 
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma

from langchain.chains import create_retrieval_chain

import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain


from langchain_community.document_loaders import JSONLoader
import json
from pathlib import Path
from pprint import pprint

with open("./schema_description.json", "r", encoding="utf-8") as file:
    sql_text = file.read()

sql_document = Document(page_content=sql_text, metadata={"source": "schema_description.json"})

text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=500)

final_document = text_splitter.split_documents([sql_document])

import os
from dotenv import load_dotenv
load_dotenv()

google_api_key = os.getenv("GOOGLE_API_KEY")


embedding = HuggingFaceBgeEmbeddings(
    model_name = "BAAI/bge-small-en-v1.5", # Model name
    model_kwargs = {"device" : "cpu"},
    encode_kwargs = {"normalize_embeddings" : True}
)

import numpy as np

np.array(embedding.embed_query(final_document[0].page_content))

# Load gemini into the llm
llm = ChatGoogleGenerativeAI(
    model='gemini-1.5-pro',
    google_api_key = os.getenv("GEMINI_API_KEY")
)

prompt = ChatPromptTemplate.from_template("""
Answer the following question based only on the provided context. 
Think step by step before providing a detailed answer. 
I will tip you $1000 if the user finds the answer helpful. 
<context>
{context}
</context>
Question: {input}""")

# Chain the llm and prompt into a chatbot
# Chain introduction
# Create stuff document chain


doc_chain = create_stuff_documents_chain(llm, prompt)

vector_store = Chroma.from_documents(final_document, embedding)

def get_answer():
    return vector_store

retriever = vector_store.as_retriever()
retriever

retriever_chain = create_retrieval_chain(retriever,doc_chain)

response = retriever_chain.invoke({'input': "Customer Info"})
print(response['answer'])