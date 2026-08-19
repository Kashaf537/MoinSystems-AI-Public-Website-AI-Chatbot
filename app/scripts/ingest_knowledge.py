
"""
MoinSystems AI - Day 2 RAG Knowledge Ingestion

Responsibilities
-----------------
1. Load the approved JSONL knowledge dataset.
2. Validate required fields.
3. Validate duplicate record IDs.
4. Normalize text and metadata.
5. Generate local embeddings using SentenceTransformers.
6. Store knowledge_document records.
7. Store knowledge_chunk records.
8. Upsert by stable dataset record ID.
9. Preserve dataset version and retrieval metadata.
10. Verify embedding dimensions before database insertion.

Embedding model
---------------
sentence-transformers/all-MiniLM-L6-v2

Embedding dimension
-------------------
384
"""

import json
import sys
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.embeddings.local_embeddings import LocalEmbeddingProvider
from app.models.knowledge_chunk import KnowledgeChunk
from app.models.knowledge_document import KnowledgeDocument


# ============================================================
# Configuration
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_PATH = (
    PROJECT_ROOT
    / "app"
    / "data"
    / "MoinSystems_RAG_Dataset.jsonl"
)

EXPECTED_EMBEDDING_DIM = 384

REQUIRED_FIELDS = {
    "id",
    "title",
    "category",
    "tags",
    "intents",
    "text",
    "metadata",
}


# ============================================================
# Normalization
# ============================================================

def normalize_text(value: Any) -> str:
    """
    Normalize whitespace while preserving the meaning of the text.
    """

    if value is None:
        return ""

    return " ".join(str(value).split()).strip()


def normalize_metadata(
    metadata: dict[str, Any],
) -> dict[str, Any]:
    """
    Normalize metadata values without changing their meaning.
    """

    normalized: dict[str, Any] = {}

    for key, value in metadata.items():

        clean_key = str(key).strip()

        if isinstance(value, str):
            normalized[clean_key] = value.strip()

        elif isinstance(value, list):
            normalized[clean_key] = [
                item.strip() if isinstance(item, str) else item
                for item in value
            ]

        else:
            normalized[clean_key] = value

    return normalized


# ============================================================
# Dataset loading
# ============================================================

def load_jsonl(
    path: Path,
) -> list[dict[str, Any]]:
    """
    Load and validate the JSONL dataset.
    """

    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {path}"
        )

    records: list[dict[str, Any]] = []

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:

        for line_number, line in enumerate(
            file,
            start=1,
        ):

            line = line.strip()

            if not line:
                continue

            try:
                record = json.loads(line)

            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSON on line {line_number}: {exc}"
                ) from exc

            if not isinstance(record, dict):
                raise ValueError(
                    f"Line {line_number} must contain a JSON object."
                )

            # ------------------------------------------------
            # Required field validation
            # ------------------------------------------------

            missing = REQUIRED_FIELDS - set(record.keys())

            if missing:
                raise ValueError(
                    f"Line {line_number} is missing fields: "
                    f"{sorted(missing)}"
                )

            # ------------------------------------------------
            # ID validation
            # ------------------------------------------------

            record_id = normalize_text(record["id"])

            if not record_id:
                raise ValueError(
                    f"Line {line_number}: empty id."
                )

            # ------------------------------------------------
            # Text validation
            # ------------------------------------------------

            text = normalize_text(record["text"])

            if not text:
                raise ValueError(
                    f"Line {line_number}: empty text."
                )

            # ------------------------------------------------
            # Metadata validation
            # ------------------------------------------------

            if not isinstance(
                record["metadata"],
                dict,
            ):
                raise ValueError(
                    f"Line {line_number}: "
                    f"metadata must be an object."
                )

            # ------------------------------------------------
            # Normalize record
            # ------------------------------------------------

            normalized_record = {
                "id": record_id,
                "title": normalize_text(record["title"]),
                "category": normalize_text(record["category"]),
                "tags": normalize_text(record["tags"]),
                "intents": normalize_text(record["intents"]),
                "text": text,
                "metadata": normalize_metadata(
                    record["metadata"]
                ),
            }

            # ------------------------------------------------
            # Validate important fields
            # ------------------------------------------------

            for field in (
                "title",
                "category",
                "tags",
                "intents",
            ):

                if not normalized_record[field]:
                    raise ValueError(
                        f"Line {line_number}: "
                        f"empty required field '{field}'."
                    )

            records.append(normalized_record)

    if not records:
        raise ValueError(
            "Dataset contains no valid records."
        )

    return records


# ============================================================
# Duplicate ID validation
# ============================================================

def validate_duplicate_ids(
    records: list[dict[str, Any]],
) -> None:
    """
    Ensure dataset IDs are unique before ingestion.
    """

    ids = [
        record["id"]
        for record in records
    ]

    seen: set[str] = set()
    duplicates: set[str] = set()

    for record_id in ids:

        if record_id in seen:
            duplicates.add(record_id)

        seen.add(record_id)

    if duplicates:
        raise ValueError(
            "Duplicate dataset IDs found: "
            f"{sorted(duplicates)}"
        )


# ============================================================
# Dataset version
# ============================================================

def get_version(
    metadata: dict[str, Any],
) -> str:
    """
    Extract dataset version from metadata.
    """

    version = metadata.get("version")

    if version is None:
        raise ValueError(
            "Dataset record is missing metadata.version."
        )

    version = str(version).strip()

    if not version:
        raise ValueError(
            "Dataset record contains an empty metadata.version."
        )

    return version


# ============================================================
# Embedding validation
# ============================================================

