from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_vector_db(documents, embedding_model):
    """
    Creates and returns an instance of the vector database.
    
    Args:
        documents (list): A list of Document objects to be stored in the vector database.
        embedding_model (object): The embedding model to use for vectorization.

    Returns:
        Chroma: A Chroma vector database instance.
    """
    vector_store = Chroma.from_documents(documents, embedding_model)
    return vector_store

def search_vector_db(vector_store, query, top_k=15):
    """
    Searches the vector database for the most similar documents.
    
    Args:
        vector_store (Chroma): The vector database instance.
        query (str): The user input text for similarity search.
        top_k (int): The number of top results to retrieve.

    Returns:
        list: A list of the most relevant documents.
    """
    results = vector_store.similarity_search(query, k=top_k)
    return results

# Load and process the schema document
with open("./schema_description.json", "r", encoding="utf-8") as file:
    sql_text = file.read()

sql_document = Document(page_content=sql_text, metadata={"source": "schema_description.json"})
text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=500)
final_document = text_splitter.split_documents([sql_document])

# Initialize embedding model
embedding = HuggingFaceBgeEmbeddings(
    model_name="BAAI/bge-small-en-v1.5",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True}
)


def wrapper():
    # # Create vector database instance
    vector_store = create_vector_db(final_document, embedding)
    return vector_store
# def get_json_data():
    
# # Example search query
# query = "Customer Info"
# results = search_vector_db(vector_store, query)

# # Print results
# for doc in results:
#     print(doc.page_content)
