import requests
from rapidfuzz import fuzz
from typing import Dict, Any, Optional

CROSSREF_WORKS = "https://api.crossref.org/works"

def crossref_lookup_by_doi(doi: str) -> Optional[Dict[str, Any]]:
    r = requests.get(f"{CROSSREF_WORKS}/{doi}", timeout=20)
    if r.status_code != 200:
        return None
    return r.json().get("message")

def crossref_search_by_title(title: str, rows: int = 5) -> Dict[str, Any]:
    params = {"query.title": title, "rows": rows}
    r = requests.get(CROSSREF_WORKS, params=params, timeout=20)
    r.raise_for_status()
    return r.json()

def best_crossref_match(ref: Dict[str, Any]) -> Dict[str, Any]:
    """
    Returns a verdict dict:
    {status, score, match_title, match_doi, reason}
    """
    title = (ref.get("title") or "").strip()
    doi = (ref.get("doi") or "").strip()

    # If DOI exists, it's the strongest signal
    if doi:
        rec = crossref_lookup_by_doi(doi)
        if rec:
            mtitle = (rec.get("title") or [""])[0]
            score = fuzz.token_set_ratio(title, mtitle) if title else 100
            return {"status": "FOUND_BY_DOI", "score": score, "match_title": mtitle, "match_doi": rec.get("DOI"), "reason": "DOI resolved in Crossref"}
        return {"status": "DOI_NOT_FOUND", "score": 0, "match_title": "", "match_doi": doi, "reason": "DOI did not resolve in Crossref"}

    # Otherwise search by title
    if not title:
        return {"status": "NO_TITLE", "score": 0, "match_title": "", "match_doi": "", "reason": "No title extracted"}

    data = crossref_search_by_title(title)
    items = data.get("message", {}).get("items", [])

    best = {"status": "NOT_FOUND", "score": 0, "match_title": "", "match_doi": "", "reason": "No good match"}
    for it in items:
        mtitle = (it.get("title") or [""])[0]
        score = fuzz.token_set_ratio(title, mtitle)
        if score > best["score"]:
            best = {
                "status": "CANDIDATE",
                "score": score,
                "match_title": mtitle,
                "match_doi": it.get("DOI", ""),
                "reason": "Best fuzzy title match from Crossref search"
            }

    # Thresholding (tune later as part of research!)
    if best["score"] >= 90:
        best["status"] = "FOUND_BY_TITLE_HIGH"
    elif best["score"] >= 75:
        best["status"] = "FOUND_BY_TITLE_MED"
    else:
        best["status"] = "NOT_FOUND"

    return best
