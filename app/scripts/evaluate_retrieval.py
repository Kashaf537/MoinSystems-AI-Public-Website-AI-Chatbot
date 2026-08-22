"""
Day 3 - Basic RAG retrieval evaluation.

Tests:
- Service questions
- Company questions
- Pricing questions
- Unknown questions
"""

from app.db.session import SessionLocal
from app.retrieval.retriever import RAGRetriever


TEST_QUERIES = [
    {
        "name": "Service",
        "query": "What services does MoinSystems AI provide?",
    },
    {
        "name": "Web Development",
        "query": "Does MoinSystems AI build websites?",
    },
    {
        "name": "Mobile Development",
        "query": "Can MoinSystems AI develop mobile applications?",
    },
    {
        "name": "Company",
        "query": "What is MoinSystems AI?",
    },
    {
        "name": "Pricing",
        "query": "How much does your software development service cost?",
    },
    {
        "name": "Unknown",
        "query": "Who won the football World Cup in 1950?",
    },
]


def main() -> None:

    print("=" * 70)
    print("MoinSystems AI - Day 3 Retrieval Evaluation")
    print("=" * 70)

    db = SessionLocal()

    try:

        retriever = RAGRetriever(db)

        for test in TEST_QUERIES:

            print("\n")
            print("=" * 70)
            print(test["name"])
            print("=" * 70)

            print(
                f"Query: {test['query']}"
            )

            results = retriever.retrieve(
                test["query"]
            )

            if not results:

                print(
                    "\nNO RELEVANT CONTEXT FOUND"
                )

                continue

            print(
                f"\nRetrieved {len(results)} results:"
            )

            for rank, result in enumerate(
                results,
                start=1,
            ):

                print(
                    f"{rank}. "
                    f"{result.record_id} | "
                    f"{result.similarity:.4f} | "
                    f"{result.title}"
                )

    finally:
        db.close()


if __name__ == "__main__":
    main()