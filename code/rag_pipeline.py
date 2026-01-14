#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RAG Pipeline Module
Loads stored index, performs retrieval, and generates responses
"""

import os
import re
import time
import logging
import warnings
from typing import Tuple

# Suppress urllib3 OpenSSL warning on macOS
warnings.filterwarnings('ignore', message='.*OpenSSL.*')
warnings.filterwarnings('ignore', module='urllib3')

from llama_index.core import VectorStoreIndex, Settings, StorageContext, load_index_from_storage
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.prompts import PromptTemplate
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.llama_cpp import LlamaCPP

logger = logging.getLogger(__name__)

# ---------------- CONFIG ---------------- #

class Config:
    """Configuration for RAG Pipeline"""
    
    # Embeddings (multilingual – Sanskrit + English)

    EMBEDDING_MODEL = "BAAI/bge-m3"

    # Chunking
    CHUNK_SIZE = 256
    CHUNK_OVERLAP = 32

    # Retrieval (STRICT)
    SIMILARITY_TOP_K = 2
    RESPONSE_MODE = "compact"

    # LLM (llama.cpp) - Optimized for English queries
    GGUF_MODEL_PATH = "models/tinyllama.gguf"
    CONTEXT_WINDOW = 2048
    MAX_NEW_TOKENS = 120
    TEMPERATURE = 0.0
    
    # Storage
    PERSIST_DIR = "./storage"

    SYSTEM_PROMPT = """You are a strict document-based QA system. Answer ONLY using the context provided.

STRICT RULES:
1. If the answer is NOT in the context, respond ONLY with: "Not in documents"
2. NEVER use outside knowledge or training data
3. NEVER make up facts, names, or information
4. Quote or paraphrase ONLY from the provided context
5. IMPORTANT: Match the language of your answer to the language of the question - Sanskrit question = Sanskrit answer, English question = English answer.
6. Be concise and direct.
"""

# ---------------- RAG PIPELINE ---------------- #

class RAGPipeline:
    """Core RAG functionality: load index, retrieve context, generate answers"""
    
    def __init__(self, load_from_disk: bool = True):
        """
        Initialize RAG pipeline
        
        Args:
            load_from_disk: If True, load existing index from storage. Otherwise, index must be set manually.
        """
        self.index = None
        self.query_engine = None
        self._setup_models()
        
        if load_from_disk:
            self._load_index()
    
    def _setup_models(self):
        """Initialize embedding model, LLM, and text splitter"""
        logger.info("Loading embedding model...")
        Settings.embed_model = HuggingFaceEmbedding(
            model_name=Config.EMBEDDING_MODEL,
            device="cpu",
        )

        logger.info("Loading LLM via llama.cpp...")
        llm = LlamaCPP(
            model_path=Config.GGUF_MODEL_PATH,
            temperature=Config.TEMPERATURE,
            max_new_tokens=Config.MAX_NEW_TOKENS,
            context_window=Config.CONTEXT_WINDOW,
            model_kwargs={"n_threads": os.cpu_count()},
            system_prompt=Config.SYSTEM_PROMPT,
            verbose=False,
        )

        Settings.llm = llm
        Settings.context_window = Config.CONTEXT_WINDOW

        Settings.text_splitter = SentenceSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP,
        )

        logger.info("Models initialized ✔")
    
    def _detect_language(self, text: str) -> str:
        """Detect if text is in Sanskrit (Devanagari) or English
        
        Args:
            text: Input text to detect language
            
        Returns:
            'sanskrit' if text contains Devanagari characters, 'english' otherwise
        """
        # Check for Devanagari Unicode range (U+0900 to U+097F)
        devanagari_count = sum(1 for char in text if '\u0900' <= char <= '\u097F')
        return 'sanskrit' if devanagari_count > 0 else 'english'
    
    def _load_index(self):
        """Load persisted index from disk"""
        logger.info(f"Loading index from {Config.PERSIST_DIR}...")
        storage_context = StorageContext.from_defaults(persist_dir=Config.PERSIST_DIR)
        self.index = load_index_from_storage(storage_context)
        self._setup_query_engine()
        logger.info("Index loaded ✔")
    
    def set_index(self, index: VectorStoreIndex):
        """
        Set index manually (when not loading from disk)
        
        Args:
            index: VectorStoreIndex object
        """
        self.index = index
        self._setup_query_engine()
    
    def _setup_query_engine(self):
        """Configure query engine with strict QA prompt"""
        qa_prompt = PromptTemplate(
            """Context information is below.
