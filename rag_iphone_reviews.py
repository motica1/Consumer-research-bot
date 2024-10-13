# Import necessary libraries
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine

def rag_iphone_reviews(query):
    # Load environment variables
    load_dotenv()

    # Load documents from a directory (you can change this path as needed)
    documents = SimpleDirectoryReader("data").load_data()

    # Create an index from the documents
    index = VectorStoreIndex.from_documents(documents)

    retriever = VectorIndexRetriever(index=index)

    # Create a query engine
    query_engine = RetrieverQueryEngine(retriever=retriever)

    # Example query
    response = query_engine.query(query)

    print(response)
