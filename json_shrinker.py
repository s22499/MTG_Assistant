import json
import random

# === CONFIG ===
INPUT_PATH = "data/Cards/oracle-cards.json"
OUTPUT_PATH = "data/Cards/oracle-cards-slim.json"

# Fraction of records to keep (e.g., 0.5 means keep 50%)
KEEP_FRACTION = 0.25

# Keys to remove from each JSON object
KEYS_TO_REMOVE = [
    "mtgo_id",
    "tcgplayer_id",
    "cardmarket_id",
    "layout",
    "highres_image",
    "image_status",
    "image_uris",
    "all_parts",
    "related_uris",
    "purchase_uris"
]

def slim_json(input_path: str, output_path: str, keep_fraction: float, keys_to_remove: list[str]):
    # Load original data
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"Loaded {len(data)} records.")

    # Shuffle and take a fraction
    random.shuffle(data)
    keep_count = int(len(data) * keep_fraction)
    slimmed_data = data[:keep_count]

    print(f"Keeping {keep_count} records (fraction = {keep_fraction})")

    # Remove specified keys
    for entry in slimmed_data:
        for key in keys_to_remove:
            entry.pop(key, None)  # Use pop with default to avoid KeyError

    # Save slimmed data
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(slimmed_data, f, ensure_ascii=False, indent=2)

    print(f"Slimmed data saved to: {output_path}")

if __name__ == "__main__":
    slim_json(INPUT_PATH, OUTPUT_PATH, KEEP_FRACTION, KEYS_TO_REMOVE)
