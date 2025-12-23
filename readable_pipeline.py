import json
from collections import Counter, defaultdict
from pathlib import Path

INPUT = "outputs/results.jsonl"   

def main():
    data = []
    for line in Path(INPUT).read_text(encoding="utf-8").splitlines():
        obj = json.loads(line)
        if "verdict" in obj:
            data.append(obj)

    if not data:
        print("No reference data found.")
        return

    per_pdf = defaultdict(list)
    for row in data:
        per_pdf[row["pdf_file"]].append(row)

    total_refs = 0
    overall = Counter()

    print("\nProcessing PDFs:", len(per_pdf), "found")
    print("────────────────────────────────────")

    for pdf, refs in per_pdf.items():
        counts = Counter(r["verdict"]["status"] for r in refs)
        n = len(refs)
        total_refs += n
        overall.update(counts)

        found = counts.get("FOUND_BY_DOI", 0) + counts.get("FOUND_BY_TITLE_HIGH", 0)
        partial = counts.get("FOUND_BY_TITLE_MED", 0)
        not_found = counts.get("NOT_FOUND", 0) + counts.get("DOI_NOT_FOUND", 0)

        print(f"{pdf}")
        print(f"  References found: {n}")
        print(f"   FOUND: {found}")
        print(f"   PARTIAL / LOW MATCH: {partial}")
        print(f"   NOT FOUND: {not_found}")
        print("────────────────────────────────────")

    print("\n Overall summary")
    print(f"  Total PDFs: {len(per_pdf)}")
    print(f"  Total references: {total_refs}")
    for k, v in overall.items():
        print(f"  {k}: {v}")

    print("\n Detailed results written to:")
    print("  outputs/results.jsonl")
    print("  outputs/summary.csv")

if __name__ == "__main__":
    main()
