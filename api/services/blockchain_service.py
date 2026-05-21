import os
import hashlib
from services.blockchain.simulated_blockchain import Blockchain, Block
from database.mongodb import get_database


class BlockchainService:

    def __init__(self):
        self.storage_path = os.getenv("STORAGE_PATH", "./storage")
        self.blockchain = Blockchain()
        self._load_chain()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _load_chain(self):
        """Restore chain from MongoDB on startup; persist genesis block if empty."""
        try:
            db = get_database()
            if db is None:
                print("WARNING: No DB — blockchain running in non-persistent memory mode.")
                return

            blocks = list(db.blockchain_blocks.find({}, {"_id": 0}).sort("index", 1))
            if not blocks:
                self._persist_block(db, self.blockchain.chain[0])
                return

            self.blockchain.chain = [Block.from_dict(b) for b in blocks]
            print(f"Blockchain restored — {len(self.blockchain.chain)} blocks loaded.")
        except Exception as e:
            print(f"WARNING: Could not load blockchain from DB: {e}. Non-persistent mode.")

    def _persist_block(self, db, block: Block):
        db.blockchain_blocks.update_one(
            {"index": block.index},
            {"$set": block.to_dict()},
            upsert=True,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def file_hash(self, file_path: str) -> str | None:
        """Return the SHA-256 hex digest of a file."""
        try:
            h = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(65536), b""):
                    h.update(chunk)
            return h.hexdigest()
        except Exception as e:
            print(f"Hash error: {e}")
            return None

    def register_document(self, document_id: str, file_path: str, ai_metadata: dict | None = None) -> dict:
        """
        Add a document to the blockchain.

        ai_metadata is included in the block data so that the AI-derived
        content (entities, tags, summary) is cryptographically bound to
        the original document hash — the core ArchivAI innovation.
        """
        try:
            full_path = os.path.join(self.storage_path, file_path)
            doc_hash = self.file_hash(full_path)
            if not doc_hash:
                return {"status": "error", "message": "Could not calculate document hash"}

            block_data = {
                "documentId": document_id,
                "documentHash": doc_hash,
                "aiMetadata": ai_metadata or {},
            }

            new_block = self.blockchain.add_block(block_data)

            db = get_database()
            if db is not None:
                self._persist_block(db, new_block)

            return {
                "status": "success",
                "transactionId": new_block.hash,
                "blockIndex": new_block.index,
                "timestamp": new_block.timestamp,
                "documentHash": doc_hash,
            }
        except Exception as e:
            print(f"Blockchain registration error: {e}")
            return {"status": "error", "message": str(e)}

    def verify_document(self, document_id: str, file_path: str | None = None) -> dict:
        """Verify a document's hash against its blockchain record."""
        try:
            doc_hash = None
            if file_path:
                full_path = os.path.join(self.storage_path, file_path)
                doc_hash = self.file_hash(full_path)

            if doc_hash:
                result = self.blockchain.verify_document(document_id, doc_hash)
            else:
                block = self.blockchain.get_block_by_document_id(document_id)
                result = (
                    {
                        "verified": True,
                        "blockIndex": block.index,
                        "timestamp": block.timestamp,
                        "blockHash": block.hash,
                        "documentHash": block.data.get("documentHash"),
                    }
                    if block
                    else {"verified": False, "reason": "Document not found in blockchain"}
                )

            return {"status": "success", "documentId": document_id, "verification": result}
        except Exception as e:
            print(f"Blockchain verification error: {e}")
            return {"status": "error", "message": str(e), "documentId": document_id}

    def fixity_check(self, document_id: str, file_path: str) -> dict:
        """
        Re-hash the stored file and compare against the blockchain record.
        Returns pass/fail with the current and expected hashes.
        """
        try:
            full_path = os.path.join(self.storage_path, file_path)
            current_hash = self.file_hash(full_path)
            if not current_hash:
                return {
                    "status": "error",
                    "passed": False,
                    "message": "Could not compute current file hash",
                }

            block = self.blockchain.get_block_by_document_id(document_id)
            if not block:
                return {
                    "status": "error",
                    "passed": False,
                    "message": "Document not found in blockchain",
                }

            expected_hash = block.data.get("documentHash")
            passed = current_hash == expected_hash

            return {
                "status": "success",
                "passed": passed,
                "documentId": document_id,
                "currentHash": current_hash,
                "expectedHash": expected_hash,
                "blockIndex": block.index,
                "blockTimestamp": block.timestamp,
                "outcome": "PASS — file integrity confirmed" if passed else "FAIL — hash mismatch detected",
            }
        except Exception as e:
            print(f"Fixity check error: {e}")
            return {"status": "error", "passed": False, "message": str(e)}

    def get_blockchain_info(self) -> dict:
        return {
            "status": "success",
            "blockchainInfo": {
                "blocks": len(self.blockchain.chain),
                "isValid": self.blockchain.is_chain_valid(),
                "latestBlock": self.blockchain.get_latest_block().to_dict(),
            },
        }
