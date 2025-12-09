#!/usr/bin/env python3
"""
DVC pipeline script for indexing PDF documents
This script resets ChromaDB and reindexes all PDFs to ensure no duplicates
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ingestion import iter_documents
from embeddings_store import index_documents

def main():
    """Main indexing function for DVC pipeline - resets ChromaDB to avoid duplicates"""
    print("=" * 60)
    print("DVC Pipeline: Document Indexing")
    print("=" * 60)
    
    # Get directories from environment or use defaults
    data_dir = os.getenv("DATA_DIR", "data/pdfs")
    chroma_dir = os.getenv("CHROMA_DIR", "data/chroma_db")
    
    print(f"Reading PDFs from: {data_dir}")
    print(f"Storing index in: {chroma_dir}")
    print()
    
    # Collect all documents from all PDFs
    print("Extracting text from PDFs...")
    docs = []
    doc_count = 0
    pdf_count = 0
    
    for doc in iter_documents():
        docs.append(doc)
        doc_count += 1
        if doc_count % 100 == 0:
            print(f"  Processed {doc_count} chunks...")
    
    # Count unique PDFs
    unique_sources = set()
    for doc in docs:
        source = doc.get("metadata", {}).get("source", "")
        if source:
            unique_sources.add(source)
    pdf_count = len(unique_sources)
    
    print(f"\nExtraction complete:")
    print(f"  - PDFs processed: {pdf_count}")
    print(f"  - Total chunks: {len(docs)}")
    
    if len(docs) == 0:
        print("\n[WARNING] No documents found to index!")
        print(f"   Check that PDFs exist in: {data_dir}")
        return 1
    
    # Reset ChromaDB and index all documents (ensures no duplicates)
    print("\n" + "=" * 60)
    print("Indexing documents (resetting ChromaDB to avoid duplicates)...")
    print("=" * 60)
    
    try:
        index_documents(docs, reset=True)  # reset=True ensures clean ChromaDB
        print(f"\n[SUCCESS] Successfully indexed {len(docs)} chunks from {pdf_count} PDF(s)")
        print(f"   ChromaDB location: {chroma_dir}")
        return 0
    except Exception as e:
        print(f"\n[ERROR] Error during indexing: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

