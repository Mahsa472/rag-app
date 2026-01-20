from retrieval import retrieve_relevant_chunks
from llm_openai import call_llm
from telemetry import retrieval_latency, retrieval_chunks, llm_latency
import time

def build_prompt(question: str, contexts):
    ctx="\n\n---\n\n".join(contexts) if contexts else "No relevant context provided"
    return(
        "You are an assistant to answer question. Use only contexts and if the answer is not there say I don't know.\n\n"
        f"Context:\n{ctx}\n\n"
        f"Question:\n{question}\n\n"
        "Answer:"
    )


def answer_question(question:str, top_answers:int = 3):
    # Track retrieval latency and chunk count
    retrieval_start = time.time()

    chunks = retrieve_relevant_chunks(question, top_k=top_answers)
    retrieval_latency.record(time.time() - retrieval_start)
    retrieval_chunks.record(len(chunks))

    answers = []

    for chunk in chunks[:top_answers]:
        prompt = build_prompt(question, [chunk["text"]])

        llm_start = time.time()
        answer_text = call_llm(prompt)
        llm_latency.record(time.time() - llm_start)
        
        meta = chunk.get("metadata", {})
        answers.append(
            {
                "answer": answer_text,
                "id": chunk.get("id"),
                "source": meta.get("source"),
                "distance": chunk.get("distance"),
            }
        )

    return answers