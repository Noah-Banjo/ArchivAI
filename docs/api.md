# ArchivAI API Documentation

## Endpoints

### Document Management

- `GET /api/documents`
  - **Description**: List all documents
  - **Response**: List of document metadata

- `GET /api/documents/{id}`
  - **Description**: Get document details
  - **Parameters**: `id` - Document ID
  - **Response**: Complete document metadata including AI analysis results

- `POST /api/documents/upload-simple`
  - **Description**: Upload a document
  - **Body**: Form data with 'file' field
  - **Response**: Document ID and basic information

### Blockchain Verification

- `GET /api/documents/{id}/verify`
  - **Description**: Verify document on blockchain
  - **Parameters**: `id` - Document ID
  - **Response**: Verification status and blockchain details

- `GET /api/blockchain/info`
  - **Description**: Get blockchain information
  - **Response**: Number of blocks, chain validity, latest block details