import os
import hashlib
from services.blockchain.simulated_blockchain import Blockchain

# Global blockchain instance
_blockchain = Blockchain()

class BlockchainService:
    """Service for blockchain interactions"""
    
    def __init__(self):
        """Initialize the blockchain service"""
        self.blockchain = _blockchain
        self.storage_path = os.getenv("STORAGE_PATH", "./storage")
    
    def calculate_file_hash(self, file_path):
        """Calculate SHA-256 hash of a file
        
        Args:
            file_path: Full path to the file
            
        Returns:
            SHA-256 hash as a hex string
        """
        try:
            sha256_hash = hashlib.sha256()
            
            with open(file_path, "rb") as f:
                # Read and update hash in chunks of 4K
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
                    
            return sha256_hash.hexdigest()
        except Exception as e:
            print(f"Error calculating file hash: {str(e)}")
            return None
    
    def register_document(self, document_id, file_path, metadata=None):
        """Register a document on the blockchain
        
        Args:
            document_id: Document ID
            file_path: Path to the document file
            metadata: Additional metadata about the document
            
        Returns:
            Dict containing transaction details
        """
        try:
            # Calculate document hash
            full_path = os.path.join(self.storage_path, file_path)
            document_hash = self.calculate_file_hash(full_path)
            
            if not document_hash:
                return {
                    "status": "error",
                    "message": "Could not calculate document hash"
                }
            
            # Prepare blockchain data
            data = {
                "documentId": document_id,
                "documentHash": document_hash,
                "metadata": metadata or {}
            }
            
            # Add to blockchain
            new_block = self.blockchain.add_block(data)
            
            return {
                "status": "success",
                "transactionId": new_block.hash,
                "blockIndex": new_block.index,
                "timestamp": new_block.timestamp,
                "documentHash": document_hash
            }
        except Exception as e:
            print(f"Error registering document on blockchain: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def verify_document(self, document_id, file_path=None):
        """Verify a document's authenticity on the blockchain
        
        Args:
            document_id: Document ID
            file_path: Optional path to recalculate the hash
            
        Returns:
            Dict containing verification results
        """
        try:
            # If file path is provided, recalculate hash
            document_hash = None
            if file_path:
                full_path = os.path.join(self.storage_path, file_path)
                document_hash = self.calculate_file_hash(full_path)
            
            # Query blockchain for verification
            if document_hash:
                verification = self.blockchain.verify_document(document_id, document_hash)
            else:
                # Get the block with this document ID
                block = self.blockchain.get_block_by_document_id(document_id)
                verification = {
                    "verified": block is not None,
                    "blockIndex": block.index if block else None,
                    "timestamp": block.timestamp if block else None,
                    "blockHash": block.hash if block else None,
                    "documentHash": block.data.get("documentHash") if block else None
                } if block else {"verified": False, "reason": "Document not found in blockchain"}
            
            return {
                "status": "success",
                "documentId": document_id,
                "verification": verification
            }
        except Exception as e:
            print(f"Error verifying document on blockchain: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "documentId": document_id
            }
    
    def get_blockchain_info(self):
        """Get information about the blockchain
        
        Returns:
            Dict containing blockchain info
        """
        return {
            "status": "success",
            "blockchainInfo": {
                "blocks": len(self.blockchain.chain),
                "isValid": self.blockchain.is_chain_valid(),
                "latestBlock": self.blockchain.get_latest_block().to_dict()
            }
        }