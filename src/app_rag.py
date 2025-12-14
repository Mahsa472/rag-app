import os
from flask import Flask, request, jsonify
from ingestion import iter_documents
from embeddings_store import index_documents
from rag_pipeline import answer_question


app = Flask(__name__)

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <title>RAG Demo</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        main { max-width: 720px; margin: auto; background: #fff; padding: 24px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }
        textarea { width: 100%; height: 120px; padding: 12px; font-size: 1rem; border-radius: 8px; border: 1px solid #ccc; resize: vertical; }
        button { margin-top: 12px; padding: 10px 24px; font-size: 1rem; border: none; border-radius: 8px; cursor: pointer; background: #0078d4; color: #fff; }
        .answer-block { margin-top: 24px; padding: 16px; border-radius: 8px; background: #fafafa; border: 1px solid #e0e0e0; }
        .answer-block p { white-space: pre-wrap; }
    </style>
</head>
<body>
    <main>
        <h1>Ask Your Documents</h1>
        <p>Type a question below. We will search your indexed PDFs and answer using the retrieved context.</p>
        <div id="index-status" style="margin-bottom: 12px; padding: 8px; background: #f0f0f0; border-radius: 4px; font-size: 0.9rem;">
            <span id="index-info">Checking index status...</span>
            <button onclick="buildIndex()" id="build-btn" style="margin-left: 12px; padding: 6px 12px; font-size: 0.85rem; display: none;">Build Index</button>
        </div>
        <textarea id="question" placeholder="Enter your question here"></textarea>
        <button onclick="ask()">Ask</button>
        <div id="status"></div>
        <div id="answers"></div>
    </main>
    <script>
        async function checkIndex() {
            const indexInfo = document.getElementById("index-info");
            const buildBtn = document.getElementById("build-btn");
            try {
                const res = await fetch("/check-index");
                const data = await res.json();
                if (data.indexed) {
                    indexInfo.textContent = `Index ready: ${data.document_count} documents indexed`;
                    indexInfo.style.color = "#28a745";
                    buildBtn.style.display = "none";
                } else {
                    indexInfo.textContent = "Index is empty. Click 'Build Index' to index your PDFs.";
                    indexInfo.style.color = "#dc3545";
                    buildBtn.style.display = "inline-block";
                }
            } catch (err) {
                indexInfo.textContent = "Error checking index status";
                indexInfo.style.color = "#dc3545";
            }
        }

        async function buildIndex() {
            const indexInfo = document.getElementById("index-info");
            const buildBtn = document.getElementById("build-btn");
            indexInfo.textContent = "Building index... This may take a moment.";
            buildBtn.disabled = true;
            try {
                const res = await fetch("/build-index", { method: "POST" });
                const data = await res.json();
                if (res.ok) {
                    indexInfo.textContent = `Index built successfully: ${data.indexed} documents indexed`;
                    indexInfo.style.color = "#28a745";
                    buildBtn.style.display = "none";
                } else {
                    indexInfo.textContent = `Error: ${data.error || "Failed to build index"}`;
                    indexInfo.style.color = "#dc3545";
                    buildBtn.disabled = false;
                }
            } catch (err) {
                indexInfo.textContent = `Error: ${err.message}`;
                indexInfo.style.color = "#dc3545";
                buildBtn.disabled = false;
            }
        }

        async function ask() {
            const questionEl = document.getElementById("question");
            const statusEl = document.getElementById("status");
            const answersEl = document.getElementById("answers");
            const question = questionEl.value.trim();
            statusEl.textContent = "";
            answersEl.innerHTML = "";
            if (!question) {
                statusEl.textContent = "Please enter a question.";
                return;
            }
            statusEl.textContent = "Thinking...";
            try {
                const res = await fetch("/ask", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ question })
                });
                const data = await res.json();
                if (!res.ok) {
                    throw new Error(data.error || "Request failed");
                }
                const answers = data.answers || [];
                if (!answers.length) {
                    answersEl.innerHTML = "<p>No relevant answers found.</p>";
                } else {
                    answersEl.innerHTML = answers
                        .map((item, idx) => `
                            <section class="answer-block">
                                <h2>Answer ${idx + 1}</h2>
                                <p>${item.answer || "No answer generated."}</p>
                                <h3>Source</h3>
                                <ul>
                                    <li>${item.source || "Unknown source"}${item.id ? ` (chunk ${item.id})` : ""}</li>
                                </ul>
                            </section>
                        `)
                        .join("");
                }
                statusEl.textContent = "";
            } catch (err) {
                statusEl.textContent = err.message;
            }
        }

        // Check index status on page load
        checkIndex();
    </script>
</body>
</html>
"""


@app.route("/", methods=["GET"])
def home():
    return HTML_PAGE


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "RAG API running"})

@app.route("/check-index", methods=["GET"])
def check_index():
    """Check if ChromaDB has documents indexed"""
    from embeddings_store import get_collection
    try:
        collection = get_collection(name="documents")
        count = collection.count()
        return jsonify({
            "status": "success",
            "document_count": count,
            "indexed": count > 0
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "indexed": False
        }), 500

@app.route("/build-index", methods=["POST"])
def build_index():
    try:
        docs = list(iter_documents())
        if not docs:
            return jsonify({
                "error": "No documents found",
                "data_dir": os.getenv("DATA_DIR", "data/pdfs"),
                "indexed": 0
            }), 400
        
        index_documents(docs, reset=True)
        return jsonify({
            "status": "success",
            "indexed": len(docs),
            "message": f"Successfully indexed {len(docs)} document chunks"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "indexed": 0
        }), 500

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json(silent=True) or {}
    if "question" not in data:
        return jsonify({"error": "Missing 'question'"}), 400

    answers = answer_question(data["question"])

    return jsonify({"answers": answers})


def ensure_index_exists():
    """Check if index exists, and build it automatically if empty"""
    try:
        from embeddings_store import get_collection
        collection = get_collection(name="documents")
        count = collection.count()
        
        if count == 0:
            print("Index is empty. Building index automatically...")
            docs = list(iter_documents())
            if docs:
                index_documents(docs, reset=True)
                print(f"Successfully auto-indexed {len(docs)} document chunks")
            else:
                print("Warning: No documents found to index. Make sure PDFs are in the data/pdfs directory.")
        else:
            print(f"Index already exists with {count} document chunks")
    except Exception as e:
        print(f"Warning: Could not check/build index on startup: {e}")


if __name__ == "__main__":
    # Automatically build index on startup if it's empty
    ensure_index_exists()
    app.run(host="0.0.0.0", port=8000)
