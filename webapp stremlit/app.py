#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Streamlit Web UI for Sanskrit RAG System
Simple interface for querying the RAG system in English or Sanskrit
"""

import sys
import time
import streamlit as st
from pathlib import Path

# Add code directory to path
sys.path.insert(0, 'code')

from rag_pipeline import RAGPipeline

# ---------------- PAGE CONFIG ---------------- #

st.set_page_config(
    page_title="Sanskrit RAG System",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ---------------- CUSTOM CSS ---------------- #

st.markdown("""
    <style>
    /* Style the sidebar button in top-left corner */
    button[kind="header"] {
        background-color: #FF6B35 !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 8px 16px !important;
        font-weight: bold !important;
        font-size: 14px !important;
        border: none !important;
        box-shadow: 0 2px 8px rgba(255, 107, 53, 0.4) !important;
    }
    button[kind="header"]:hover {
        background-color: #ff8c5a !important;
        box-shadow: 0 4px 12px rgba(255, 107, 53, 0.6) !important;
    }
    
    /* Make sidebar toggle button more visible with label */
    [data-testid="collapsedControl"] {
        background: linear-gradient(135deg, #FF6B35 0%, #ff8c5a 100%) !important;
        border-radius: 10px !important;
        min-width: 160px !important;
        height: 55px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 4px 12px rgba(255, 107, 53, 0.5) !important;
        border: 2px solid white !important;
        cursor: pointer !important;
        padding: 0 15px !important;
    }
    [data-testid="collapsedControl"]::after {
        content: "→ 📂 View Documents & Files" !important;
        color: white !important;
        font-size: 15px !important;
        font-weight: bold !important;
        margin-left: 5px !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2) !important;
    }
    [data-testid="collapsedControl"]:hover {
        background: linear-gradient(135deg, #ff8c5a 0%, #ffaa7a 100%) !important;
        box-shadow: 0 6px 16px rgba(255, 107, 53, 0.7) !important;
        transform: scale(1.05) !important;
    }
    [data-testid="collapsedControl"] svg {
        display: none !important;
    }
    
    .main-title {
        text-align: center;
        color: #FF6B35;
        font-size: 2.8rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .subtitle {
        text-align: center;
        color: #888;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .query-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        margin: 1rem 0;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .answer-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        border-left: 5px solid #FF6B35;
        margin: 1rem 0;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        font-size: 1.05rem;
        line-height: 1.6;
        word-wrap: break-word;
        overflow-wrap: break-word;
        white-space: pre-wrap;
    }
    .stats-box {
        background-color: #fff3cd;
        padding: 0.5rem;
        border-radius: 0.3rem;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
    .language-badge {
        display: inline-block;
        padding: 0.4rem 1rem;
        border-radius: 1.5rem;
        font-size: 0.9rem;
        font-weight: bold;
        margin-right: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .english-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    .sanskrit-badge {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------- INITIALIZE RAG ---------------- #

@st.cache_resource
def load_rag_pipeline():
    """Load RAG pipeline (cached to avoid reloading)"""
    with st.spinner("🔄 Loading RAG system..."):
        pipeline = RAGPipeline(load_from_disk=True)
    return pipeline

# ---------------- HELPER FUNCTIONS ---------------- #

def detect_language(text: str) -> str:
    """Detect if text is in Sanskrit (Devanagari) or English"""
    devanagari_count = sum(1 for char in text if '\u0900' <= char <= '\u097F')
    return 'Sanskrit' if devanagari_count > 0 else 'English'

def format_answer(answer: str, language: str, latency: float):
    """Format and display the answer with metadata"""
    
    # Language badge
    badge_class = "sanskrit-badge" if language == "Sanskrit" else "english-badge"
    st.markdown(f"""
        <div>
            <span class="language-badge {badge_class}">📖 {language}</span>
            <span class="language-badge english-badge">⏱️ {latency:.2f}s</span>
        </div>
    """, unsafe_allow_html=True)
    
    # Answer box
    st.markdown(f"""
        <div class="answer-box">
            <strong>Answer:</strong><br>
            {answer}
        </div>
    """, unsafe_allow_html=True)

# ---------------- MAIN APP ---------------- #

def main():
    # Header
    st.markdown('<p class="main-title">📚 Sanskrit RAG System</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Ask questions in English or Sanskrit (संस्कृत)</p>', unsafe_allow_html=True)
    
    # Load pipeline
    try:
        pipeline = load_rag_pipeline()
        st.success("✅ System ready!")
    except Exception as e:
        st.error(f"❌ Failed to load RAG system: {e}")
        st.info("💡 Make sure to run `python code/ingest.py` first to build the index.")
        st.stop()
    
    st.markdown("---")
    
    # Query input
    st.markdown("### 💬 Ask Your Question")
    
    # Check if example was clicked
    if 'example_query' in st.session_state:
        query = st.session_state.example_query
        del st.session_state.example_query
    else:
        query = ""
    
    # Text area for query
    query = st.text_area(
        label="Enter your question",
        placeholder="Example: What is karma? or विद्या किं अस्ति?",
        height=100,
        label_visibility="collapsed",
        value=query
    )
    
    # Query button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        submit_button = st.button("🔍 Get Answer", use_container_width=True, type="primary")
    
    # Process query
    if submit_button and query.strip():
        # Detect language
        language = detect_language(query)
        
        # Show query info
        st.markdown("---")
        st.markdown("### 📝 Query Details")
        st.markdown(f"""
            <div class="query-box">
                <strong>Question:</strong> {query}<br>
                <strong>Detected Language:</strong> {language}
            </div>
        """, unsafe_allow_html=True)
        
        # Get answer
        with st.spinner("🤔 Thinking..."):
            try:
                answer, latency = pipeline.query(query)
                
                # Display answer
                st.markdown("### 💡 Response")
                format_answer(answer, language, latency)
                
            except Exception as e:
                st.error(f"❌ Error: {e}")
    
    elif submit_button:
        st.warning("⚠️ Please enter a question first!")
    
    # Sidebar with examples
    with st.sidebar:
        st.markdown("### 📂 Data Files")
        
        # Show all files in data folder
        data_dir = Path("data")
        if data_dir.exists():
            txt_files = sorted(data_dir.glob("*.txt"))
            
            if txt_files:
                for file in txt_files:
                    with st.expander(f"📄 {file.name}"):
                        try:
                            content = file.read_text(encoding='utf-8')
                            st.text_area(
                                label="File content",
                                value=content,
                                height=200,
                                disabled=True,
                                label_visibility="collapsed"
                            )
                            st.caption(f"Size: {len(content)} characters")
                        except Exception as e:
                            st.error(f"Error reading file: {e}")
            else:
                st.warning("No .txt files found in data folder")
        else:
            st.error("Data folder not found")
        
        st.markdown("---")
        st.markdown("### 💡 Example Questions")
        st.markdown("Click any question to try it:")
        
        # Create a nicer UI for example questions
        st.markdown("#### 🇬🇧 English Questions")
        
        english_examples = [
            "What is the foundation of human life?",
            "What is the theory of karma?",
            "What does the Bhagavad Gita teach?",
            "What is righteousness?",
            "What is truth?"
        ]
        
        for i, example in enumerate(english_examples, 1):
            if st.button(f"📌 {example}", key=f"en_{i}", use_container_width=True):
                st.session_state.example_query = example
                st.rerun()
        
        st.markdown("#### 🇮🇳 Sanskrit Questions (संस्कृत)")
        
        sanskrit_examples = [
            ("विद्या किं अस्ति?", "What is knowledge?"),
            ("कर्म सिद्धान्तः कः?", "What is the theory of karma?"),
            ("धर्मः किम् अर्थः?", "What is righteousness?")
        ]
        
        for i, (sanskrit, english) in enumerate(sanskrit_examples, 1):
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button(f"📌 {sanskrit}", key=f"sa_{i}", use_container_width=True):
                    st.session_state.example_query = sanskrit
                    st.rerun()
            with col2:
                st.caption(english)
        
        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.info("""
        This RAG system answers questions based on Sanskrit documents.
        
        **Features:**
        - 🌐 Bilingual (English & Sanskrit)
        - 🎯 Document-based answers only
        - ⚡ Fast CPU inference
        - 🔒 No hallucinations
        """)

# ---------------- RUN APP ---------------- #

if __name__ == "__main__":
    main()
