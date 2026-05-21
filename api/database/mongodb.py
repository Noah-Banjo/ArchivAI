import pymongo
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/archivai")

# Module-level singletons — one client per process, thread-safe per pymongo spec
_client: pymongo.MongoClient | None = None
_db = None


def _parse_db_name(uri: str) -> str:
    """Extract database name from a MongoDB URI."""
    if "mongodb+srv://" in uri or "mongodb://" in uri:
        path = uri.split("/")
        if len(path) > 3:
            name = path[3].split("?")[0]
            if name:
                return name
    return "archivai"


def get_client() -> pymongo.MongoClient:
    global _client
    if _client is None:
        _client = pymongo.MongoClient(
            MONGODB_URI,
            serverSelectionTimeoutMS=5000,
            maxPoolSize=50,
            minPoolSize=5,
        )
    return _client


def get_database():
    global _db
    if _db is None:
        try:
            client = get_client()
            client.admin.command("ping")
            db_name = _parse_db_name(MONGODB_URI)
            _db = client[db_name]
            print(f"MongoDB connected — database: {db_name}")
        except Exception as e:
            print(f"MongoDB connection error: {e}")
            return None
    return _db


def init_database():
    db = get_database()
    if db is None:
        return False
    try:
        existing = db.list_collection_names()
        for collection in ("documents", "blockchain_blocks", "premis_events"):
            if collection not in existing:
                db.create_collection(collection)

        db.documents.create_index("documentId", unique=True)
        db.documents.create_index("dateCreated")
        db.documents.create_index("status")
        db.blockchain_blocks.create_index("index", unique=True)
        db.premis_events.create_index(
            [("linkingObjectIdentifier.linkingObjectIdentifierValue", pymongo.ASCENDING),
             ("eventDateTime", pymongo.ASCENDING)]
        )
        print("Database initialised successfully.")
        return True
    except Exception as e:
        print(f"Database initialisation error: {e}")
        return False
