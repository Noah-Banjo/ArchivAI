from config import Config
from auth import require_api_key

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.utils import secure_filename

import os
import uuid
import threading
from datetime import datetime, timezone

from dotenv import load_dotenv
from database.mongodb import get_database, init_database
from services.ai_service import AIService
from services.blockchain_service import BlockchainService
from services.premis_service import log_event, get_events

load_dotenv()

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = Config.MAX_CONTENT_LENGTH
CORS(app, origins=Config.CORS_ORIGINS)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[Config.RATE_LIMIT_DEFAULT],
    storage_uri="memory://",
)

ai_service = AIService()
blockchain_service = BlockchainService()

os.makedirs("./storage", exist_ok=True)
init_database()


# ---------------------------------------------------------------------------
# Background processing
# ---------------------------------------------------------------------------

def _process_document(document_id: str, file_path: str, content_type: str, filename: str):
    """Run AI then blockchain in sequence, update MongoDB, log PREMIS events."""
    db = get_database()
    if db is None:
        return

    # --- AI characterisation ---
    try:
        ai_results = ai_service.process_document(document_id, file_path, content_type, filename=filename)

        db.documents.update_one(
            {"documentId": document_id},
            {
                "$set": {
                    "status": "processed",
                    "dateModified": datetime.now(timezone.utc).isoformat(),
                    "tags": ai_results.get("tags", []),
                    "formatInfo": ai_results.get("formatInfo", {}),
                    "aiMetadata": {
                        "entities": ai_results.get("entities", []),
                        "summary": ai_results.get("summary", ""),
                        "language": ai_results.get("language", "unknown"),
                        "characterCount": ai_results.get("characterCount", 0),
                    },
                }
            },
        )

        log_event(
            "characterization",
            document_id,
            "success",
            "AI analysis completed: entities extracted, tags generated, summary created.",
            f"Entities: {len(ai_results.get('entities', []))}, Tags: {len(ai_results.get('tags', []))}",
        )
    except Exception as e:
        print(f"AI processing failed for {document_id}: {e}")
        db.documents.update_one(
            {"documentId": document_id},
            {"$set": {"status": "error", "processingError": str(e)}},
        )
        log_event("characterization", document_id, "failure", "AI analysis failed.", str(e))
        return

    # --- Blockchain registration (AI metadata bound to document hash) ---
    try:
        ai_metadata_for_chain = {
            "entities": ai_results.get("entities", []),
            "tags": ai_results.get("tags", []),
            "summary": ai_results.get("summary", ""),
            "characterCount": ai_results.get("characterCount", 0),
        }

        bc_result = blockchain_service.register_document(
            document_id=document_id,
            file_path=file_path,
            ai_metadata=ai_metadata_for_chain,
        )

        if bc_result["status"] == "success":
            db.documents.update_one(
                {"documentId": document_id},
                {
                    "$set": {
                        "blockchainVerification": {
                            "status": "verified",
                            "transactionId": bc_result.get("transactionId", ""),
                            "blockIndex": bc_result.get("blockIndex"),
                            "timestamp": bc_result.get("timestamp", ""),
                            "documentHash": bc_result.get("documentHash", ""),
                        }
                    }
                },
            )
            log_event(
                "messageDigestCalculation",
                document_id,
                "success",
                "SHA-256 hash computed and registered on blockchain.",
                f"Block index: {bc_result.get('blockIndex')}, Hash: {bc_result.get('documentHash', '')[:16]}…",
            )
        else:
            db.documents.update_one(
                {"documentId": document_id},
                {
                    "$set": {
                        "blockchainVerification": {
                            "status": "error",
                            "errorMessage": bc_result.get("message", "Unknown error"),
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                        }
                    }
                },
            )
            log_event("messageDigestCalculation", document_id, "failure",
                      "Blockchain registration failed.", bc_result.get("message", ""))
    except Exception as e:
        print(f"Blockchain processing failed for {document_id}: {e}")


# ---------------------------------------------------------------------------
# Routes — public (read)
# ---------------------------------------------------------------------------

