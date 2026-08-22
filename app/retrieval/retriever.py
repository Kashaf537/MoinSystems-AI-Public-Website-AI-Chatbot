"""
Day 3 - RAG retrieval service.

Responsibilities:
- Query normalization
- Query embedding
- pgvector similarity search
- Configurable top-k
- Configurable relevance threshold
- Metadata filtering
- Lexical ranking
- Query-type detection
- Canonical knowledge prioritization
- Duplicate control
- Retrieval tracing/debugging
"""

from dataclasses import dataclass
import re
from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.embeddings.local_embeddings import LocalEmbeddingProvider


@dataclass
class RetrievedDocument:
    record_id: str
    title: str
    category: str
    tags: str | None
    intents: str | None
    content: str
    dataset_version: str
    metadata: dict
    similarity: float
    retrieval_score: float = 0.0


class RAGRetriever:
    """Dedicated retrieval service for the RAG knowledge base."""

    def __init__(
        self,
        db: Session,
        embedding_provider: LocalEmbeddingProvider | None = None,
    ):
        self.db = db
        self.settings = get_settings()

        self.embedding_provider = (
            embedding_provider
            or LocalEmbeddingProvider()
        )

    # =========================================================
    # Query preparation
    # =========================================================

    @staticmethod
    def normalize_query(query: str) -> str:
        """Normalize whitespace while preserving meaning."""

        if not query:
            return ""

        return re.sub(r"\s+", " ", query).strip()

    @staticmethod
    def tokenize(value: str) -> set[str]:
        """Extract normalized alphanumeric tokens."""

        if not value:
            return set()

        return {
            token.lower()
            for token in re.findall(r"[a-zA-Z0-9]+", value)
            if len(token) > 2
        }

    # =========================================================
    # Query type detection
    # =========================================================

    @staticmethod
    def detect_query_type(query: str) -> str | None:
        """
        Detect the broad intent of the query.

        This is deterministic and conservative.
        """

        q = query.lower()

        # -----------------------------------------------------
        # Pricing
        # -----------------------------------------------------

        pricing_terms = [
            "price",
            "pricing",
            "cost",
            "costs",
            "budget",
            "charge",
            "charges",
            "fee",
            "fees",
            "how much",
            "quote",
            "quotation",
        ]

        if any(term in q for term in pricing_terms):
            return "pricing"

        # -----------------------------------------------------
        # Company
        # -----------------------------------------------------

        company_terms = [
            "what is moin",
            "what is moinsystems",
            "who is moin",
            "who are moinsystems",
            "about moinsystems",
            "about moin",
            "company overview",
            "tell me about moinsystems",
        ]

        if any(term in q for term in company_terms):
            return "company"

        # -----------------------------------------------------
        # Web
        # -----------------------------------------------------

        web_terms = [
            "website",
            "web development",
            "web application",
            "web app",
            "landing page",
            "wordpress",
            "ecommerce website",
            "e-commerce website",
        ]

        if any(term in q for term in web_terms):
            return "web"

        # -----------------------------------------------------
        # Mobile
        # -----------------------------------------------------

        mobile_terms = [
            "mobile app",
            "mobile application",
            "android",
            "ios",
            "iphone",
            "ipad",
        ]

        if any(term in q for term in mobile_terms):
            return "mobile"

        # -----------------------------------------------------
        # AI
        # -----------------------------------------------------

        ai_terms = [
            "artificial intelligence",
            "ai development",
            "ai agent",
            "ai agents",
            "chatbot",
            "voice ai",
            "generative ai",
        ]

        if any(term in q for term in ai_terms):
            return "ai"

        # -----------------------------------------------------
        # General services
        # -----------------------------------------------------

        service_terms = [
            "services",
            "service",
            "what do you provide",
            "what can you build",
            "what do you offer",
            "capabilities",
        ]

        if any(term in q for term in service_terms):
            return "service"

        return None

    # =========================================================
    # Lexical relevance
    # =========================================================

    def calculate_lexical_overlap(
        self,
        query: str,
        result: RetrievedDocument,
    ) -> float:
        """
        Calculate lexical overlap between the query and result.

        Title, tags, intents and content are considered.
        """

        query_tokens = self.tokenize(query)

        if not query_tokens:
            return 0.0

        searchable_text = " ".join(
            [
                result.title or "",
                result.tags or "",
                result.intents or "",
                result.content or "",
            ]
        )

        result_tokens = self.tokenize(searchable_text)

        if not result_tokens:
            return 0.0

        overlap = query_tokens.intersection(result_tokens)

        return len(overlap) / len(query_tokens)

    # =========================================================
    # Metadata boost
    # =========================================================

    def calculate_metadata_boost(
        self,
        query: str,
        result: RetrievedDocument,
    ) -> float:
        """
        Return a normalized metadata relevance signal.

        The value is intentionally kept between 0 and 1.
        """

        query_type = self.detect_query_type(query)

        if not query_type:
            return 0.0

        category = (result.category or "").lower()
        title = (result.title or "").lower()
        intents = (result.intents or "").lower()
        tags = (result.tags or "").lower()

        searchable = " ".join(
            [
                category,
                title,
                intents,
                tags,
            ]
        )

        # -----------------------------------------------------
        # Pricing
        # -----------------------------------------------------

        if query_type == "pricing":
            if (
                "pricing" in category
                or "pricing" in title
                or "pricing" in intents
                or "pricing" in tags
                or "price" in searchable
                or "quote" in searchable
            ):
                return 1.0

        # -----------------------------------------------------
        # Company
        # -----------------------------------------------------

        if query_type == "company":
            if (
                category == "company"
                or "company overview" in title
                or "company" in intents
                or "company" in tags
            ):
                return 1.0

        # -----------------------------------------------------
        # Web
        # -----------------------------------------------------

        if query_type == "web":
            if (
                "web" in title
                or "web" in intents
                or "web" in tags
                or "website" in searchable
            ):
                return 1.0

        # -----------------------------------------------------
        # Mobile
        # -----------------------------------------------------

        if query_type == "mobile":
            if (
                "mobile" in title
                or "mobile" in intents
                or "mobile" in tags
            ):
                return 1.0

        # -----------------------------------------------------
        # AI
        # -----------------------------------------------------

        if query_type == "ai":
            if (
                "ai" in title
                or "ai" in intents
                or "ai" in tags
                or "artificial intelligence" in searchable
            ):
                return 1.0

        # -----------------------------------------------------
        # General service
        # -----------------------------------------------------

        if query_type == "service":
            if (
                category == "service"
                or "service" in intents
                or "service" in tags
            ):
                return 1.0

        return 0.0

    # =========================================================
    # Canonical knowledge priority
    # =========================================================

    @staticmethod
    def calculate_record_priority(
        query: str,
        result: RetrievedDocument,
    ) -> float:
        """
        Return a normalized canonical-record priority.

        Range:
            -1.0 to +1.0

        This is converted into a small ranking contribution later.
        """

        query_type = RAGRetriever.detect_query_type(query)

        record_id = (
            result.record_id or ""
        ).lower()

        title = (
            result.title or ""
        ).lower()

        # -----------------------------------------------------
        # Company
        # -----------------------------------------------------

        if query_type == "company":

            if record_id == "company_001":
                return 1.0

            if (
                record_id.startswith("company_")
                and "overview" in title
            ):
                return 0.75

            if record_id.startswith("company_"):
                return 0.50

            if record_id.startswith("phase2_public_positioning"):
                return 0.30

            if record_id.startswith("conversation_"):
                return -0.50

        # -----------------------------------------------------
        # General services
        # -----------------------------------------------------

        if query_type == "service":

            if record_id.startswith("service_detail_"):
                return 0.80

            if record_id.startswith("service_"):
                return 0.60

            if record_id.startswith("phase2_public_positioning"):
                return 0.50

            if record_id.startswith("intent_"):
                return -0.40

            if record_id.startswith("conversation_"):
                return -0.60

        # -----------------------------------------------------
        # Web
        # -----------------------------------------------------

        if query_type == "web":

            if (
                record_id.startswith("service_detail_")
                and "web" in title
            ):
                return 1.0

            if record_id.startswith("service_"):
                return 0.40

            if record_id.startswith("conversation_"):
                return -0.50

        # -----------------------------------------------------
        # Mobile
        # -----------------------------------------------------

        if query_type == "mobile":

            if (
                record_id.startswith("service_detail_")
                and "mobile" in title
            ):
                return 1.0

            if record_id.startswith("service_"):
                return 0.40

            if record_id.startswith("conversation_"):
                return -0.50

        # -----------------------------------------------------
        # AI
        # -----------------------------------------------------

        if query_type == "ai":

            if (
                record_id.startswith("service_detail_")
                and (
                    "ai" in title
                    or "artificial intelligence" in title
                )
            ):
                return 1.0

            if record_id.startswith("service_"):
                return 0.40

            if record_id.startswith("conversation_"):
                return -0.50

        # -----------------------------------------------------
        # Pricing
        # -----------------------------------------------------

        if query_type == "pricing":

            if record_id.startswith("pricing_"):
                return 1.0

            if record_id.startswith("phase2_pricing_"):
                return 0.90

            if record_id.startswith("intent_"):
                return -0.30

            if record_id.startswith("process_"):
                return -0.50

            if record_id.startswith("conversation_"):
                return -0.50

        # -----------------------------------------------------
        # Generic conversation penalty
        # -----------------------------------------------------

        if record_id.startswith("conversation_"):
            return -0.25

        return 0.0

    # =========================================================
    # Combined ranking score
    # =========================================================

    def calculate_retrieval_score(
        self,
        query: str,
        result: RetrievedDocument,
    ) -> float:
        """
        Calculate a bounded retrieval score.

        Weighted signals:

        Semantic similarity : 70%
        Lexical overlap     : 10%
        Metadata relevance  : 10%
        Record priority     : 10%

        Final score is always constrained to [0, 1].
        """

        semantic_score = max(
            0.0,
            min(1.0, float(result.similarity)),
        )

        lexical_score = max(
            0.0,
            min(
                1.0,
                self.calculate_lexical_overlap(
                    query,
                    result,
                ),
            ),
        )

        metadata_score = max(
            0.0,
            min(
                1.0,
                self.calculate_metadata_boost(
                    query,
                    result,
                ),
            ),
        )

        record_priority = max(
            -1.0,
            min(
                1.0,
                self.calculate_record_priority(
                    query,
                    result,
                ),
            ),
        )

        # Convert priority from [-1, 1] to [0, 1].
        priority_score = (
            record_priority + 1.0
        ) / 2.0

        score = (
            semantic_score * 0.70
            + lexical_score * 0.10
            + metadata_score * 0.10
            + priority_score * 0.10
        )

        return max(
            0.0,
            min(1.0, score),
        )

    # =========================================================
    # Vector retrieval
    # =========================================================

    def retrieve(
        self,
        query: str,
        category: Optional[str] = None,
        intent: Optional[str] = None,
        top_k: Optional[int] = None,
        threshold: Optional[float] = None,
    ) -> list[RetrievedDocument]:

        query = self.normalize_query(query)

        if not query:
            return []

        top_k = (
            top_k
            if top_k is not None
            else self.settings.RAG_TOP_K
        )

        threshold = (
            threshold
            if threshold is not None
            else self.settings.RAG_SCORE_THRESHOLD
        )

        # Safety validation.
        top_k = max(1, int(top_k))
        threshold = max(
            0.0,
            min(1.0, float(threshold)),
        )

        # -----------------------------------------------------
        # Query embedding
        # -----------------------------------------------------

        query_embedding = self.embedding_provider.embed(query)

        if not query_embedding:
            return []

        expected_dimension = (
            self.embedding_provider.dimension
        )

        if len(query_embedding) != expected_dimension:
            raise ValueError(
                "Query embedding dimension mismatch: "
                f"expected {expected_dimension}, "
                f"got {len(query_embedding)}"
            )

        # -----------------------------------------------------
        # Convert embedding to pgvector literal
        # -----------------------------------------------------

        vector_literal = (
            "["
            + ",".join(
                str(float(value))
                for value in query_embedding
            )
            + "]"
        )

        # -----------------------------------------------------
        # Metadata filters
        # -----------------------------------------------------

        filters = [
            "kc.embedding IS NOT NULL"
        ]

        parameters = {
            "query_embedding": vector_literal,

            # Candidate pool is intentionally larger than final
            # top-k so deterministic ranking can improve results.
            "candidate_limit": max(
                top_k * 3,
                15,
            ),
        }

        if category:

            filters.append(
                "LOWER(kd.category) = LOWER(:category)"
            )

            parameters["category"] = (
                category.strip()
            )

        if intent:

            filters.append(
                "LOWER(kd.intents) "
                "LIKE LOWER(:intent_pattern)"
            )

            parameters["intent_pattern"] = (
                f"%{intent.strip()}%"
            )

        where_clause = " AND ".join(filters)

        # =====================================================
        # pgvector similarity search
        # =====================================================

        query_sql = text(
            f"""
            SELECT
                kd.external_id AS record_id,
                kd.title,
                kd.category,
                kd.tags,
                kd.intents,
                kd.content,
                kd.dataset_version,
                kd.metadata_json AS metadata,

                1 - (
                    kc.embedding
                    <=> CAST(
                        :query_embedding AS vector
                    )
                ) AS similarity

            FROM knowledge_chunk AS kc

            JOIN knowledge_document AS kd
                ON kd.id = kc.document_id

            WHERE {where_clause}

            ORDER BY
                kc.embedding
                <=> CAST(
                    :query_embedding AS vector
                )

            LIMIT :candidate_limit
            """
        )

        rows = (
            self.db.execute(
                query_sql,
                parameters,
            )
            .mappings()
            .all()
        )

        # =====================================================
        # Candidate construction
        # =====================================================

        candidates: list[RetrievedDocument] = []

        # Use a conservative semantic floor so ranking boosts
        # can never turn clearly unrelated records into relevant
        # context.
        semantic_floor = min(
            threshold,
            0.30,
        )

        for row in rows:

            similarity = float(
                row["similarity"]
            )

            # -------------------------------------------------
            # Semantic safety gate
            # -------------------------------------------------

            if similarity < semantic_floor:
                continue

            document = RetrievedDocument(
                record_id=str(row["record_id"]),
                title=row["title"],
                category=row["category"],
                tags=row["tags"],
                intents=row["intents"],
                content=row["content"],
                dataset_version=row["dataset_version"],
                metadata=row["metadata"] or {},
                similarity=similarity,
            )

            document.retrieval_score = (
                self.calculate_retrieval_score(
                    query,
                    document,
                )
            )

            # -------------------------------------------------
            # Final confidence threshold
            # -------------------------------------------------

            if document.similarity < threshold:
                continue

            candidates.append(document)

        # =====================================================
        # Final ranking
        # =====================================================

        candidates.sort(
            key=lambda document: (
                document.retrieval_score,
                document.similarity,
            ),
            reverse=True,
        )

        # =====================================================
        # Duplicate control
        # =====================================================

        unique_results: list[RetrievedDocument] = []
        seen_ids: set[str] = set()

        for result in candidates:

            if result.record_id in seen_ids:
                continue

            seen_ids.add(result.record_id)
            unique_results.append(result)

            if len(unique_results) >= top_k:
                break

        # =====================================================
        # Retrieval tracing
        # =====================================================

        print("\n" + "-" * 70)
        print("RAG RETRIEVAL TRACE")
        print("-" * 70)

        print(f"Query     : {query}")

        print(
            "Query Type: "
            f"{self.detect_query_type(query) or 'general'}"
        )

        print(f"Top-K     : {top_k}")
        print(f"Threshold : {threshold}")
        print(f"Candidates: {len(candidates)}")
        print(f"Results   : {len(unique_results)}")

        for rank, result in enumerate(
            unique_results,
            start=1,
        ):
            print(
                f"{rank}. "
                f"{result.record_id} | "
                f"semantic={result.similarity:.4f} | "
                f"score={result.retrieval_score:.4f} | "
                f"{result.title}"
            )

        print("-" * 70)

        return unique_results