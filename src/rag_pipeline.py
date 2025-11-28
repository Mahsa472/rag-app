from retrieval import retrieve_relevant_chunks
from llm_openai import call_llm

def build_prompt(question: str, contexts):
    ctx="\n\n---\n\n".join(contexts) if contexts else "No relevant context provided"
    return(
        "You are an assistant to answer question. Use only contexts and if the answer is not there say I don't know.\n\n"
        f"Context:\n{ctx}\n\n"
        f"Question:\n{question}\n\n"
        "Answer:"
    )


def answer_question(question:str, top_answers:int = 3):
    chunks = retrieve_relevant_chunks(question, top_k=top_answers)
    answers = []

    for chunk in chunks[:top_answers]:
        prompt = build_prompt(question, [chunk["text"]])
        answer_text = call_llm(prompt)
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