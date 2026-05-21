# ArchivAI: Blockchain + AI Digital Preservation Framework

ArchivAI is a research-grade framework that integrates blockchain verification with AI-powered metadata extraction for digital preservation. It directly extends the ARCHANGEL project (UK National Archives / University of Surrey, 2019) by applying the combined AI + blockchain pipeline to all document types and making AI-derived metadata cryptographically verifiable.

Published at **iPRES 2025** (Wellington, Aotearoa New Zealand):
> Adebanjo, O. N., Alabi, A. V., & Bolaji, O. O. (2025). *ArchivAI Revolution: Pioneering the Fusion of Blockchain, AI, and ML for Digital Preservation.*

---

## The Problem ArchivAI Solves

Digital archives face three compounding pressures:

1. **Authentication** — deepfakes and AI-generated content make traditional checksums insufficient
2. **Backlog** — staff and resources cannot keep pace with born-digital volume
3. **Silos** — disconnected preservation systems undermine consistent chain of custody

ArchivAI addresses all three simultaneously: AI processes and describes content at scale, blockchain makes that processing cryptographically verifiable, and both operate through a single integrated pipeline.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface Layer                      │
├─────────────────────────────────────────────────────────────┤
│                       Flask API Layer                         │
├──────────────────────────┬──────────────────────────────────┤
│   AI Processing Pipeline │   Blockchain Verification Layer   │
│  • spaCy NER (PERSON,    │  • SHA-256 document hash          │
│    ORG, PLACE, DATE…)    │  • AI metadata bound to block     │
│  • Keyword extraction    │  • Persistent chain (MongoDB)     │
│  • Summarisation         │  • Fixity check on demand         │
│  • PRONOM format ID      │                                   │
├──────────────────────────┴──────────────────────────────────┤
│                 Storage Layer (MongoDB Atlas)                  │
│  documents · blockchain_blocks · premis_events               │
└─────────────────────────────────────────────────────────────┘
```

### What makes ArchivAI distinctive

| Capability | ARCHANGEL (TNA, 2019) | ArchivAI |
|---|---|---|
| Blockchain provenance | Ethereum (video only) | Persistent chain, all doc types |
| AI fingerprinting | Perceptual hash | SHA-256 + AI metadata bound to block |
| Named Entity Recognition | None | spaCy: PERSON, ORG, PLACE, DATE, LAW… |
| File format identification | None | PRONOM registry (TNA standard) |
| PREMIS event logging | None | Full PREMIS 3.0 lifecycle events |
| Metadata standards | None | PRONOM + RiC-aligned JSON-LD export |
| Open architecture | No | MIT licence, REST API |

---

## Standards Compliance

- **PRONOM** — every ingested document is identified against The National Archives' PRONOM format registry (PUID assigned)
- **PREMIS 3.0** — all preservation events (ingestion, characterization, messageDigestCalculation, fixityCheck) are logged as structured PREMIS events
- **ICA Records in Contexts (RiC)** — each document exposes a `/metadata.jsonld` endpoint returning RiC-aligned JSON-LD, suitable for integration with linked-data archival catalogues
- **OAIS** — system design maps to OAIS ingest and access workflows

---

## Technology Stack

| Layer | Technology |
|---|---|
| API | Flask 3.x (Python) |
| NLP / NER | spaCy `en_core_web_sm` |
| Keyword extraction | NLTK frequency distribution |
| PDF parsing | pypdf |
| Blockchain | Custom SHA-256 chain, persisted to MongoDB |
| Database | MongoDB Atlas |
| Deployment | Gunicorn on Render |

---

## API Reference

### Public endpoints (no auth required)

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | System status |
| GET | `/health` | Database + blockchain health |
| GET | `/api/documents` | List all documents |
| GET | `/api/documents/{id}` | Get document detail |
| GET | `/api/documents/{id}/verify` | Verify against blockchain |
| GET | `/api/documents/{id}/premis-events` | Full PREMIS event log |
| GET | `/api/documents/{id}/metadata.jsonld` | RiC-aligned JSON-LD |
| GET | `/api/blockchain/info` | Chain statistics |

### Authenticated endpoints (set `X-API-Key` header when `API_KEY` env var is configured)

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/documents/upload-simple` | Ingest a document |
| POST | `/api/documents/{id}/fixity-check` | Run fixity check |

---

## Installation

### Prerequisites
- Python 3.10+
- MongoDB Atlas account (or local MongoDB)

### Setup

```bash
git clone https://github.com/Noah-Banjo/ArchivAI.git
cd ArchivAI/api
pip install -r requirements.txt
```

Create `.env` in the `api/` directory:

```env
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/archivai
API_KEY=your-secret-key          # optional — omit to disable auth (dev mode)
FLASK_DEBUG=false
MAX_UPLOAD_SIZE_MB=50
```

Run:

```bash
python app.py          # development
gunicorn app:app       # production
```

The spaCy `en_core_web_sm` model is downloaded automatically on first run.

### Environment variables

| Variable | Default | Description |
|---|---|---|
| `MONGODB_URI` | `mongodb://localhost:27017/archivai` | MongoDB connection string |
| `API_KEY` | *(unset)* | API key for write operations; unset = auth disabled |
| `FLASK_DEBUG` | `false` | Enable Flask debug mode |
| `MAX_UPLOAD_SIZE_MB` | `50` | Maximum upload file size |
| `STORAGE_PATH` | `./storage` | Local file storage root |
| `CORS_ORIGINS` | `*` | Comma-separated allowed origins |

---

## Demo

Live demo: https://archivai-demo.onrender.com  
Setup video: https://youtu.be/AlkG2o08i7I *(set quality to 1080p)*

---

## Research Context

ArchivAI builds directly on:

- **ARCHANGEL** (UK National Archives + University of Surrey, 2019) — blockchain provenance for video archives
- Lemieux (2017) — blockchain typology for recordkeeping
- Colavizza et al. (2022) — AI and archives survey
- Jaillant & McDonald (2024) — computational methods in digital archives

The March 2026 *"Sifting the Digital Heap"* scoping study identified AI-powered metadata enrichment for textual materials as one of four national priorities for UK digital archives. ArchivAI directly addresses this priority.

---

## Team

- **[Oluseyi Noah Adebanjo](https://orcid.org/0009-0002-6367-5999)** — Center for Arkansas History and Culture, University of Arkansas at Little Rock
- **[Anuoluwapo Victoria Alabi](https://orcid.org/0009-0002-3641-3977)** — Prairie View A&M University
- **[Oyeleke Onaolapo Bolaji](https://orcid.org/0009-0009-0871-7333)** — Yaşar Üniversitesi

Contact: onadebanjo@ualr.edu

---

## Citation

```bibtex
@inproceedings{adebanjo2025archivai,
  title     = {ArchivAI Revolution: Pioneering the Fusion of Blockchain, AI, and ML for Digital Preservation},
  author    = {Adebanjo, Oluseyi Noah and Alabi, Anuoluwapo Victoria and Bolaji, Oyeleke Onaolapo},
  booktitle = {Proceedings of the 21st International Conference on Digital Preservation (iPRES 2025)},
  year      = {2025},
  address   = {Wellington, Aotearoa New Zealand}
}
```

---

## Licence

MIT — see [LICENSE](LICENSE)

## Acknowledgements

The authors acknowledge the Center for Arkansas History and Culture (CAHC) and Amanda McQueen, Elise Tanner, and Brigitte Billeaudeaux for their support.
