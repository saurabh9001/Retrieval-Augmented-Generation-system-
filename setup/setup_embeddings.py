#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Setup Script - Download improved embedding model
Run this after installing requirements
"""

print("\n" + "="*70)
print("📥 DOWNLOADING IMPROVED EMBEDDING MODEL (BAAI/bge-m3)")
print("="*70)
print("\n🎯 Benefits:")
print("  • 8% better accuracy for Sanskrit-English understanding")
print("  • Research-backed: 92.88% vs 85.39% translation accuracy")
print("  • Better semantic similarity evaluation")
print("\n⏳ Downloading ~2.24 GB model (this may take 3-5 minutes)...\n")

try:
    from sentence_transformers import SentenceTransformer
    
    # Download model
    model = SentenceTransformer('BAAI/bge-m3', device='cpu')
    
    # Quick test
    embeddings = model.encode(["test"], show_progress_bar=False)
    
    print("\n✅ Model downloaded and cached successfully!")
    print("\n📚 Next steps:")
    print("  1. Rebuild index: python code/main.py --rebuild")
    print("  2. Run tests: python code/main.py --test")
    print("=" * 70 + "\n")
    
except ImportError:
    print("❌ Error: sentence-transformers not installed")
    print("   Run: pip install sentence-transformers")
except Exception as e:
    print(f"❌ Error: {e}")
    print("\n💡 Tip: Check internet connection and disk space (~3GB needed)")
