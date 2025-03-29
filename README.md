# ArchivAI: Blockchain and AI for Digital Preservation

This project demonstrates the integration of blockchain technology and artificial intelligence for digital archiving and preservation.

## Overview

ArchivAI leverages blockchain for document verification and AI for metadata extraction to create a trustworthy digital preservation system.

## Features

- Document upload and storage
- AI-powered metadata extraction and tag generation
- Automatic entity recognition (emails, dates, etc.)
- Document summarization
- Blockchain verification of document authenticity
- Search and retrieval capabilities

## Technology Stack

- Backend: Flask (Python)
- AI Processing: NLTK for natural language processing
- Blockchain: Custom blockchain implementation with cryptographic verification
- Database: MongoDB Atlas for cloud storage
- Frontend: Simple HTML demo interface

## Installation

### Prerequisites
- Python 3.9+
- MongoDB Atlas account
- Git

### Setup
1. Clone the repository:
git clone https://github.com/Noah-Banjo/ArchivAI.git
cd ArchivAI

2. Install dependencies:
cd api
pip install -r requirements.txt

3. Configure MongoDB:
- Create a `.env` file in the `/api` directory
- Add your MongoDB connection string:
  ```
  MONGODB_URI=mongodb+srv://yourusername:yourpassword@yourcluster.mongodb.net/archivai
  ```

4. Run the application:
python app.py

5. Open the demo interface:
- Open `demo/upload_test.html` in your browser

## API Documentation

The API provides endpoints for document management and blockchain verification. See `docs/api.md` for complete documentation.

## Research Context

This prototype was developed for research on applying emerging technologies to archival science, specifically for the presentation "ArchivAI Revolution: Blockchain, AI and ML for Digital Preservation" at iPRES 2025.

## Status

This project is currently under development for research purposes.
