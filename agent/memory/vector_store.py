"""
Vector store module for the NBA Betting Agent.
This module provides semantic search capabilities for the agent's memory.
"""

import logging
import os
import json
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import faiss

class VectorStore:
    """
    Vector store for semantic search in the NBA betting agent.
    
    This class provides vector-based storage and retrieval of information,
    enabling semantic search capabilities for the agent.
    """
    
    def __init__(self, settings: Dict[str, Any]):
        """
        Initialize the vector store.
        
        Args:
            settings: Configuration settings for the vector store
        """
        self.logger = logging.getLogger(__name__)
        self.settings = settings
        
        # Vector dimension - depends on the embedding model used
        self.dimension = settings.get('dimension', 1536)  # Default for OpenAI embeddings
        
        # Storage paths
        self.base_path = settings.get('storage_path', 'data/models/vector_store')
        os.makedirs(self.base_path, exist_ok=True)
        
        # Initialize FAISS index
        self.index_path = os.path.join(self.base_path, 'faiss_index.bin')
        self.metadata_path = os.path.join(self.base_path, 'metadata.json')
        
        # Load or create index
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
            self.logger.debug(f"Loaded existing FAISS index with {self.index.ntotal} vectors")
        else:
            self.index = faiss.IndexFlatL2(self.dimension)
            self.logger.debug(f"Created new FAISS index with dimension {self.dimension}")
        
        # Load or create metadata
        if os.path.exists(self.metadata_path):
            with open(self.metadata_path, 'r') as f:
                self.metadata = json.load(f)
            self.logger.debug(f"Loaded metadata for {len(self.metadata)} vectors")
        else:
            self.metadata = []
            self.logger.debug("Created new metadata store")
    
    def add_vectors(self, vectors: np.ndarray, metadata_list: List[Dict[str, Any]]):
        """
        Add vectors and their metadata to the store.
        
        Args:
            vectors: Numpy array of vectors to add
            metadata_list: List of metadata dictionaries for each vector
        """
        if vectors.shape[0] != len(metadata_list):
            raise ValueError("Number of vectors must match number of metadata entries")
        
        # Add vectors to FAISS index
        self.index.add(vectors)
        
        # Add metadata
        self.metadata.extend(metadata_list)
        
        # Save index and metadata
        self._save_store()
        
        self.logger.debug(f"Added {vectors.shape[0]} vectors to the store")
    
    def search(self, query_vector: np.ndarray, k: int = 5) -> List[Tuple[Dict[str, Any], float]]:
        """
        Search for similar vectors in the store.
        
        Args:
            query_vector: Vector to search for
            k: Number of results to return
        
        Returns:
            List of tuples containing (metadata, distance)
        """
        if self.index.ntotal == 0:
            return []
        
        # Ensure query vector is 2D
        if query_vector.ndim == 1:
            query_vector = query_vector.reshape(1, -1)
        
        # Search for similar vectors
        distances, indices = self.index.search(query_vector, min(k, self.index.ntotal))
        
        # Prepare results
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1:  # FAISS returns -1 for invalid indices
                results.append((self.metadata[idx], float(distances[0][i])))
        
        return results
    
    def _save_store(self):
        """Save the index and metadata to disk."""
        faiss.write_index(self.index, self.index_path)
        
        with open(self.metadata_path, 'w') as f:
            json.dump(self.metadata, f, indent=2)
        
        self.logger.debug("Saved vector store to disk")
    
    def clear(self):
        """Clear the vector store."""
        self.index = faiss.IndexFlatL2(self.dimension)
        self.metadata = []
        self._save_store()
        self.logger.debug("Cleared vector store") 