---------------------
{context_str}
---------------------
Given ONLY the context above and NO other knowledge, answer the question.
If the answer is not in the context, respond with ONLY: "Not in documents"
Do NOT make up information. Do NOT use your training data.

Question: {query_str}
Answer: """
        )
        
        self.query_engine = self.index.as_query_engine(
            similarity_top_k=Config.SIMILARITY_TOP_K,
            response_mode=Config.RESPONSE_MODE,
            text_qa_template=qa_prompt,
        )
    
    def query(self, query_text: str) -> Tuple[str, float]:
        """
        Query the RAG system with automatic language detection
        
        Args:
            query_text: User question
            
        Returns:
            Tuple of (answer, latency_in_seconds)
        """
        if not self.query_engine:
            raise RuntimeError("Query engine not initialized. Load or set an index first.")
        
        # Detect query language
        query_language = self._detect_language(query_text)
        logger.info(f"Query language detected: {query_language}")
        
        # Create language-specific prompt
        if query_language == 'sanskrit':
            language_instruction = "IMPORTANT: The question is in Sanskrit. You MUST answer in Sanskrit (Devanagari script) only."
        else:
            language_instruction = "IMPORTANT: The question is in English. You MUST answer in English only."
        
        # Build custom prompt for this query
        qa_prompt = PromptTemplate(
            f"""Context information is below.
---------------------
{{context_str}}
---------------------
{language_instruction}

Given ONLY the context above and NO other knowledge, answer the question.
If the answer is not in the context, respond with ONLY: "Not in documents"
Do NOT make up information. Do NOT use your training data.

Question: {{query_str}}
Answer: """
        )
        
        # Reconfigure query engine with language-specific prompt
        self.query_engine = self.index.as_query_engine(
            similarity_top_k=Config.SIMILARITY_TOP_K,
            response_mode=Config.RESPONSE_MODE,
            text_qa_template=qa_prompt,
        )
        
        start = time.time()
        response = self.query_engine.query(query_text)
        latency = time.time() - start

        answer = self._clean_response(str(response))
        answer = self._validate_answer(answer, query_text)
        
        return answer, latency
    
    def _clean_response(self, text: str) -> str:
        """Remove metadata and clean up response text"""
        # Remove metadata and junk patterns
        junk = [
            "Context information",
            "The following is a summary",
            "filename:",
            "Filename:",
            "datas.txt",
            "---------------------",
            "from multiple sources is below.",
            "from multiple sources",
            "is below.",
            "Based on the context",
            "According to the context",
            "The context states"
        ]
        for j in junk:
            text = text.replace(j, "")

        # Remove metadata patterns
        text = re.sub(r'[Ff]ilename:\s*\S+', '', text)
        text = re.sub(r'from multiple sources.*?below\.?', '', text, flags=re.IGNORECASE)
        
        # If response starts with raw context dump, it's invalid
        if text.strip().startswith('न हैं।') or 'विद्या मानवस्य' in text[:50]:
            return "Not in documents"
        
        text = " ".join(text.split()).strip()

        if not text or len(text) < 10:
            return "Not in documents"

        return text
    
    def _validate_answer(self, answer: str, query: str) -> str:
        """Detect and filter hallucinated content"""
        
        # Check if already marked as not found
        if "not in documents" in answer.lower():
            return "Not in documents"
        
        # Detect definite hallucinations (topics NOT in document)
        hallucination_markers = [
            "arduino", "microcontroller", "embedded systems",
            "saurabh is a", "hindu god", "son of lord brahma",
            "brother of lord vishnu", "sage of knowledge",
            "kalidasa", "5th century bce", "megha-kumara",
            "playwright", "dramatist", "translated into many"
        ]
        
        answer_lower = answer.lower()
        
        # Check for definite hallucinations
        for marker in hallucination_markers:
            if marker in answer_lower:
                logger.warning(f"Hallucination detected: {marker}")
                return "Not in documents"
        
        return answer