@app.route("/")
def home():
    return jsonify({
        "system": "ArchivAI",
        "description": "Blockchain + AI Digital Preservation Framework",
        "version": "2.0.0",
        "status": "operational",
        "standards": ["PREMIS 3.0", "PRONOM", "ICA RiC (aligned)"],
    })


@app.route("/health")
def health():
    db = get_database()
    bc_info = blockchain_service.get_blockchain_info()
    return jsonify({
        "status": "healthy",
        "database": "connected" if db is not None else "disconnected",
        "blockchain": {
            "blocks": bc_info["blockchainInfo"]["blocks"],
            "valid": bc_info["blockchainInfo"]["isValid"],
        },
    })


@app.route("/api/documents", methods=["GET"])
def get_documents():
    try:
        db = get_database()
        if db is None:
            return jsonify({"error": "Database connection failed"}), 500

        docs = list(db.documents.find({}, {
            "_id": 0, "documentId": 1, "filename": 1, "contentType": 1,
            "fileSize": 1, "dateCreated": 1, "title": 1, "status": 1,
            "tags": 1, "formatInfo": 1,
        }))
        return jsonify({"status": "success", "count": len(docs), "documents": docs})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/documents/<document_id>", methods=["GET"])
def get_document(document_id):
    try:
        db = get_database()
        if db is None:
            return jsonify({"error": "Database connection failed"}), 500
        doc = db.documents.find_one({"documentId": document_id}, {"_id": 0})
        if doc is None:
            return jsonify({"error": "Document not found"}), 404
        return jsonify({"status": "success", "document": doc})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/documents/<document_id>/verify", methods=["GET"])
def verify_document(document_id):
    try:
        db = get_database()
        if db is None:
            return jsonify({"error": "Database connection failed"}), 500
        doc = db.documents.find_one({"documentId": document_id}, {"_id": 0})
        if not doc:
            return jsonify({"error": "Document not found"}), 404
        result = blockchain_service.verify_document(document_id, file_path=doc.get("path"))
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/documents/<document_id>/premis-events", methods=["GET"])
def get_premis_events(document_id):
    """Return all PREMIS preservation events for a document."""
    try:
        events = get_events(document_id)
        return jsonify({"status": "success", "documentId": document_id, "events": events})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/documents/<document_id>/metadata.jsonld", methods=["GET"])
def ric_metadata(document_id):
    """
    Return ICA Records in Contexts (RiC) aligned JSON-LD metadata.
    Suitable for integration with archival linked-data catalogues
    (e.g., TNA Project Omega / Discovery API).
    """
    try:
        db = get_database()
        if db is None:
            return jsonify({"error": "Database connection failed"}), 500
        doc = db.documents.find_one({"documentId": document_id}, {"_id": 0})
        if not doc:
            return jsonify({"error": "Document not found"}), 404

        base_url = request.host_url.rstrip("/")
        fmt = doc.get("formatInfo", {})
        ai = doc.get("aiMetadata", {})
        bc = doc.get("blockchainVerification", {})

        ric_doc = {
            "@context": {
                "rico": "https://www.ica.int/standards/RiC/ontology#",
                "schema": "https://schema.org/",
                "dc": "http://purl.org/dc/elements/1.1/",
                "premis": "http://www.loc.gov/premis/rdf/v3/",
                "pronom": "https://www.nationalarchives.gov.uk/pronom/",
                "archivai": f"{base_url}/api/",
            },
            "@type": "rico:RecordResource",
            "@id": f"{base_url}/api/documents/{document_id}",
            "rico:title": doc.get("title", doc.get("filename", "")),
            "rico:creationDate": doc.get("dateCreated", ""),
            "rico:modificationDate": doc.get("dateModified", ""),
            "schema:description": ai.get("summary", ""),
            "dc:subject": doc.get("tags", []),
            "dc:language": ai.get("language", ""),
            "premis:size": doc.get("fileSize", 0),
            "premis:formatName": fmt.get("formatName", ""),
            "premis:formatRegistryKey": fmt.get("puid", ""),
            "premis:formatRegistryName": "PRONOM",
            "pronom:formatUrl": fmt.get("pronomUrl", ""),
            "rico:hasInstantiation": {
                "@type": "rico:Instantiation",
                "rico:instantiationIdentifier": document_id,
                "dc:format": doc.get("contentType", ""),
            },
            "archivai:namedEntities": ai.get("entities", []),
            "archivai:blockchainVerification": {
                "status": bc.get("status", "pending"),
                "documentHash": bc.get("documentHash", ""),
                "transactionId": bc.get("transactionId", ""),
                "blockIndex": bc.get("blockIndex"),
                "timestamp": bc.get("timestamp", ""),
            },
        }

        response = jsonify(ric_doc)
        response.headers["Content-Type"] = "application/ld+json"
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/blockchain/info", methods=["GET"])
def get_blockchain_info():
    try:
        return jsonify(blockchain_service.get_blockchain_info())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------------------------------------------------------------------
