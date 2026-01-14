#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Document Ingestion Module
Handles document loading, preprocessing, chunking, and index creation
"""

import os
import sys
import json
import time
import hashlib
import logging
from pathlib import Path
from typing import List

from llama_index.core import VectorStoreIndex, Settings, Document, StorageContext, load_index_from_storage
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# ---------------- LOGGING ---------------- #

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# ---------------- CONFIG ---------------- #

class Config:
    # Embeddings (multilingual – Sanskrit + English)
    # Upgraded to BAAI/bge-m3 for better Sanskrit-English understanding (92.88% vs 85.39% accuracy)
    EMBEDDING_MODEL = "BAAI/bge-m3"
    
    # Chunking
    CHUNK_SIZE = 256
    CHUNK_OVERLAP = 32
    
    # Storage
    PERSIST_DIR = "./storage"

# ---------------- DOCUMENT LOADER ---------------- #

class DocumentLoader:
    """Loads documents from specified directory"""
    
    @staticmethod
    def load_documents(data_dir: str) -> List[Document]:
        """
        Load all .txt documents from data directory
        
        Args:
            data_dir: Path to directory containing .txt files
            
        Returns:
            List of Document objects
        """
        data_path = Path(data_dir)
        if not data_path.exists():
            raise FileNotFoundError(f"Data directory not found: {data_dir}")

        docs = []
        for file in data_path.glob("*.txt"):
            logger.info(f"Loading: {file.name}")
            text = file.read_text(encoding="utf-8").strip()
            if text:
                docs.append(Document(text=text, metadata={"filename": file.name}))

        if not docs:
            raise ValueError("No valid .txt documents found")

        logger.info(f"Loaded {len(docs)} document(s)")
        return docs

# ---------------- INDEX BUILDER ---------------- #

class IndexBuilder:
    """Builds and persists vector index from documents"""
    
    def __init__(self):
        self._setup_embedding()
    
    def _setup_embedding(self):
        """Initialize embedding model and text splitter"""
        logger.info("Loading embedding model...")
        Settings.embed_model = HuggingFaceEmbedding(
            model_name=Config.EMBEDDING_MODEL,
            device="cpu",
        )
        
        Settings.text_splitter = SentenceSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP,
        )
        
        logger.info("Embedding model initialized ✔")
    
    def build_and_persist_index(self, documents: List[Document]) -> VectorStoreIndex:
        """
        Build vector index from documents and persist to disk
        
        Args:
            documents: List of Document objects
            
        Returns:
            VectorStoreIndex object
        """
        logger.info("Building vector index...")
        start = time.time()
        
        # Build index
        index = VectorStoreIndex.from_documents(documents)
        
        # Persist to disk
        logger.info(f"Persisting index to {Config.PERSIST_DIR}...")
        os.makedirs(Config.PERSIST_DIR, exist_ok=True)
        index.storage_context.persist(persist_dir=Config.PERSIST_DIR)
        
        logger.info(f"Index built and persisted in {time.time() - start:.2f}s ✔")
        return index


def save_index_metadata(data_dir: str, persist_dir: str):
    """Save metadata about the indexed documents"""
    data_path = Path(data_dir)
    file_hashes = []
    
    for file in sorted(data_path.glob("*.txt")):
        content = file.read_bytes()
        file_hash = hashlib.md5(content).hexdigest()
        file_hashes.append(f"{file.name}:{file_hash}")
    
    combined = "|".join(file_hashes)
    data_hash = hashlib.md5(combined.encode()).hexdigest()
    
    metadata = {
        "data_hash": data_hash,
        "data_dir": data_dir,
        "num_files": len(list(data_path.glob("*.txt")))
    }
    
    metadata_file = os.path.join(persist_dir, "index_metadata.json")
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    logger.info(f"Metadata saved: {metadata['num_files']} files indexed")

# ---------------- MAIN ---------------- #

def main():
    """Run document ingestion pipeline"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Ingest documents and build vector index")
    parser.add_argument("--data-dir", default="data", help="Directory containing .txt documents")
    args = parser.parse_args()
    
    try:
        # Load documents
        logger.info("Starting document ingestion...")
        documents = DocumentLoader.load_documents(args.data_dir)
        
        # Build and persist index
        builder = IndexBuilder()
        index = builder.build_and_persist_index(documents)
        
        # Save metadata for change detection
        save_index_metadata(args.data_dir, Config.PERSIST_DIR)
        
        logger.info("="*60)
        logger.info("✅ Ingestion complete!")
        logger.info(f"Documents processed: {len(documents)}")
        logger.info(f"Index saved to: {Config.PERSIST_DIR}")
        logger.info("="*60)
        
    except Exception as e:
        logger.error(f"❌ Ingestion failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
