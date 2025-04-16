from metapub import PubMedFetcher
from backend.rag_pipeline.embeddings import GeminiEmbeddingModel
from backend.retriever.pubmed_retriever import PubMedAbstractRetriever
from backend.data.local_data_store import LocalJSONStore
from backend.rag_pipeline.chromadb import ChromaDbRag
import os
from dotenv import load_dotenv
load_dotenv()

query = "Does abamectin cause cancer?"
embeddings = GeminiEmbeddingModel(api_key=os.getenv("GOOGLE_API_KEY"))

# Step 1: Use PubMedAbstractRetriever to get abstract data for a query "Does abamectin cause cancer?"
pubmed_fetcher = PubMedFetcher()
abstract_retriever = PubMedAbstractRetriever(pubmed_fetcher)
storage_folder_path = "backend/data"
store = LocalJSONStore(storage_folder_path)
persist_directory = "backend/chromadb_storage"
rag_workflow = ChromaDbRag(persist_directory, embeddings)

# Step 2: Use the retrieved data with LocalJSONStorage to persist them in local storage
query_list = store.get_list_of_queries()
if query in query_list.values():
    # Query exists, retrieve query_id and documents from local storage
    query_id = [qid for qid, qtext in query_list.items() if qtext == query][0]
    documents = store.read_documents(query_id)
else:
    # Query does not exist, fetch data from PubMed and save to local storage
    abstracts = abstract_retriever.get_abstract_data(query)
    query_id = store.save_dataset(abstracts, query)
    documents = store.read_documents(query_id)

# Step 3: Use ChromDBRAGWorkflow to create a vector index using the list of documents created via LocalJSONStorage
vector_index = rag_workflow.create_vector_index_for_user_query(documents, query_id)

# Run similarity search on newly created index, using the original user query: 
print(vector_index.similarity_search(query, k=1)[0])