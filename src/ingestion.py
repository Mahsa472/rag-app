import os
from config import DATA_DIR, CHUNK_SIZE, CHUNK_OVERLAP
from PyPDF2 import PdfReader

def _read_pdf(file_path):
    reader = PdfReader(file_path)
    return "\n".join([page.extract_text() or "" for page in reader.pages])

def _chunk(text, source):
    start = 0
    L = len(text)

    while start < L:
        end = min(start + CHUNK_SIZE, L)
        chunk = text[start:end]

        if chunk.strip():
            yield {
                "id": f"{source}-{start}",
                "text": chunk,
                "metadata": {"source": source}
            }

        next_start = end - CHUNK_OVERLAP
        if next_start <= start:
            next_start = end
        start = next_start

def iter_documents():
    for root, _, files in os.walk(DATA_DIR):
        for file in files:
            if not file.lower().endswith(".pdf"):
                continue

            file_path = os.path.join(root, file)
            text = _read_pdf(file_path)
            rel = os.path.relpath(file_path, DATA_DIR)

            for chunk in _chunk(text, rel):
                yield chunk



if __name__ == "__main__":
    for i, doc in enumerate(iter_documents()):
        print(doc["id"], len(doc["text"]))
        if i > 10:
            break