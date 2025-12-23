import json
from pathlib import Path
from tqdm import tqdm

from grobid_client import pdf_to_tei_xml, extract_bibl_structs
from validate_crossref import best_crossref_match

def run(input_dir: str, output_path: str, grobid_url: str = "http://localhost:8070"):
    input_dir = Path(input_dir)
    pdfs = sorted(input_dir.glob("*.pdf"))

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    with out.open("w", encoding="utf-8") as f:
        for pdf in tqdm(pdfs, desc="Processing PDFs"):
            try:
                tei = pdf_to_tei_xml(pdf, grobid_url=grobid_url)
                refs = extract_bibl_structs(tei)

                for idx, ref in enumerate(refs):
                    verdict = best_crossref_match(ref)
                    record = {
                        "pdf_file": pdf.name,
                        "ref_index": idx,
                        "ref": ref,
                        "verdict": verdict
                    }
                    f.write(json.dumps(record, ensure_ascii=False) + "\n")

            except Exception as e:
                err = {"pdf_file": pdf.name, "error": str(e)}
                f.write(json.dumps(err, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    run(input_dir="pdfs", output_path="outputs/results.jsonl")
