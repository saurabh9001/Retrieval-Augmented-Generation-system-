#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Main CLI Interface for Sanskrit RAG System
Provides command-line interface for querying and testing the RAG system

"""

import os
import sys
import argparse
import time
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from rag_pipeline import RAGPipeline
from ingest import DocumentLoader, IndexBuilder, save_index_metadata


# ---------------- TEST QUERIES ---------------- #

TEST_QUERIES = [
    # English queries
    "What is dharma?",
    "Who is Krishna?",
    "What is the purpose of yoga?",
    "What does the Gita say about karma?",
    "What is moksha?",
    
    # Sanskrit queries
    "धर्मः किम्?",
    "कृष्णः कः?",
    "योगस्य उद्देश्यं किम्?",
    "गीता कर्मणः विषये किं वदति?",
]

# ---------------- MAIN FUNCTIONS ---------------- #

def run_test_mode():
    """Run automated test suite with predefined queries"""
    print("\n" + "="*60)
    print("🧪 RUNNING TEST SUITE WITH EVALUATION METRICS")
    print("="*60 + "\n")
    
    # Initialize RAG pipeline and evaluator
    print("🔧 Initializing RAG Pipeline...")
    rag = RAGPipeline()
    print("✅ RAG Pipeline Ready\n")
    
    print("📊 Initializing Evaluation Metrics...")
    evaluator = EvaluationMetrics()
    
    results = []
    eval_results = []
    total_time = 0
    
    for i, query in enumerate(TEST_QUERIES, 1):
        print(f"[{i}/{len(TEST_QUERIES)}] Query: {query}")
        
        try:
            answer, latency = rag.query(query)
            total_time += latency
            
            # Evaluate with semantic similarity
            eval_result = evaluator.evaluate_single_query(query, answer, latency)
            eval_results.append(eval_result)
            
            print(f"    Answer: {answer}")
            print(f"    Latency: {latency:.2f}s")
            print(f"    Similarity: {eval_result['similarity']:.2f}/100")
            
            # Check if answer is valid
            is_valid = eval_result["valid"]
            status = "✅" if is_valid else "⚠️"
            print(f"    Status: {status}\n")
            
            results.append({
                "query": query,
                "answer": answer,
                "latency": latency,
                "valid": is_valid,
                "similarity": eval_result['similarity']
            })
            
        except Exception as e:
            print(f"    ❌ Error: {str(e)}\n")
            results.append({
                "query": query,
                "answer": f"ERROR: {str(e)}",
                "latency": 0,
                "valid": False,
                "similarity": 0.0
            })
            eval_results.append({
                "query": query,
                "answer": f"ERROR: {str(e)}",
                "latency": 0,
                "valid": False,
                "similarity": 0.0,
                "answer_length": 0
            })
    
    # Print summary with evaluation metrics
    print("\n" + "="*60)
    print("📊 TEST SUMMARY WITH SEMANTIC EVALUATION")
    print("="*60)
    
    valid_count = sum(1 for r in results if r["valid"])
    total_count = len(results)
    avg_latency = total_time / total_count if total_count > 0 else 0
    
    # Calculate evaluation metrics
    batch_metrics = evaluator.evaluate_batch(eval_results)
    
    print(f"✅ Valid Answers: {valid_count}/{total_count}")
    print(f"⏱️  Average Latency: {avg_latency:.2f}s")
    print(f"⏱️  Total Time: {total_time:.2f}s")
    print(f"📈 Success Rate: {(valid_count/total_count)*100:.1f}%")
    print(f"🎯 Avg Semantic Similarity: {batch_metrics.get('avg_similarity', 0):.2f}/100")
    print(f"📏 Avg Answer Length: {batch_metrics.get('avg_answer_length', 0):.0f} chars")
    print("="*60 + "\n")
    
    # Detailed evaluation report
    evaluator.print_detailed_report(eval_results)
    
    return results


def run_interactive_mode():
    """Run interactive query mode"""
    print("\n" + "="*60)
    print("💬 INTERACTIVE MODE")
    print("="*60)
    print("Ask questions in English or Sanskrit (संस्कृत)")
    print("Type 'quit' or 'exit' to stop\n")
    
    # Initialize RAG pipeline
    print("🔧 Initializing RAG Pipeline...")
    rag = RAGPipeline()
    print("✅ RAG Pipeline Ready\n")
    
    while True:
        try:
            query = input("📝 Your Question: ").strip()
            
            if not query:
                continue
                
            if query.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!\n")
                break
            
            print("\n🔍 Processing...")
            answer, latency = rag.query(query)
            
            print(f"\n💡 Answer: {answer}")
            print(f"⏱️  Time: {latency:.2f}s\n")
            print("-" * 60 + "\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}\n")


def run_single_query(query: str):
    """Run a single query"""
    print("\n" + "="*60)
    print(f"📝 Query: {query}")
    print("="*60 + "\n")
    
    # Initialize RAG pipeline
    print("🔧 Initializing RAG Pipeline...")
    rag = RAGPipeline()
    print("✅ RAG Pipeline Ready\n")
    
    print("🔍 Processing...")
    answer, latency = rag.query(query)
    
    print(f"\n💡 Answer: {answer}")
    print(f"⏱️  Time: {latency:.2f}s")
    print("="*60 + "\n")


def rebuild_index(force: bool = False):
    """Rebuild the document index"""
    print("\n" + "="*60)
    print("🔨 REBUILDING INDEX")
    print("="*60 + "\n")
    
    try:
        if force:
            print("⚠️  Force rebuild enabled - deleting existing index...")
            if os.path.exists("./storage"):
                import shutil
                shutil.rmtree("./storage")
            print("✅ Existing index deleted\n")
        
        print("📚 Loading documents from data/...")
        documents = DocumentLoader.load_documents("data")
        
        print("🔧 Creating embeddings and building index...")
        print("⏳ This may take a few minutes...\n")
        
        start = time.time()
        builder = IndexBuilder()
        index = builder.build_and_persist_index(documents)
        save_index_metadata("data", "./storage")
        elapsed = time.time() - start
        
        print(f"\n✅ Index rebuilt successfully!")
        print(f"⏱️  Time taken: {elapsed:.2f}s")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error rebuilding index: {str(e)}")
        print("="*60 + "\n")
        sys.exit(1)


# ---------------- MAIN ---------------- #

def main():
    parser = argparse.ArgumentParser(
        description="Sanskrit RAG System - CLI Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --test                    # Run test suite
  python main.py                           # Interactive mode
  python main.py --query "What is dharma?" # Single query
  python main.py --rebuild                 # Rebuild index
  python main.py --force-rebuild           # Force rebuild index
        """
    )
    
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run automated test suite"
    )
    
    parser.add_argument(
        "--query", "-q",
        type=str,
        help="Run a single query"
    )
    
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Rebuild the document index"
    )
    
    parser.add_argument(
        "--force-rebuild",
        action="store_true",
        help="Force rebuild (delete existing index first)"
    )
    
    args = parser.parse_args()
    
    try:
        # Handle different modes
        if args.force_rebuild:
            rebuild_index(force=True)
        elif args.rebuild:
            rebuild_index(force=False)
        elif args.test:
            run_test_mode()
        elif args.query:
            run_single_query(args.query)
        else:
            # Default to interactive mode
            run_interactive_mode()
            
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal Error: {str(e)}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
