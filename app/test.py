from metapub import PubMedFetcher
from backend.retriever.pubmed_retriever import PubMedAbstractRetriever
import dotenv

dotenv.load_dotenv()

if __name__ == "__main__":
    pubmed_fetch = PubMedAbstractRetriever(PubMedFetcher())
    query = 'what is the relationship between dental cavities and osteoporosis'
    abstracts = pubmed_fetch.get_abstract_data(query, simplify_query=False)
    print(f'query: {query}')
    print(f'number of abstracts: {len(abstracts)}\n')
    
    abstracts = pubmed_fetch.get_abstract_data(query, simplify_query=True)
    print(f'query: {query}')
    print(f'number of abstracts: {len(abstracts)}\n')
    