from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        # TODO: store references to store and llm_fn
        # Save the vector store so the agent can retrieve relevant knowledge later.
        self.store = store
        # Save the language model function used to turn the prompt into an answer.
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        # TODO: retrieve chunks, build prompt, call llm_fn
        # Retrieve the most relevant pieces of context for the user's question.
        results = self.store.search(question, top_k=top_k)

        # Convert the retrieved search results into a readable context block.
        # Numbering the chunks makes the prompt easier to inspect and debug.
        if results:
            context_parts = []
            for index, item in enumerate(results, start=1):
                context_parts.append(f"[{index}] {item['content']}")
            context = "\n\n".join(context_parts)
        else:
            # If nothing is retrieved, keep the context explicit instead of failing.
            context = "No relevant context was found in the knowledge base."

        # Build a grounded RAG prompt: instruction + retrieved evidence + question.
        # This encourages the LLM to answer from the retrieved material.
        prompt = (
            "You are a helpful assistant answering questions from a knowledge base.\n"
            "Use the provided context to answer the question as accurately as possible.\n"
            "If the context is limited, say so clearly.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {question}\n\n"
            "Answer:"
        )

        # Call the injected LLM function and return its final text response.
        return self.llm_fn(prompt)
