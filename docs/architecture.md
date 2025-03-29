# ArchivAI System Architecture

## Overview

ArchivAI implements a hybrid architecture that combines cloud-based metadata storage with local file storage, AI processing, and blockchain verification.

## Core Components

### 1. Document Management System
- **Flask API**: Provides RESTful endpoints for document operations
- **MongoDB Atlas**: Cloud database for storing document metadata
- **Local Storage**: File system storage for actual document content

### 2. AI Analysis Engine
- **Text Extraction**: Extracts text from various document formats
- **Entity Recognition**: Identifies key entities like dates, emails, etc.
- **Tag Generation**: Creates relevant tags based on document content
- **Summary Generation**: Produces concise document summaries

### 3. Blockchain Verification System
- **Document Hashing**: Creates cryptographic hashes of documents
- **Blockchain Registry**: Records document hashes in an immutable ledger
- **Verification Service**: Verifies document authenticity against blockchain records

## Data Flow

1. **Document Upload**:
   - Client uploads document → API saves file → Document metadata created in MongoDB
   - Background process triggers AI analysis
   - Background process registers document on blockchain

2. **AI Processing**:
   - Document processed for text extraction
   - Text analyzed for entities, topics, and summary
   - Metadata updated in MongoDB with AI results

3. **Blockchain Verification**:
   - Document hash calculated
   - Hash registered on blockchain
   - Verification status updated in metadata