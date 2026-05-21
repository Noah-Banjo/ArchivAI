"""
AI text analysis pipeline.

NER uses spaCy en_core_web_sm (downloaded on first run).
Keyword tagging uses NLTK frequency distribution.
File format identification uses a curated PRONOM registry map.
"""
import os
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist
import pypdf

# ---------------------------------------------------------------------------
# NLTK bootstrap
# ---------------------------------------------------------------------------
for _resource, _kind in [("punkt_tab", "tokenizers"), ("punkt", "tokenizers"), ("stopwords", "corpora")]:
    try:
        nltk.data.find(f"{_kind}/{_resource}")
    except LookupError:
        nltk.download(_resource, quiet=True)

# ---------------------------------------------------------------------------
# spaCy — lazy singleton (downloaded on first use)
# ---------------------------------------------------------------------------
_nlp = None


def _get_nlp():
    global _nlp
    if _nlp is None:
        import spacy
        try:
            _nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Downloading spaCy en_core_web_sm model…")
            spacy.cli.download("en_core_web_sm")
            _nlp = spacy.load("en_core_web_sm")
    return _nlp


# ---------------------------------------------------------------------------
# PRONOM format registry (The National Archives, UK)
# https://www.nationalarchives.gov.uk/pronom/
# ---------------------------------------------------------------------------
_PRONOM = {
    ".pdf":  {"puid": "fmt/276",   "formatName": "Acrobat PDF 1.7",                    "mimeType": "application/pdf"},
    ".docx": {"puid": "fmt/412",   "formatName": "Microsoft Word 2007 onwards",         "mimeType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"},
    ".doc":  {"puid": "fmt/40",    "formatName": "Microsoft Word Document 97-2003",     "mimeType": "application/msword"},
    ".xlsx": {"puid": "fmt/214",   "formatName": "Microsoft Excel 2007 onwards",        "mimeType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"},
    ".xls":  {"puid": "fmt/55",    "formatName": "Microsoft Excel 97-2003",             "mimeType": "application/vnd.ms-excel"},
    ".pptx": {"puid": "fmt/215",   "formatName": "Microsoft PowerPoint 2007 onwards",   "mimeType": "application/vnd.openxmlformats-officedocument.presentationml.presentation"},
    ".odt":  {"puid": "fmt/290",   "formatName": "OpenDocument Text 1.2",              "mimeType": "application/vnd.oasis.opendocument.text"},
    ".rtf":  {"puid": "fmt/969",   "formatName": "Rich Text Format",                   "mimeType": "application/rtf"},
    ".txt":  {"puid": "x-fmt/111", "formatName": "Plain Text File",                    "mimeType": "text/plain"},
    ".md":   {"puid": "x-fmt/111", "formatName": "Plain Text File",                    "mimeType": "text/plain"},
    ".csv":  {"puid": "x-fmt/18",  "formatName": "Comma Separated Values",             "mimeType": "text/csv"},
    ".html": {"puid": "fmt/100",   "formatName": "Hypertext Markup Language 4.01",     "mimeType": "text/html"},
    ".htm":  {"puid": "fmt/100",   "formatName": "Hypertext Markup Language 4.01",     "mimeType": "text/html"},
    ".xml":  {"puid": "fmt/101",   "formatName": "Extensible Markup Language 1.0",     "mimeType": "application/xml"},
    ".json": {"puid": "fmt/817",   "formatName": "JavaScript Object Notation",         "mimeType": "application/json"},
    ".jpg":  {"puid": "fmt/43",    "formatName": "JPEG File Interchange Format 1.02",  "mimeType": "image/jpeg"},
    ".jpeg": {"puid": "fmt/43",    "formatName": "JPEG File Interchange Format 1.02",  "mimeType": "image/jpeg"},
    ".png":  {"puid": "fmt/13",    "formatName": "Portable Network Graphics 1.0",      "mimeType": "image/png"},
    ".tif":  {"puid": "fmt/10",    "formatName": "Tagged Image File Format 6.0",       "mimeType": "image/tiff"},
    ".tiff": {"puid": "fmt/10",    "formatName": "Tagged Image File Format 6.0",       "mimeType": "image/tiff"},
    ".mp3":  {"puid": "fmt/134",   "formatName": "MPEG 1/2 Audio Layer 3",             "mimeType": "audio/mpeg"},
    ".wav":  {"puid": "fmt/6",     "formatName": "Waveform Audio 1.0",                 "mimeType": "audio/x-wav"},
    ".mp4":  {"puid": "fmt/199",   "formatName": "MPEG-4 Media File",                  "mimeType": "video/mp4"},
    ".zip":  {"puid": "fmt/289",   "formatName": "ZIP Format",                         "mimeType": "application/zip"},
}

