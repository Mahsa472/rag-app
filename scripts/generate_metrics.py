#!/usr/bin/env python3
"""
Generate metrics for DVC pipeline
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from embeddings_store import get_collection

def main():
    """Generate metrics from ChromaDB"""
    try:
        collection = get_collection(name="documents")
        count = collection.count()
        
        metrics = {
            "document_count": count,
            "indexed": count > 0
        }
        
        with open("metrics.json", "w") as f:
            json.dump(metrics, f, indent=2)
        
        print(f"Generated metrics: {count} documents indexed")
        return 0
    except Exception as e:
        print(f"Error generating metrics: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

