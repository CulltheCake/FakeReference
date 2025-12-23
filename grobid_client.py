import requests
from pathlib import Path
from typing import List, Dict
import xml.etree.ElementTree as ET

TEI_NS = {"tei": "http://www.tei-c.org/ns/1.0"}

def pdf_to_tei_xml(pdf_path: Path, grobid_url = "http://127.0.0.1:8070") -> str:
    endpoint = f"{grobid_url}/api/processFulltextDocument"
    with pdf_path.open("rb") as f:
        r = requests.post(endpoint, files={"input": f}, timeout=120)
    r.raise_for_status()
    return r.text

def extract_bibl_structs(tei_xml: str) -> List[Dict]:
    """
    Extract references from TEI XML. Returns a list of dicts:
    {raw, title, year, doi, authors[]}
    """
    root = ET.fromstring(tei_xml)

    refs = []
    for bibl in root.findall(".//tei:listBibl/tei:biblStruct", TEI_NS):
        title_el = bibl.find(".//tei:analytic/tei:title", TEI_NS)
        if title_el is None:
            title_el = bibl.find(".//tei:monogr/tei:title", TEI_NS)
        title = (title_el.text or "").strip() if title_el is not None else ""

        year = ""
        date_el = bibl.find(".//tei:monogr/tei:imprint/tei:date", TEI_NS)
        if date_el is not None:
            year = (date_el.get("when") or date_el.text or "").strip()

        doi = ""
        doi_el = bibl.find(".//tei:idno[@type='DOI']", TEI_NS)
        if doi_el is not None and doi_el.text:
            doi = doi_el.text.strip()

        authors = []
        for auth in bibl.findall(".//tei:analytic/tei:author", TEI_NS):
            surname = auth.find(".//tei:surname", TEI_NS)
            forename = auth.find(".//tei:forename", TEI_NS)
            name = " ".join(filter(None, [
                (forename.text.strip() if forename is not None and forename.text else ""),
                (surname.text.strip() if surname is not None and surname.text else "")
            ])).strip()
            if name:
                authors.append(name)

        raw = " | ".join([p for p in [title, year, doi] if p])

        refs.append({
            "raw": raw,
            "title": title,
            "year": year,
            "doi": doi,
            "authors": authors
        })

    return refs
