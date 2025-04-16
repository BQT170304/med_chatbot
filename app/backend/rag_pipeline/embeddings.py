import os
from typing import List, Union, Optional
import numpy as np
from google import genai
from google.genai import types


class GeminiEmbeddingModel:
    """Wrapper for Google's Gemini embedding model."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "text-embedding-004",
    ):
        """
        Initialize the Gemini embedding model.
        
        Args:
            api_key: Google API key. If None, uses GOOGLE_API_KEY environment variable.
            model_name: The name of the embedding model to use.
        """
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("API key must be provided as parameter or environment variable.")
        
        self.model_name = model_name
        self.client = genai.Client(api_key=self.api_key)
        
    def embed(self, text: Union[str, List[str]]) -> np.ndarray:
        """
        Generate embeddings for a single text or list of texts.
        
        Args:
            text: A single string or list of strings to generate embeddings for.
            
        Returns:
            Numpy array of embeddings with shape (n_texts, embedding_dim).
        """
        if isinstance(text, str):
            return self._embed_single(text)
        elif isinstance(text, list):
            return self._embed_batch(text)
        else:
            raise TypeError("Input must be a string or a list of strings.")
    
    def _embed_single(self, text: str) -> np.ndarray:
        """Generate embedding for a single text string."""
        try:
            result = self.client.models.embed_content(
                model=self.model_name,
                contents=text,
                config=types.EmbedContentConfig(task_type="RETRIEVAL-DOCUMENT"),
            )
            return np.array(result.embeddings[0].values, dtype=np.float32)
        except Exception as e:
            raise RuntimeError(f"Error generating embedding: {str(e)}")
    
    def _embed_batch(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for a batch of text strings."""
        if not texts:
            return np.array([])
        
        embeddings = []
        for text in texts:
            embedding = self._embed_single(text)
            embeddings.append(embedding)
        
        return np.stack(embeddings)
    
    # Thêm các phương thức để tương thích với LangChain
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of documents.
        This method is required by LangChain's vectorstore implementations.
        
        Args:
            texts: List of document texts to embed
            
        Returns:
            List of embedding vectors as lists of floats
        """
        embeddings = self._embed_batch(texts)
        return embeddings.tolist()
    
    def embed_query(self, text: str) -> List[float]:
        """
        Generate embedding for a query text.
        This method is required by LangChain's vectorstore implementations.
        
        Args:
            text: Query text to embed
            
        Returns:
            Embedding vector as a list of floats
        """
        embedding = self._embed_single(text)
        return embedding.tolist()
    
    @property
    def embedding_dimension(self) -> int:
        """Get the dimension of the embedding vectors."""
        sample_text = "Sample text to determine embedding dimension."
        embedding = self._embed_single(sample_text)
        return embedding.shape[0]