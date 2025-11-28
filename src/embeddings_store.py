import chromadb
from sentence_transformers import SentenceTransformer
from config import CHROMA_DIR, EMBEDDING_MODEL

_model = None

def load_embedding_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL, device="cpu")

    return _model

def embed_texts(texts):
    model = load_embedding_model()
    return model.encode(texts, batch_size=32, show_progress_bar=True).tolist()

def get_collection(name="documents"):
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    return client.get_or_create_collection(name)


def clear_collection(name="documents"):
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    try:
        client.delete_collection(name)
    except chromadb.errors.NotFoundError:
        return


def index_documents(docs, batch_size=16, reset=False):
    if reset:
        clear_collection()
    collection = get_collection()

    for i in range(0, len(docs), batch_size):
        batch = docs[i:i+batch_size]
        ids = [doc["id"] for doc in batch]
        texts = [doc["text"] for doc in batch]
        metas = [doc["metadata"] for doc in batch]

        emb = embed_texts(texts)

        collection.add(
            ids=ids,
            documents=texts,
            metadatas=metas,
            embeddings=emb,
        )

if __name__ == "__main__":
    from ingestion import iter_documents
    docs=[]
    for doc in iter_documents():
        docs.append(doc)
    index_documents(docs, reset=True)
    print("Indexed documents")
