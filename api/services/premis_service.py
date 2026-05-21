"""
PREMIS 3.0 preservation event logging.

Event types used:
  ingestion                 — document accepted into the system
  messageDigestCalculation  — SHA-256 hash computed for blockchain
  characterization          — AI analysis completed
  fixityCheck               — stored hash re-verified against file
  validation                — blockchain chain integrity checked
"""
import uuid
from datetime import datetime, timezone
from database.mongodb import get_database

_AGENT = {
    "linkingAgentIdentifierType": "softwareName",
    "linkingAgentIdentifierValue": "ArchivAI",
    "linkingAgentRole": "executing program",
}


def log_event(event_type: str, document_id: str, outcome: str,
              detail: str, outcome_detail: str = "") -> dict:
    """
    Persist a PREMIS event and return it (without Mongo _id).
    Silently degrades if the database is unavailable.
    """
    event = {
        "premisVersion": "3.0",
        "eventIdentifier": {
            "eventIdentifierType": "UUID",
            "eventIdentifierValue": str(uuid.uuid4()),
        },
        "eventType": event_type,
        "eventDateTime": datetime.now(timezone.utc).isoformat(),
        "eventDetail": detail,
        "eventOutcomeInformation": {
            "eventOutcome": outcome,
            "eventOutcomeDetail": outcome_detail,
        },
        "linkingAgentIdentifier": [_AGENT],
        "linkingObjectIdentifier": [{
            "linkingObjectIdentifierType": "archivaiDocumentId",
            "linkingObjectIdentifierValue": document_id,
        }],
    }
    try:
        db = get_database()
        if db is not None:
            db.premis_events.insert_one(event)
            event.pop("_id", None)
    except Exception as e:
        print(f"PREMIS logging error: {e}")
    return event


def get_events(document_id: str) -> list:
    """Return all PREMIS events for a document, ordered by date."""
    try:
        db = get_database()
        if db is None:
            return []
        return list(
            db.premis_events.find(
                {"linkingObjectIdentifier": {
                    "$elemMatch": {"linkingObjectIdentifierValue": document_id}
                }},
                {"_id": 0},
            ).sort("eventDateTime", 1)
        )
    except Exception as e:
        print(f"PREMIS retrieval error: {e}")
        return []
