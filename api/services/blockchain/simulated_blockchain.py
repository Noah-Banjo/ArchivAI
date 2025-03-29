import hashlib
import json
import time
from datetime import datetime

class Block:
    """A simple block in our blockchain"""
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()
        
    def calculate_hash(self):
        """Calculate SHA-256 hash of the block"""
        block_string = json.dumps({"index": self.index, 
                                  "timestamp": self.timestamp, 
                                  "data": self.data, 
                                  "previous_hash": self.previous_hash}, 
                                  sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()
    
    def to_dict(self):
        """Convert block to dictionary"""
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "hash": self.hash
        }

class Blockchain:
    """A simplified blockchain implementation"""
    def __init__(self):
        """Initialize blockchain with genesis block"""
        self.chain = [self.create_genesis_block()]
        
    def create_genesis_block(self):
        """Create the first block in the chain"""
        return Block(0, datetime.now().isoformat(), {"message": "Genesis Block"}, "0")
    
    def get_latest_block(self):
        """Get the most recent block in the chain"""
        return self.chain[-1]
    
    def add_block(self, data):
        """Add a new block to the chain"""
        previous_block = self.get_latest_block()
        new_index = previous_block.index + 1
        new_timestamp = datetime.now().isoformat()
        new_hash = previous_block.hash
        new_block = Block(new_index, new_timestamp, data, new_hash)
        self.chain.append(new_block)
        return new_block
    
    def is_chain_valid(self):
        """Verify the blockchain integrity"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            
            # Check if hash is correctly calculated
            if current_block.hash != current_block.calculate_hash():
                return False
            
            # Check if this block points to the correct previous block
            if current_block.previous_hash != previous_block.hash:
                return False
        
        return True
    
    def get_block_by_document_id(self, document_id):
        """Find a block containing the given document ID"""
        for block in reversed(self.chain):
            if 'documentId' in block.data and block.data['documentId'] == document_id:
                return block
        return None
    
    def verify_document(self, document_id, document_hash):
        """Verify a document's hash against the blockchain"""
        block = self.get_block_by_document_id(document_id)
        if block and 'documentHash' in block.data:
            return {
                "verified": block.data['documentHash'] == document_hash,
                "blockIndex": block.index,
                "timestamp": block.timestamp,
                "blockHash": block.hash
            }
        return {"verified": False, "reason": "Document not found in blockchain"}
    
    def to_dict(self):
        """Convert blockchain to dictionary"""
        return {
            "chain": [block.to_dict() for block in self.chain],
            "length": len(self.chain)
        }