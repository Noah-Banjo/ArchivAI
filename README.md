# ArchivAI: Blockchain, AI, and ML for Digital Preservation

ArchivAI is a revolutionary framework that integrates blockchain technology and artificial intelligence for digital archiving and preservation. The platform leverages blockchain for document verification and AI for metadata extraction to create a trustworthy digital preservation system.

## 🌟 Overview

Digital archives today face three critical challenges:
1. **Authentication**: How to verify the authenticity of digital objects in an era of deepfakes and AI-generated content
2. **Resource Limitations**: Managing overwhelming content volume with limited staff and funding
3. **Preservation Silos**: Disconnected systems that complicate consistent authentication

ArchivAI addresses these challenges by integrating blockchain and AI technologies. Our approach is unique because AI plays a direct role in verification - when the system extracts text, identifies entities, generates tags, and creates summaries, these actions become cryptographically verifiable on a blockchain.

## 🏗️ System Architecture

![System Architecture Diagram](images/archivai-system-architecture.png)


ArchivAI consists of five interconnected layers:
- **User Interface Layer**: Tailored interfaces for users, experts, and administrators
- **API Layer**: Manages all interactions between users and backend systems
- **Processing Layers**: 
  - AI Processing Pipeline for content analysis and metadata extraction
  - Blockchain Layer for verification and immutable record-keeping
- **Integration Point**: Where AI-generated data becomes part of blockchain transactions
- **Storage Layer**: Maintains documents, metadata, and blockchain records

## ✨ Features

- **Document Upload and Storage**: Securely store documents with unique identifiers
- **AI-powered Metadata Extraction**: Automatically extract relevant information from documents
- **Intelligent Tag Generation**: Generate tags based on document content for easy categorization
- **Entity Recognition**: Automatically identify entities such as people, organizations, dates, emails, etc.
- **Document Summarization**: Create concise summaries of document content
- **Blockchain Verification**: Ensure document authenticity through immutable blockchain records
- **Processing Status Tracking**: Monitor the status of document processing in real-time
- **Search and Retrieval Capabilities**: Easily find documents based on their metadata

## 🛠️ Technology Stack

- **Backend**: Flask (Python) REST API
- **AI Processing**: NLTK for natural language processing and metadata extraction
- **Blockchain**: Custom blockchain implementation with cryptographic verification for document integrity
- **Database**: MongoDB Atlas for cloud-based metadata storage
- **Frontend**: Simple HTML/JavaScript interface for demonstration purposes

## 🧪 Demo

*Coming soon: Screenshots of the application interface and demo video*

Here is the demo video of how to install and use the app:  https://youtu.be/AlkG2o08i7I   **(💡 Tip: Set video quality to 1080p for best viewing (click the gear icon))**

## 📋 Installation and Setup

### Prerequisites
- Python 3.9+
- MongoDB Atlas account
- Git

### Setup Instructions

1. Clone the repository:
```bash
git clone https://github.com/Noah-Banjo/ArchivAI.git
cd ArchivAI
```

2. Install dependencies:
```bash
cd api
pip install -r requirements.txt
```

3. Configure MongoDB:
   - Create a `.env` file in the `/api` directory
   - Add your MongoDB connection string:
   ```
   MONGODB_URI=mongodb+srv://yourusername:yourpassword@yourcluster.mongodb.net/archivai
   ```

4. Run the application:
```bash
python app.py
```

5. Access the API at http://localhost:8000

## 🌐 API Documentation

### Base URL
```
https://archivai-demo.onrender.com
```

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Check API Status |
| `/api/documents/upload-simple` | POST | Upload Document |
| `/api/documents` | GET | Get All Documents |
| `/api/documents/{documentId}` | GET | Get Document Details |
| `/api/documents/{documentId}/verify` | GET | Verify Document on Blockchain |
| `/api/blockchain/info` | GET | Get Blockchain Info |

For complete API documentation, please see our [API Documentation](docs/API_EXTENDED.md) page.

## 🔍 Use Cases

ArchivAI is particularly valuable for:

- **Historical Archives**: Preserving cultural heritage with verifiable authenticity
- **Legal Records**: Maintaining chain of custody for legal documents
- **Research Repositories**: Ensuring data integrity and provenance
- **Corporate Archives**: Simplifying compliance and records management
- **Digital Libraries**: Enhancing metadata and discovery while ensuring authenticity

## 🚀 Development Roadmap

We're actively working on enhancing ArchivAI with:

- **Enhanced AI capabilities**: More sophisticated natural language processing, OCR, speech-to-text, and computer vision
- **Full blockchain implementation**: Moving from our simulated proof-of-concept to a properly distributed blockchain system
- **Cross-institutional implementation**: Extending the system across multiple archives
- **Preservation-focused machine learning**: Developing AI specifically for digital preservation needs
- **Performance evaluation**: Formal testing to quantify efficiency improvements

## 👥 Team

- **[Oluseyi Noah Adebanjo](https://orcid.org/0009-0002-6367-5999)** - Center for Arkansas History and Culture, United States
- **[Anuoluwapo Victoria Alabi](https://orcid.org/0009-0002-3641-3977)** - Prairie View A&M University, United States
- **[Oyeleke Onaolapo Bolaji](https://orcid.org/0009-0009-0871-7333)** - Yaşar Üniversitesi, Turkey

## 🤝 Contributing

We welcome contributions to ArchivAI! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please see our [Contributing Guidelines](CONTRIBUTING.md) for more details.

## ❓ Possibly Asked Questions

**Q: How does ArchivAI compare to traditional digital preservation approaches?**  
A: ArchivAI enhances traditional approaches by adding blockchain verification for authenticity and AI processing for efficient metadata extraction, addressing both trust and efficiency concerns simultaneously.

**Q: What types of documents can ArchivAI process?**  
A: Currently, ArchivAI can process text-based documents. Support for images, audio, and video is planned for future releases.

**Q: Is ArchivAI suitable for small archives with limited technical expertise?**  
A: While the current prototype requires some technical knowledge to set up, we're working on making the system more accessible for organizations with varying levels of technical expertise.

**Q: How does the blockchain verification work without high energy consumption?**  
A: We use a permissioned blockchain model that avoids resource-intensive "mining," making it more energy-efficient than cryptocurrency blockchains.

## 📚 Citation Information

If you use ArchivAI in your research, please cite our paper:

```
Adebanjo, O. N., Alabi, A. V., & Bolaji, O. O. (2025). ArchivAI Revolution: Pioneering the Fusion of Blockchain, AI, and ML for Digital Preservation. In Proceedings of the 21st International Conference on Digital Preservation (iPRES 2025), Wellington, Aotearoa New Zealand.
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

The authors would like to acknowledge the Center for Arkansas History and Culture (CAHC) for the training and exposure that significantly contributed to our professional growth and the development of this project. Special thanks to Amanda McQueen, Elise Tanner, and Brigitte Billeaudeaux for their support and resources.
