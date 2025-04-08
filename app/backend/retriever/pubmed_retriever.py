from typing import List
from metapub import PubMedFetcher
from backend.data.models import ScientificAbstract
from backend.retriever.interface import AbstractRetriever
from backend.retriever.pubmed_simplify_query import simplify_pubmed_query
import logging

class PubMedAbstractRetriever(AbstractRetriever):
    def __init__(self, pubmed_fetch_object: PubMedFetcher):
        self.pubmed_fetch_object = pubmed_fetch_object
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    def _simplify_pubmed_query(self, query: str, simplification_function: callable = simplify_pubmed_query) -> str:
        return simplification_function(query)

    def _get_abstract_list(self, query: str, simplify_query: bool = True) -> List[str]:
        """ Fetch a list of PubMed IDs for the given query. """
        if simplify_query:
            self.logger.info(f'Trying to simplify scientist query {query}')
            query_simplified = self._simplify_pubmed_query(query)

            if query_simplified != query:
                self.logger.info(f'Initial query simplified to: {query_simplified}')
                query = query_simplified
            else:
                self.logger.info('Initial query is simple enough and does not need simplification.')

        self.logger.info(f'Searching abstracts for query: {query}')
        return self.pubmed_fetch_object.pmids_for_query(query)

    def _get_abstracts(self, pubmed_ids: List[str]) -> List[ScientificAbstract]:
        """ Fetch PubMed abstracts  """
        self.logger.info(f'Fetching abstract data for following pubmed_ids: {pubmed_ids}')
        scientific_abstracts = []
        
        for id in pubmed_ids:
            abstract = self.pubmed_fetch_object.article_by_pmid(id)
            if abstract.abstract is None:
                continue
            
            abstract_formatted = ScientificAbstract(
                doi=abstract.doi,
                title=abstract.title,
                authors=abstract.authors,
                # authors=', '.join(abstract.authors),
                year=abstract.year,
                abstract_content=abstract.abstract
            )
            scientific_abstracts.append(abstract_formatted)

        self.logger.info(f'Total of {len(scientific_abstracts)} abstracts retrieved.')
        
        return scientific_abstracts

    def get_abstract_data(self, scientist_question: str, simplify_query: bool = True) -> List[ScientificAbstract]:
        """  Retrieve abstract list for scientist query. """
        pmids = self._get_abstract_list(scientist_question, simplify_query)
        abstracts = self._get_abstracts(pmids)
        return abstracts
    
if __name__ == "__main__":
    pubmed_fetch = PubMedAbstractRetriever(PubMedFetcher())
    query = 'what is the relationship between dental cavities and osteoporosis'
    abstracts = pubmed_fetch.get_abstract_data(query)
    print(f'query: {query}')
    print(f'number of abstracts: {len(abstracts)}\n')
    for abstract in abstracts:
        print(f'doi: {abstract.doi} \n title: {abstract.title} \n author: {abstract.authors} \n content:{abstract.abstract_content} \n \n')