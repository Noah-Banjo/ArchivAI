import hashlib
import json
from datetime import datetime


class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = json.dumps(
            {
                "index": self.index,
                "timestamp": self.timestamp,
                "data": self.data,
                "previous_hash": self.previous_hash,
            },
            sort_keys=True,
        ).encode()
        return hashlib.sha256(block_string).hexdigest()

    def to_dict(self):
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "hash": self.hash,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Block":
        """Reconstruct a block from stored data; hash is recalculated for integrity."""
        return cls(
            data["index"],
            data["timestamp"],
            data["data"],
            data["previous_hash"],
        )


class Blockchain:
    def __init__(self):
        self.chain = [self._genesis()]

    def _genesis(self):
        return Block(0, datetime.utcnow().isoformat(), {"message": "Genesis Block"}, "0")

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, data) -> Block:
        previous = self.get_latest_block()
        block = Block(previous.index + 1, datetime.utcnow().isoformat(), data, previous.hash)
        self.chain.append(block)
        return block

    def is_chain_valid(self) -> bool:
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]
            if current.hash != current.calculate_hash():
                return False
            if current.previous_hash != previous.hash:
                return False
        return True

    def get_block_by_document_id(self, document_id: str) -> Block | None:
        for block in reversed(self.chain):
            if block.data.get("documentId") == document_id:
                return block
        return None

    def verify_document(self, document_id: str, document_hash: str) -> dict:
        block = self.get_block_by_document_id(document_id)
        if block and "documentHash" in block.data:
            return {
                "verified": block.data["documentHash"] == document_hash,
                "blockIndex": block.index,
                "timestamp": block.timestamp,
                "blockHash": block.hash,
            }
        return {"verified": False, "reason": "Document not found in blockchain"}

    def to_dict(self):
        return {"chain": [b.to_dict() for b in self.chain], "length": len(self.chain)}
