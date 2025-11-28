from math import dist
from typing import List, Dict
from config import TOP_K
from embeddings_store import get_collection, embed_texts


def retrieve_relevant_chunks(query: str, top_k: int = TOP_K, name: str = "documents") -> List[Dict]:
    collection = get_collection(name="documents")
    query_emb = embed_texts([query])[0]

    res = collection.query(
        query_embeddings=[query_emb],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    results=[]
    for doc, meta, dist in zip(
        res["documents"][0], res["metadatas"][0], res["distances"][0]
    ):
        results.append(
            {
                "text": doc,
                "metadata": meta,
                "distance": dist,
            }
        )
    return results
