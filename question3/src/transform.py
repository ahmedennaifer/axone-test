import csv


def clean_text(text):
    ui_elements = [
        "See more",
        "See translation",
        "Show more",
        "Hide",
        "See less",
        "· Translated from French",
        "Translated from French",
        "· ",
    ]
    cleaned = text
    for element in ui_elements:
        cleaned = cleaned.replace(element, "").strip()
    return " ".join(cleaned.split())


def is_duplicate(text1, text2):
    clean1 = clean_text(text1).lower()
    clean2 = clean_text(text2).lower()

    if clean1 == clean2:
        return True
    if clean1 in clean2 or clean2 in clean1:
        return True
    if len(clean1) > 100 and len(clean2) > 100 and clean1[:100] == clean2[:100]:
        return True
    return False


def remove_duplicates():
    with open("data/data.csv", "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    unique_rows = []
    for row in rows:
        if not any(
            is_duplicate(row["text"], unique_row["text"]) for unique_row in unique_rows
        ):
            row["text"] = clean_text(row["text"])
            unique_rows.append(row)

    with open("data/clean.csv", "w", newline="", encoding="utf-8") as f:
        if unique_rows:
            writer = csv.DictWriter(f, fieldnames=unique_rows[0].keys())
            writer.writeheader()
            writer.writerows(unique_rows)

    print(f"{len(rows)} -> {len(unique_rows)}")


if __name__ == "__main__":
    remove_duplicates()
