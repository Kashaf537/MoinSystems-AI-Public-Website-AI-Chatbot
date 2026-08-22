"""
Day 3 - Deterministic RAG context builder.

Converts retrieved knowledge records into a predictable
context format for downstream LLM prompting.
"""

from app.retrieval.retriever import RetrievedDocument


def build_context(
    documents: list[RetrievedDocument],
) -> str:
    """
    Build deterministic context from retrieved documents.

    Includes only safe knowledge-base fields.
    """

    if not documents:
        return ""

    blocks: list[str] = []
    seen_content: set[str] = set()

    for index, document in enumerate(
        documents,
        start=1,
    ):

        normalized_content = (
            " ".join(
                document.content.lower().split()
            )
        )

        # Prevent identical context blocks.
        if normalized_content in seen_content:
            continue

        seen_content.add(normalized_content)

        block = (
            f"[Knowledge {index}]\n"
            f"Record ID: {document.record_id}\n"
            f"Title: {document.title}\n"
            f"Category: {document.category}\n"
            f"Content: {document.content}\n"
            f"Dataset Version: {document.dataset_version}\n"
        )

        blocks.append(block)

    return "\n".join(blocks)