_SPACY_LABEL_MAP = {
    "PERSON":   "PERSON",
    "ORG":      "ORGANIZATION",
    "GPE":      "PLACE",
    "LOC":      "LOCATION",
    "DATE":     "DATE",
    "TIME":     "TIME",
    "MONEY":    "MONETARY_VALUE",
    "PRODUCT":  "PRODUCT",
    "EVENT":    "EVENT",
    "FAC":      "FACILITY",
    "NORP":     "NATIONALITY_OR_GROUP",
    "LAW":      "LEGAL_REFERENCE",
    "WORK_OF_ART": "WORK_OF_ART",
    "LANGUAGE": "LANGUAGE",
}


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def identify_format(filename: str) -> dict:
    """Return PRONOM format information for a filename."""
    ext = os.path.splitext(filename)[1].lower()
    info = _PRONOM.get(ext)
    if info:
        return {
            "puid": info["puid"],
            "formatName": info["formatName"],
            "mimeType": info["mimeType"],
            "extension": ext,
            "pronomUrl": f"https://www.nationalarchives.gov.uk/pronom/{info['puid']}",
            "identified": True,
        }
    return {
        "puid": None,
        "formatName": "Unknown Format",
        "mimeType": "application/octet-stream",
        "extension": ext,
        "pronomUrl": "https://www.nationalarchives.gov.uk/pronom/",
        "identified": False,
    }


def extract_text(file_path: str, content_type: str | None = None) -> str:
    """Extract plain text from a file."""
    if not os.path.exists(file_path):
        return ""

    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf" or (content_type and "pdf" in content_type):
        return _extract_pdf(file_path)

    if ext in (".txt", ".md", ".csv", ".html", ".htm", ".xml", ".json") or (
        content_type and "text" in content_type
    ):
        return _read_text_file(file_path)

    return ""


def extract_entities(text: str) -> list:
    """Extract named entities with spaCy NER plus regex for email addresses."""
    entities = []
    seen: set[tuple] = set()

    # spaCy NER
    nlp = _get_nlp()
    # spaCy has a default max doc length of 1M characters
    doc = nlp(text[:1_000_000])
    for ent in doc.ents:
        key = (ent.text.strip(), ent.label_)
        if key not in seen:
            seen.add(key)
            entities.append({
                "text": ent.text.strip(),
                "type": _SPACY_LABEL_MAP.get(ent.label_, ent.label_),
                "confidence": 0.85,
            })

    # Regex for email addresses (spaCy does not extract these)
    for email in re.findall(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b", text):
        key = (email, "EMAIL")
        if key not in seen:
            seen.add(key)
            entities.append({"text": email, "type": "EMAIL", "confidence": 0.9})

    return entities


def generate_tags(text: str, max_tags: int = 10) -> list:
    """Return top-N keywords by frequency after stopword removal."""
    if not text:
        return []
    try:
        tokens = word_tokenize(text.lower())
    except Exception:
        tokens = text.lower().split()
    stops = set(stopwords.words("english"))
    filtered = [t for t in tokens if t.isalpha() and t not in stops and len(t) > 3]
    return [word for word, _ in FreqDist(filtered).most_common(max_tags)]


def analyze_document(file_path: str, content_type: str | None = None, filename: str | None = None) -> dict:
    """Full document analysis: text, NER, tags, summary, PRONOM format."""
    fname = filename or os.path.basename(file_path)
    format_info = identify_format(fname)

    text = extract_text(file_path, content_type)

    if not text:
        ext = os.path.splitext(fname)[1].lower()
        default_tags = (
            ["image", ext.lstrip("."), "visual"]
            if ext in (".jpg", ".jpeg", ".png", ".tif", ".tiff", ".gif", ".bmp")
            else [ext.lstrip(".") or "unknown"]
        )
        return {
            "text": "",
            "entities": [],
            "tags": default_tags,
            "summary": "No text content extracted",
            "language": "unknown",
            "characterCount": 0,
            "formatInfo": format_info,
        }

    entities = extract_entities(text)
    tags = generate_tags(text)
    summary = text[:300] + "…" if len(text) > 300 else text

    return {
        "text": text[:2000] + "…" if len(text) > 2000 else text,
        "entities": entities,
        "tags": tags,
        "summary": summary,
        "language": "en",
        "characterCount": len(text),
        "formatInfo": format_info,
    }


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _extract_pdf(path: str) -> str:
    try:
        text = ""
        with open(path, "rb") as f:
            reader = pypdf.PdfReader(f)
            for page in reader.pages:
                text += (page.extract_text() or "") + "\n"
        return text.strip()
    except Exception as e:
        print(f"PDF extraction error: {e}")
        return ""


def _read_text_file(path: str) -> str:
    for enc in ("utf-8", "latin-1", "cp1252"):
        try:
            with open(path, "r", encoding=enc) as f:
                return f.read()
        except (UnicodeDecodeError, LookupError):
            continue
    return ""