# Routes — write operations (require API key when configured)
# ---------------------------------------------------------------------------

@app.route("/api/documents/upload-simple", methods=["POST"])
@require_api_key
@limiter.limit(Config.RATE_LIMIT_UPLOAD)
def upload_document():
    if "file" not in request.files:
        return jsonify({"error": "No file part in request"}), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "No file selected"}), 400

    safe_name = secure_filename(file.filename)
    if not safe_name:
        return jsonify({"error": "Invalid filename"}), 400

    try:
        db = get_database()
        if db is None:
            return jsonify({"error": "Database connection failed"}), 500

        document_id = str(uuid.uuid4())
        directory = f"./storage/documents/{document_id}"
        os.makedirs(directory, exist_ok=True)

        file_path = os.path.join(directory, safe_name)
        file.save(file_path)

        now = datetime.now(timezone.utc).isoformat()
        relative_path = f"documents/{document_id}/{safe_name}"

        metadata = {
            "documentId": document_id,
            "filename": safe_name,
            "path": relative_path,
            "contentType": file.content_type or "application/octet-stream",
            "fileSize": os.path.getsize(file_path),
            "dateCreated": now,
            "dateModified": now,
            "status": "processing",
            "title": safe_name,
            "description": "",
            "tags": [],
            "formatInfo": {},
            "blockchainVerification": {"status": "pending", "timestamp": now},
        }
        db.documents.insert_one(metadata)

        # Log PREMIS ingestion event
        log_event(
            "ingestion",
            document_id,
            "success",
            f"Document '{safe_name}' ingested into ArchivAI.",
            f"Size: {metadata['fileSize']} bytes, Content-Type: {metadata['contentType']}",
        )

        # Background AI + blockchain processing
        threading.Thread(
            target=_process_document,
            args=(document_id, relative_path, file.content_type or "", safe_name),
            daemon=True,
        ).start()

        return jsonify({
            "status": "success",
            "documentId": document_id,
            "filename": safe_name,
            "path": relative_path,
            "dateCreated": now,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/documents/<document_id>/fixity-check", methods=["POST"])
@require_api_key
@limiter.limit("30 per minute")
def fixity_check(document_id):
    """
    Re-hash the stored file and compare against the blockchain record.
    Logs a PREMIS fixityCheck event regardless of outcome.
    """
    try:
        db = get_database()
        if db is None:
            return jsonify({"error": "Database connection failed"}), 500

        doc = db.documents.find_one({"documentId": document_id}, {"_id": 0})
        if not doc:
            return jsonify({"error": "Document not found"}), 404

        result = blockchain_service.fixity_check(document_id, doc.get("path", ""))

        log_event(
            "fixityCheck",
            document_id,
            "success" if result.get("passed") else "failure",
            "Fixity check: file hash recomputed and compared against blockchain record.",
            result.get("outcome", ""),
        )

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------

@app.errorhandler(413)
def request_entity_too_large(_):
    limit_mb = Config.MAX_CONTENT_LENGTH // (1024 * 1024)
    return jsonify({"error": f"File too large. Maximum upload size is {limit_mb} MB."}), 413


@app.errorhandler(429)
def rate_limit_exceeded(_):
    return jsonify({"error": "Rate limit exceeded. Please slow down your requests."}), 429


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=Config.DEBUG, port=8000)
