
"""
Day 2 - pgvector similarity search verification.

Tests:
1. Local embedding generation.
2. Embedding dimension = 384.
3. PostgreSQL connection.
4. pgvector cosine similarity.
5. Retrieval of the most relevant knowledge chunks.
"""

from sqlalchemy import text

from app.db.session import SessionLocal
from app.embeddings.local_embeddings import LocalEmbeddingProvider


# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

QUERY = "What software development services does MoinSystems AI provide?"

EXPECTED_DIMENSION = 384

TOP_K = 5


# ------------------------------------------------------------
# Main test
# ------------------------------------------------------------

def main() -> None:

    print("=" * 70)
    print("MoinSystems AI - Day 2 Vector Search Verification")
    print("=" * 70)

    # --------------------------------------------------------
    # 1. Generate query embedding
    # --------------------------------------------------------

    print("\nQuery:")
    print(QUERY)

    print("\nLoading embedding model...")

    embedding_provider = LocalEmbeddingProvider()

    query_embedding = embedding_provider.embed(QUERY)

    print(
        f"Embedding model: "
        f"{embedding_provider.model_name}"
    )

    print(
        f"Embedding dimension: "
        f"{len(query_embedding)}"
    )

    # --------------------------------------------------------
    # 2. Verify embedding dimension
    # --------------------------------------------------------

    if len(query_embedding) != EXPECTED_DIMENSION:
        raise ValueError(
            "Embedding dimension mismatch: "
            f"expected {EXPECTED_DIMENSION}, "
            f"got {len(query_embedding)}"
        )

    print("Embedding dimension check: PASSED")

    # --------------------------------------------------------
    # 3. Connect to PostgreSQL
    # --------------------------------------------------------

    db = SessionLocal()

    try:

        # ----------------------------------------------------
        # 4. Check indexed records
        # ----------------------------------------------------

        counts = db.execute(
            text(
                """
                SELECT
                    COUNT(*) AS total_chunks,
                    COUNT(embedding) AS embedded_chunks
                FROM knowledge_chunk
                """
            )
        ).mappings().one()

        print(
            f"\nTotal chunks: "
            f"{counts['total_chunks']}"
        )

        print(
            f"Embedded chunks: "
            f"{counts['embedded_chunks']}"
        )

        if counts["total_chunks"] == 0:
            raise RuntimeError(
                "No knowledge chunks found."
            )

        if counts["embedded_chunks"] == 0:
            raise RuntimeError(
                "No embeddings found."
            )

        if (
            counts["total_chunks"]
            != counts["embedded_chunks"]
        ):
            raise RuntimeError(
                "Some knowledge chunks are missing embeddings."
            )

        print("Embedding completeness check: PASSED")

        # ----------------------------------------------------
        # 5. Convert Python list to pgvector literal
        # ----------------------------------------------------

        vector_literal = (
            "["
            + ",".join(
                str(float(value))
                for value in query_embedding
            )
            + "]"
        )

        # ----------------------------------------------------
        # 6. Run cosine similarity search
        # ----------------------------------------------------

        results = db.execute(
            text(
                """
                SELECT
                    kc.id,
                    kd.external_id,
                    kd.title,
                    kd.category,
                    kd.dataset_version,
                    kc.text,
                    1 - (
                        kc.embedding
                        <=> CAST(:query_embedding AS vector)
                    ) AS similarity
                FROM knowledge_chunk AS kc
                JOIN knowledge_document AS kd
                    ON kd.id = kc.document_id
                WHERE kc.embedding IS NOT NULL
                ORDER BY
                    kc.embedding
                    <=> CAST(:query_embedding AS vector)
                LIMIT :top_k
                """
            ),
            {
                "query_embedding": vector_literal,
                "top_k": TOP_K,
            },
        ).mappings().all()

        # ----------------------------------------------------
        # 7. Validate results
        # ----------------------------------------------------

        if not results:
            raise RuntimeError(
                "Vector similarity search returned no results."
            )

        print(
            "\nVector similarity search: PASSED"
        )

        # ----------------------------------------------------
        # 8. Display results
        # ----------------------------------------------------

        print("\n" + "=" * 70)
        print(f"TOP {len(results)} RESULTS")
        print("=" * 70)

        for rank, result in enumerate(
            results,
            start=1,
        ):

            print(
                f"\n#{rank}"
            )

            print(
                f"Record ID : "
                f"{result['external_id']}"
            )

            print(
                f"Title     : "
                f"{result['title']}"
            )

            print(
                f"Category  : "
                f"{result['category']}"
            )

            print(
                f"Version   : "
                f"{result['dataset_version']}"
            )

            print(
                f"Similarity: "
                f"{float(result['similarity']):.4f}"
            )

            print(
                f"Text      : "
                f"{result['text'][:300]}"
            )

        # ----------------------------------------------------
        # 9. Final status
        # ----------------------------------------------------

        print("\n" + "=" * 70)
        print("VECTOR SEARCH VERIFICATION PASSED")
        print("=" * 70)

        print(
            "\nDay 2 verification:"
        )

        print(
            "✓ JSONL dataset loaded"
        )

        print(
            "✓ 384-dimensional embeddings generated"
        )

        print(
            "✓ PostgreSQL connection successful"
        )

        print(
            "✓ pgvector similarity search successful"
        )

        print(
            "✓ Indexed chunks retrieved successfully"
        )

    finally:

        db.close()


if __name__ == "__main__":

    try:
        main()

    except Exception as exc:

        print(
            f"\nERROR: {exc}"
        )

        raise

