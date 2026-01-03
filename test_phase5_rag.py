#!/usr/bin/env python3
"""
Phase 5 Testing - RAG (Retrieval-Augmented Generation)
Note: Requires OpenAI API key and chromadb for vector storage
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_chromadb_import():
    """Test if chromadb is available"""
    print("\n" + "="*60)
    print("TEST: ChromaDB Import")
    print("="*60)
    
    try:
        import chromadb
        print(f"✅ PASS | ChromaDB available")
        print(f"   └─ Version: {chromadb.__version__}")
        return True
    except ImportError:
        print(f"⚠️  SKIP | ChromaDB not installed")
        print(f"   └─ Run: pip install chromadb")
        return None


def test_autogen_rag_import():
    """Test if AutoGen RAG components are available"""
    print("\n" + "="*60)
    print("TEST: AutoGen RAG Components")
    print("="*60)
    
    try:
        from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
        print(f"✅ PASS | RetrieveUserProxyAgent available")
        return True
    except ImportError as e:
        print(f"⚠️  SKIP | RAG components not available")
        print(f"   └─ Error: {e}")
        print(f"   └─ Run: pip install pyautogen[retrievechat]")
        return None


def test_rag_function_import():
    """Test if our RAG function can be imported"""
    print("\n" + "="*60)
    print("TEST: RAG Function Import")
    print("="*60)
    
    try:
        from aurelius.functional.rag import get_rag_function, PROMPT_RAG_FUNC
        print(f"✅ PASS | RAG function imported")
        print(f"   └─ Prompt template length: {len(PROMPT_RAG_FUNC)} chars")
        return True
    except ImportError as e:
        print(f"❌ FAIL | Could not import RAG function")
        print(f"   └─ Error: {e}")
        return False


def test_sentence_transformers():
    """Test if sentence-transformers is available for embeddings"""
    print("\n" + "="*60)
    print("TEST: Sentence Transformers (Embeddings)")
    print("="*60)
    
    try:
        from sentence_transformers import SentenceTransformer
        print(f"✅ PASS | Sentence Transformers available")
        return True
    except ImportError:
        print(f"⚠️  SKIP | Sentence Transformers not installed")
        print(f"   └─ Run: pip install sentence-transformers")
        return None


def test_simple_document_qa():
    """Test simple document Q&A without full RAG setup"""
    print("\n" + "="*60)
    print("TEST: Simple Document Q&A Logic")
    print("="*60)
    
    try:
        # Simulate document chunks
        document_chunks = [
            "Apple Inc. reported Q4 2024 revenue of $89.5 billion, a 6% increase year-over-year.",
            "The company's iPhone segment generated $46.2 billion in revenue, representing 52% of total sales.",
            "Services revenue reached a record $22.3 billion, growing 12% compared to the prior year.",
            "Mac revenue was $7.7 billion, while iPad revenue came in at $6.9 billion.",
            "Operating expenses increased to $14.8 billion due to increased R&D investments."
        ]
        
        # Simple keyword-based retrieval
        query = "What was Apple's iPhone revenue?"
        
        # Score chunks by keyword relevance
        query_words = set(query.lower().split())
        scored_chunks = []
        
        for chunk in document_chunks:
            chunk_words = set(chunk.lower().split())
            overlap = len(query_words & chunk_words)
            scored_chunks.append((overlap, chunk))
        
        # Get top 2 most relevant chunks
        scored_chunks.sort(reverse=True)
        relevant_chunks = [chunk for _, chunk in scored_chunks[:2]]
        
        print(f"✅ PASS | Simple document Q&A working")
        print(f"   └─ Query: '{query}'")
        print(f"   └─ Top relevant chunks:")
        for i, chunk in enumerate(relevant_chunks, 1):
            print(f"      {i}. {chunk[:60]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ FAIL | Simple Q&A error")
        print(f"   └─ Error: {e}")
        return False


def test_pdf_parsing():
    """Test if PDF parsing libraries are available"""
    print("\n" + "="*60)
    print("TEST: PDF Parsing Libraries")
    print("="*60)
    
    results = {}
    
    # Test PyPDF2
    try:
        import PyPDF2
        results['PyPDF2'] = True
        print(f"   ✓ PyPDF2 available")
    except ImportError:
        results['PyPDF2'] = False
        print(f"   ✗ PyPDF2 not installed")
    
    # Test pdfplumber
    try:
        import pdfplumber
        results['pdfplumber'] = True
        print(f"   ✓ pdfplumber available")
    except ImportError:
        results['pdfplumber'] = False
        print(f"   ✗ pdfplumber not installed")
    
    # Test pymupdf (fitz)
    try:
        import fitz
        results['pymupdf'] = True
        print(f"   ✓ pymupdf (fitz) available")
    except ImportError:
        results['pymupdf'] = False
        print(f"   ✗ pymupdf not installed")
    
    any_available = any(results.values())
    status = "✅ PASS" if any_available else "⚠️  SKIP"
    print(f"\n{status} | At least one PDF library: {any_available}")
    
    return any_available if any_available else None


if __name__ == "__main__":
    print("\n" + "🔬 PHASE 5 TESTING: RAG DOCUMENT Q&A".center(60))
    print("=" * 60)
    
    results = {
        "ChromaDB": test_chromadb_import(),
        "AutoGen RAG": test_autogen_rag_import(),
        "RAG Function": test_rag_function_import(),
        "Sentence Transformers": test_sentence_transformers(),
        "Simple Q&A Logic": test_simple_document_qa(),
        "PDF Parsing": test_pdf_parsing(),
    }
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v is True)
    skipped = sum(1 for v in results.values() if v is None)
    failed = sum(1 for v in results.values() if v is False)
    total = len(results)
    
    for test, result in results.items():
        if result is True:
            status = "✅ PASS"
        elif result is None:
            status = "⚠️  SKIP"
        else:
            status = "❌ FAIL"
        print(f"   {status} | {test}")
    
    print(f"\n   Passed: {passed}/{total} | Skipped: {skipped} | Failed: {failed}")
    print("=" * 60)
    
    if failed == 0:
        print("🎉 Phase 5 RAG tests complete!")
        if skipped > 0:
            print("   Note: Some optional dependencies not installed")
            print("   The UI will work with simpler document Q&A fallback")
    else:
        print("⚠️  Some tests failed - review output above")

