from services.blockchain_service import BlockchainService
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import uuid
import threading
from datetime import datetime
from dotenv import load_dotenv
from database.mongodb import get_database, init_database
from services.ai_service import AIService

# Load environment variables from .env file
load_dotenv()

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize services
ai_service = AIService()
blockchain_service = BlockchainService()

# Create storage directory
os.makedirs("./storage", exist_ok=True)

# Initialize database
init_database()

# Background processing function for AI
def process_document_with_ai(document_id, file_path, content_type):
    """Process a document with AI in the background"""
    try:
        # Get MongoDB database
        db = get_database()
        if db is None:
            print("Database connection failed during AI processing")
            return
        
        # Process with AI
        ai_results = ai_service.process_document(document_id, file_path, content_type)
        
        # Update document metadata with AI results
        db.documents.update_one(
            {"documentId": document_id},
            {
                "$set": {
                    "status": "processed",
                    "dateModified": datetime.now().isoformat(),
                    "tags": ai_results.get("tags", []),
                    "aiMetadata": {
                        "entities": ai_results.get("entities", []),
                        "summary": ai_results.get("summary", ""),
                        "language": ai_results.get("language", "unknown"),
                        "characterCount": ai_results.get("characterCount", 0)
                    }
                }
            }
        )
        
        print(f"AI processing completed for document {document_id}")
        
        # Process with blockchain after AI processing
        process_document_with_blockchain(document_id, file_path)
    except Exception as e:
        print(f"Error in background AI processing: {str(e)}")
        
        # Update status to reflect error
        if 'db' in locals() and db:
            db.documents.update_one(
                {"documentId": document_id},
                {
                    "$set": {
                        "status": "error",
                        "processingError": str(e)
                    }
                }
            )

# Background processing function for blockchain
def process_document_with_blockchain(document_id, file_path):
    """Register a document on the blockchain in the background"""
    try:
        # Get MongoDB database
        db = get_database()
        if db is None:
            print("Database connection failed during blockchain processing")
            return
        
        # Register document on blockchain
        blockchain_result = blockchain_service.register_document(
            document_id=document_id,
            file_path=file_path
        )
        
        # Update document metadata with blockchain results
        if blockchain_result["status"] == "success":
            db.documents.update_one(
                {"documentId": document_id},
                {
                    "$set": {
                        "blockchainVerification": {
                            "status": "verified",
                            "transactionId": blockchain_result.get("transactionId", ""),
                            "timestamp": blockchain_result.get("timestamp", ""),
                            "documentHash": blockchain_result.get("documentHash", "")
                        }
                    }
                }
            )
            
            print(f"Blockchain registration completed for document {document_id}")
        else:
            db.documents.update_one(
                {"documentId": document_id},
                {
                    "$set": {
                        "blockchainVerification": {
                            "status": "error",
                            "errorMessage": blockchain_result.get("message", "Unknown error"),
                            "timestamp": datetime.now().isoformat()
                        }
                    }
                }
            )
            
            print(f"Blockchain registration failed for document {document_id}")
    except Exception as e:
        print(f"Error in background blockchain processing: {str(e)}")

# Root endpoint
@app.route('/')
def home():
    return jsonify({"message": "Welcome to ArchivAI API"})

# Upload test endpoint
@app.route('/api/upload-test', methods=['POST'])
def upload_test():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    return jsonify({
        "filename": file.filename,
        "content_type": file.content_type,
        "size": None  # Flask doesn't provide file size directly
    })

# Document upload with MongoDB and AI processing
@app.route('/api/documents/upload-simple', methods=['POST'])
def upload_document():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    try:
        # Get MongoDB database
        db = get_database()
        if db is None:
            return jsonify({"error": "Database connection failed"}), 500
        
        # Generate a unique ID
        document_id = str(uuid.uuid4())
        
        # Create the directory structure
        directory = f"./storage/documents/{document_id}"
        os.makedirs(directory, exist_ok=True)
        
        # Save the file
        file_path = os.path.join(directory, file.filename)
        file.save(file_path)
        
        # Create document metadata
        current_time = datetime.now().isoformat()
        metadata = {
            "documentId": document_id,
            "filename": file.filename,
            "path": f"documents/{document_id}/{file.filename}",
            "contentType": file.content_type or "application/octet-stream",
            "fileSize": os.path.getsize(file_path),
            "dateCreated": current_time,
            "dateModified": current_time,
            "status": "uploading",  # Will be updated to "processed" after AI processing
            "title": file.filename,  # Default title is filename
            "description": "",
            "tags": [],
            "blockchainVerification": {
                "status": "pending",
                "timestamp": current_time
            }
        }
        
        # Insert document metadata into MongoDB
        db.documents.insert_one(metadata)
        
        # Process with AI in the background
        processing_thread = threading.Thread(
            target=process_document_with_ai,
            args=(document_id, f"documents/{document_id}/{file.filename}", file.content_type)
        )
        processing_thread.daemon = True
        processing_thread.start()
        
        # Return information
        return jsonify({
            "status": "success",
            "documentId": document_id,
            "filename": file.filename,
            "path": f"documents/{document_id}/{file.filename}",
            "dateCreated": current_time
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get all documents
@app.route('/api/documents', methods=['GET'])
def get_documents():
    try:
        # Get MongoDB database
        db = get_database()
        if db is None:
            return jsonify({"error": "Database connection failed"}), 500
        
        # Query documents
        documents = list(db.documents.find({}, {
            "_id": 0,  # Exclude MongoDB _id field
            "documentId": 1,
            "filename": 1,
            "contentType": 1,
            "fileSize": 1,
            "dateCreated": 1,
            "title": 1,
            "status": 1,
            "tags": 1
        }))
        
        return jsonify({
            "status": "success",
            "count": len(documents),
            "documents": documents
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get document by ID
@app.route('/api/documents/<document_id>', methods=['GET'])
def get_document(document_id):
    try:
        # Get MongoDB database
        db = get_database()
        if db is None:
            return jsonify({"error": "Database connection failed"}), 500
        
        # Query document
        document = db.documents.find_one({"documentId": document_id}, {"_id": 0})
        
        if document is None:
            return jsonify({"error": "Document not found"}), 404
        
        return jsonify({
            "status": "success",
            "document": document
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get blockchain info
@app.route('/api/blockchain/info', methods=['GET'])
def get_blockchain_info():
    try:
        info = blockchain_service.get_blockchain_info()
        return jsonify(info)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Verify document on blockchain
@app.route('/api/documents/<document_id>/verify', methods=['GET'])
def verify_document_on_blockchain(document_id):
    try:
        # Get MongoDB database
        db = get_database()
        if db is None:
            return jsonify({"error": "Database connection failed"}), 500
        
        # Get document
        document = db.documents.find_one({"documentId": document_id}, {"_id": 0})
        if not document:
            return jsonify({"error": "Document not found"}), 404
        
        # Verify document
        verification = blockchain_service.verify_document(
            document_id=document_id,
            file_path=document.get("path")
        )
        
        return jsonify(verification)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the app
if __name__ == '__main__':
    app.run(debug=True, port=8000)