def validate_embedding(
    record_id: str,
    embedding: list[float],
) -> None:
    """
    Validate generated embedding.
    """

    if embedding is None:
        raise ValueError(
            f"Embedding is None for {record_id}."
        )

    if not embedding:
        raise ValueError(
            f"Empty embedding generated for {record_id}."
        )

    if len(embedding) != EXPECTED_EMBEDDING_DIM:
        raise ValueError(
            f"Embedding dimension mismatch for {record_id}: "
            f"expected {EXPECTED_EMBEDDING_DIM}, "
            f"got {len(embedding)}"
        )

    for value in embedding:

        if value is None:
            raise ValueError(
                f"Embedding contains null value for {record_id}."
            )


# ============================================================
# Main ingestion
# ============================================================

def ingest() -> None:

    print("=" * 70)
    print("MoinSystems AI - Day 2 Knowledge Ingestion")
    print("=" * 70)

    print(
        f"\nDataset: {DATASET_PATH}"
    )

    # ========================================================
    # 1. Load dataset
    # ========================================================

    records = load_jsonl(
        DATASET_PATH
    )

    print(
        f"Records loaded: {len(records)}"
    )

    # ========================================================
    # 2. Duplicate validation
    # ========================================================

    validate_duplicate_ids(
        records
    )

    print(
        "Duplicate ID check: PASSED"
    )

    # ========================================================
    # 3. Embedding provider
    # ========================================================

    embedding_provider = (
        LocalEmbeddingProvider()
    )

    print(
        f"Embedding model: "
        f"{embedding_provider.model_name}"
    )

    print(
        f"Embedding dimensions: "
        f"{EXPECTED_EMBEDDING_DIM}"
    )

    # ========================================================
    # 4. Verify embedding provider itself
    # ========================================================

    test_embedding = embedding_provider.embed(
        "MoinSystems AI provides software development services."
    )

    validate_embedding(
        "embedding_provider_test",
        test_embedding,
    )

    print(
        "Embedding provider check: PASSED"
    )

    # ========================================================
    # 5. Database
    # ========================================================

    db: Session = SessionLocal()

    documents_created = 0
    documents_updated = 0

    chunks_created = 0
    chunks_updated = 0

    try:

        # ====================================================
        # Process every record
        # ====================================================

        for index, record in enumerate(
            records,
            start=1,
        ):

            record_id = record["id"]

            title = record["title"]

            category = record["category"]

            tags = record["tags"]

            intents = record["intents"]

            text = record["text"]

            metadata = record["metadata"]

            version = get_version(
                metadata
            )

            # ------------------------------------------------
            # Generate embedding
            # ------------------------------------------------

            embedding = embedding_provider.embed(
                text
            )

            validate_embedding(
                record_id,
                embedding,
            )

            # ------------------------------------------------
            # Document UPSERT
            # ------------------------------------------------

            document = db.scalar(
                select(KnowledgeDocument).where(
                    KnowledgeDocument.external_id
                    == record_id
                )
            )

            if document is None:

                document = KnowledgeDocument(
                    external_id=record_id,
                    title=title,
                    category=category,
                    tags=tags,
                    intents=intents,
                    content=text,
                    data_status=metadata.get(
                        "data_status",
                        "cleaned_validated",
                    ),
                    source_basis=(
                        metadata.get(
                            "source_basis"
                        )
                        or None
                    ),
                    dataset_version=version,
                    metadata_json=metadata,
                )

                db.add(document)

                db.flush()

                documents_created += 1

            else:

                document.title = title

                document.category = category

                document.tags = tags

                document.intents = intents

                document.content = text

                document.data_status = metadata.get(
                    "data_status",
                    "cleaned_validated",
                )

                document.source_basis = (
                    metadata.get(
                        "source_basis"
                    )
                    or None
                )

                document.dataset_version = version

                document.metadata_json = metadata

                documents_updated += 1

            # ------------------------------------------------
            # Chunk UPSERT
            # ------------------------------------------------

            chunk = db.scalar(
                select(KnowledgeChunk).where(
                    KnowledgeChunk.document_id
                    == document.id,
                    KnowledgeChunk.chunk_index
                    == 0,
                )
            )

            if chunk is None:

                chunk = KnowledgeChunk(
                    document_id=document.id,
                    chunk_index=0,
                    text=text,
                    embedding=embedding,
                )

                db.add(chunk)

                chunks_created += 1

            else:

                chunk.text = text

                chunk.embedding = embedding

                chunks_updated += 1

            # ------------------------------------------------
            # Progress
            # ------------------------------------------------

            if (
                index % 10 == 0
                or index == len(records)
            ):

                print(
                    f"Processed "
                    f"{index}/{len(records)} records..."
                )

        # ====================================================
        # Commit ONLY after all records succeed
        # ====================================================

        db.commit()

    except Exception:

        db.rollback()

        raise

    finally:

        db.close()

    # ========================================================
    # 6. Final report
    # ========================================================

    print("\n" + "=" * 70)
    print("INGESTION COMPLETE")
    print("=" * 70)

    print(
        f"Documents created : "
        f"{documents_created}"
    )

    print(
        f"Documents updated : "
        f"{documents_updated}"
    )

    print(
        f"Chunks created    : "
        f"{chunks_created}"
    )

    print(
        f"Chunks updated    : "
        f"{chunks_updated}"
    )

    print(
        f"Total records     : "
        f"{len(records)}"
    )

    print(
        "\nDataset version: v2"
    )

    print(
        "Embedding model: "
        "sentence-transformers/all-MiniLM-L6-v2"
    )

    print(
        f"Embedding dimensions: "
        f"{EXPECTED_EMBEDDING_DIM}"
    )


# ============================================================
# Entry point
# ============================================================

if __name__ == "__main__":

    try:

        ingest()

    except Exception as exc:

        print(
            f"\nERROR: {exc}"
        )

        sys.exit(1)

