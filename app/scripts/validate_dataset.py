import json
from pathlib import Path


DATASET_PATH = Path("app/data/MoinSystems_RAG_Dataset.jsonl")

REQUIRED_FIELDS = {
    "id",
    "title",
    "category",
    "tags",
    "intents",
    "text",
    "metadata",
}


def validate_dataset() -> None:
    if not DATASET_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATASET_PATH}")

    seen_ids = set()
    total = 0
    errors = []

    with DATASET_PATH.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()

            if not line:
                continue

            total += 1

            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(
                    f"Line {line_number}: invalid JSON - {exc}"
                )
                continue

            missing = REQUIRED_FIELDS - record.keys()

            if missing:
                errors.append(
                    f"Line {line_number}: missing fields: {sorted(missing)}"
                )

            record_id = record.get("id")

            if not record_id:
                errors.append(
                    f"Line {line_number}: empty ID"
                )
            elif record_id in seen_ids:
                errors.append(
                    f"Line {line_number}: duplicate ID: {record_id}"
                )
            else:
                seen_ids.add(record_id)

            if not record.get("text", "").strip():
                errors.append(
                    f"Line {line_number}: empty text"
                )

            if not isinstance(record.get("metadata"), dict):
                errors.append(
                    f"Line {line_number}: metadata must be an object"
                )

    print(f"Records: {total}")
    print(f"Unique IDs: {len(seen_ids)}")

    if errors:
        print("\nVALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("VALIDATION PASSED")


if __name__ == "__main__":
    validate_dataset()