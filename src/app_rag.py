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
        <textarea id="question" placeholder="Enter your question here"></textarea>
        <button onclick="ask()">Ask</button>
        <div id="status"></div>
        <div id="answers"></div>
    </main>
    <script>
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

    docs = list(iter_documents())
    index_documents(docs, reset=True)
    return jsonify({"indexed": len(docs)})

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json(silent=True) or {}
    if "question" not in data:
        return jsonify({"error": "Missing 'question'"}), 400

    answers = answer_question(data["question"])

    return jsonify({"answers": answers})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
