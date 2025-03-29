# ArchivAI: Blockchain and AI for Digital Preservation

This project demonstrates the integration of blockchain technology and artificial intelligence for digital archiving and preservation.

## Overview

ArchivAI leverages blockchain for document verification and AI for metadata extraction to create a trustworthy digital preservation system. The platform allows users to upload documents, which are then automatically processed to extract meaningful information and verified on a blockchain to ensure authenticity and immutability.

## Live Demo

Access the live application: [ArchivAI Demo](https://archivai-demo.onrender.com)

## Features

* **Document Upload and Storage**: Securely store documents with unique identifiers
* **AI-powered Metadata Extraction**: Automatically extract relevant information from documents
* **Intelligent Tag Generation**: Generate tags based on document content for easy categorization
* **Entity Recognition**: Automatically identify entities such as people, organizations, dates, emails, etc.
* **Document Summarization**: Create concise summaries of document content
* **Blockchain Verification**: Ensure document authenticity through immutable blockchain records
* **Processing Status Tracking**: Monitor the status of document processing in real-time
* **Search and Retrieval Capabilities**: Easily find documents based on their metadata

## Technology Stack

* **Backend**: Flask (Python) REST API
* **AI Processing**: NLTK for natural language processing and metadata extraction
* **Blockchain**: Custom blockchain implementation with cryptographic verification for document integrity
* **Database**: MongoDB Atlas for cloud-based metadata storage
* **Frontend**: Simple HTML/JavaScript interface for demonstration purposes

## API Documentation

### Base URL

```
https://archivai-demo.onrender.com
```

### Endpoints

#### Check API Status

```
GET /
```

Response:
```json
{
  "message": "Welcome to ArchivAI API"
}
```

#### Upload Document

```
POST /api/documents/upload-simple
```

Parameters:
- `file` (multipart/form-data): The document file to upload

Response:
```json
{
  "status": "success",
  "documentId": "f2c90c43-5684-4cba-b02d-9c0de5537a5a",
  "filename": "document.pdf",
  "path": "documents/f2c90c43-5684-4cba-b02d-9c0de5537a5a/document.pdf",
  "dateCreated": "2025-03-29T16:39:47.000Z"
}
```

#### Get All Documents

```
GET /api/documents
```

Response:
```json
{
  "status": "success",
  "count": 1,
  "documents": [
    {
      "documentId": "f2c90c43-5684-4cba-b02d-9c0de5537a5a",
      "filename": "document.pdf",
      "contentType": "application/pdf",
      "fileSize": 2432000,
      "dateCreated": "2025-03-29T16:39:47.000Z",
      "title": "document.pdf",
      "status": "processed",
      "tags": []
    }
  ]
}
```

#### Get Document Details

```
GET /api/documents/{documentId}
```

Response:
```json
{
  "status": "success",
  "document": {
    "documentId": "f2c90c43-5684-4cba-b02d-9c0de5537a5a",
    "filename": "document.pdf",
    "contentType": "application/pdf",
    "fileSize": 2432000,
    "dateCreated": "2025-03-05T23:51:56.000Z",
    "dateModified": "2025-03-05T23:51:57.000Z",
    "status": "processed",
    "tags": [],
    "aiMetadata": {
      "entities": [],
      "summary": "",
      "language": "unknown",
      "characterCount": 0
    },
    "blockchainVerification": {
      "status": "pending",
      "timestamp": "2025-03-05T23:51:56.000Z"
    }
  }
}
```

#### Verify Document on Blockchain

```
GET /api/documents/{documentId}/verify
```

Response:
```json
{
  "status": "success",
  "verified": true,
  "documentHash": "0xabcdef1234567890",
  "transactionId": "0x1234567890abcdef",
  "timestamp": "2025-03-05T23:51:56.000Z"
}
```

#### Get Blockchain Info

```
GET /api/blockchain/info
```

Response:
```json
{
  "status": "success",
  "chainLength": 12,
  "lastBlockHash": "0xabcdef1234567890",
  "verifiedDocuments": 8
}
```

## Usage Examples

### JavaScript

```javascript
// Upload a document
async function uploadDocument(file) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch('https://archivai-demo.onrender.com/api/documents/upload-simple', {
    method: 'POST',
    body: formData
  });
  
  return await response.json();
}

// Get all documents
async function getDocuments() {
  const response = await fetch('https://archivai-demo.onrender.com/api/documents');
  return await response.json();
}

// Get a specific document
async function getDocument(documentId) {
  const response = await fetch(`https://archivai-demo.onrender.com/api/documents/${documentId}`);
  return await response.json();
}
```

### Python

```python
import requests

# Upload a document
def upload_document(file_path):
    files = {'file': open(file_path, 'rb')}
    response = requests.post('https://archivai-demo.onrender.com/api/documents/upload-simple', files=files)
    return response.json()

# Get all documents
def get_documents():
    response = requests.get('https://archivai-demo.onrender.com/api/documents')
    return response.json()

# Get a specific document
def get_document(document_id):
    response = requests.get(f'https://archivai-demo.onrender.com/api/documents/{document_id}')
    return response.json()
```

## Installation

### Prerequisites

* Python 3.9+
* MongoDB Atlas account
* Git

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/Noah-Banjo/ArchivAI.git
   cd ArchivAI
   ```

2. Install dependencies:
   ```
   cd api
   pip install -r requirements.txt
   ```

3. Configure MongoDB:
   * Create a `.env` file in the `/api` directory
   * Add your MongoDB connection string:
     ```
     MONGODB_URI=mongodb+srv://yourusername:yourpassword@yourcluster.mongodb.net/archivai
     ```

4. Run the application:
   ```
   python app.py
   ```

5. Access the API at `http://localhost:8000`

### Using the Demo Interface

1. Open `demo/upload_test.html` in your browser, or
2. Visit the hosted interface at [ArchivAI Frontend](https://archivai-demo.onrender.com) 

## System Architecture

### Document Processing Flow

1. **Upload**: User uploads document through the API
2. **Storage**: Document is saved to storage with unique ID
3. **AI Processing**: Background thread processes document to extract metadata
   - Text extraction from various formats
   - Entity recognition
   - Summary generation
   - Language detection
   - Tag generation
4. **Blockchain Registration**: Document hash is calculated and registered on the blockchain
5. **Metadata Storage**: All metadata is stored in MongoDB Atlas
6. **Retrieval**: User can retrieve processed documents with all metadata

### Blockchain Implementation

The blockchain component provides:
- Document hash creation using SHA-256
- Immutable chain of document registration events
- Verification mechanism to prove document authenticity
- Timestamp proof of document existence

## Research Context

This prototype was developed for research on applying emerging technologies to archival science, specifically for the presentation "ArchivAI Revolution: Blockchain, AI and ML for Digital Preservation" at iPRES 2025.

## Future Improvements

- Add user authentication and access control
- Implement more sophisticated AI document analysis
- Add search functionality across document content
- Create a more robust frontend application
- Expand blockchain features for enhanced verification
- Add multi-language support for document processing

## Status

This project is deployed and functional for research and demonstration purposes.

## License

[MIT License](LICENSE)
