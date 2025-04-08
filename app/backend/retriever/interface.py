from abc import ABC, abstractmethod
from typing import List
from backend.data.models import ScientificAbstract


class AbstractRetriever(ABC):
    """ Abstract class for retriever implementations. """
    @abstractmethod
    def get_abstract_data(self, scientist_question: str) -> List[ScientificAbstract]:
        """ Retrieve a list of scientific abstracts based on a given query. """
        raise NotImplementedError