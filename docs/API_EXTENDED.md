# ArchivAI API Documentation

This document provides detailed information about the ArchivAI API endpoints, request/response formats, and usage examples.

## Base URL

```
https://archivai-demo.onrender.com
```

For local development:
```
http://localhost:8000
```

## Authentication

The current prototype does not implement authentication. Future versions will include JWT-based authentication and role-based access control.

## API Endpoints

### System Status

#### Check API Status

Verifies that the API is running and available.

- **URL**: `/`
- **Method**: `GET`
- **Response**: 

```json
{
  "message": "Welcome to ArchivAI API",
  "status": "success",
  "version": "1.0.0"
}
```

### Document Management

#### Upload Document

Uploads a document to the system for AI processing and blockchain verification.

- **URL**: `/api/documents/upload-simple`
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`
- **Parameters**:
  - `file` (required): The document file to upload

- **Response**: 

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

Retrieves a list of all documents in the system.

- **URL**: `/api/documents`
- **Method**: `GET`
- **Query Parameters**:
  - `limit` (optional): Maximum number of documents to return (default: 100)
  - `offset` (optional): Number of documents to skip (default: 0)
  - `status` (optional): Filter by processing status (values: "pending", "processing", "processed", "failed")

- **Response**: 

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

Retrieves detailed information about a specific document.

- **URL**: `/api/documents/{documentId}`
- **Method**: `GET`
- **URL Parameters**:
  - `documentId` (required): The unique identifier of the document

- **Response**: 

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
    "tags": ["research", "digital preservation", "blockchain"],
    "aiMetadata": {
      "entities": [
        {
          "type": "person",
          "value": "John Smith",
          "confidence": 0.87
        },
        {
          "type": "organization",
          "value": "University of Arkansas",
          "confidence": 0.92
        },
        {
          "type": "date",
          "value": "2025-01-15",
          "confidence": 0.98
        }
      ],
      "summary": "This document discusses digital preservation approaches using blockchain technology and artificial intelligence.",
      "language": "en",
      "characterCount": 24560
    },
    "blockchainVerification": {
      "status": "verified",
      "timestamp": "2025-03-05T23:51:56.000Z",
      "hash": "0xabcdef1234567890",
      "transactionId": "0x1234567890abcdef"
    }
  }
}
```

#### Verify Document on Blockchain

Verifies the authenticity of a document using blockchain.

- **URL**: `/api/documents/{documentId}/verify`
- **Method**: `GET`
- **URL Parameters**:
  - `documentId` (required): The unique identifier of the document

- **Response**: 

```json
{
  "status": "success",
  "verified": true,
  "documentHash": "0xabcdef1234567890",
  "transactionId": "0x1234567890abcdef",
  "timestamp": "2025-03-05T23:51:56.000Z"
}
```

### Blockchain Information

#### Get Blockchain Info

Retrieves information about the blockchain system.

- **URL**: `/api/blockchain/info`
- **Method**: `GET`
- **Response**: 

```json
{
  "status": "success",
  "chainLength": 12,
  "lastBlockHash": "0xabcdef1234567890",
  "verifiedDocuments": 8
}
```

## Error Handling

All endpoints follow a consistent error response format:

```json
{
  "status": "error",
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message"
  }
}
```

Common error codes:

| Code | Description |
|------|-------------|
| `DOCUMENT_NOT_FOUND` | The requested document does not exist |
| `INVALID_DOCUMENT_ID` | The document ID format is invalid |
| `FILE_TOO_LARGE` | The uploaded file exceeds the size limit |
| `UNSUPPORTED_FILE_TYPE` | The file type is not supported |
| `BLOCKCHAIN_ERROR` | Error communicating with the blockchain |
| `INTERNAL_SERVER_ERROR` | Unexpected server error |

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

// Verify a document
async function verifyDocument(documentId) {
  const response = await fetch(`https://archivai-demo.onrender.com/api/documents/${documentId}/verify`);
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

# Verify a document
def verify_document(document_id):
    response = requests.get(f'https://archivai-demo.onrender.com/api/documents/{document_id}/verify')
    return response.json()
```

## Rate Limiting

The API enforces rate limiting to prevent abuse:

- 100 requests per minute per IP address
- 1000 requests per day per IP address

Exceeding these limits will result in a `429 Too Many Requests` response.

## Future API Enhancements

The following enhancements are planned for future API versions:

1. User authentication and authorization
2. Advanced search functionality
3. Batch document processing
4. Webhooks for processing status notifications
5. Document update and deletion capabilities

## Support

For API support or to report issues, please contact:

- Email (Not functioning yet): support@archivai.example.com
- GitHub Issues: https://github.com/Noah-Banjo/ArchivAI/issues
