import os
from services.ai.text_analysis import analyze_document

class AIService:
    """Service for AI processing of documents"""
    
    def __init__(self):
        """Initialize the AI service"""
        self.storage_path = os.getenv("STORAGE_PATH", "./storage")
    
    def process_document(self, document_id, file_path, content_type=None):
        """Process a document with AI
        
        Args:
            document_id: Document ID
            file_path: Path to the document file
            content_type: MIME type of the document
            
        Returns:
            Dict containing AI-generated metadata
        """
        try:
            # Create full path
            full_path = os.path.join(self.storage_path, file_path)
            
            # Analyze document
            analysis = analyze_document(full_path, content_type)
            
            # Return analysis results
            return {
                "documentId": document_id,
                "aiGenerated": True,
                "textContent": analysis.get("text", ""),
                "entities": analysis.get("entities", []),
                "tags": analysis.get("tags", []),
                "summary": analysis.get("summary", ""),
                "language": analysis.get("language", "unknown"),
                "characterCount": analysis.get("characterCount", 0)
            }
        except Exception as e:
            print(f"Error processing document with AI: {str(e)}")
            return {
                "documentId": document_id,
                "aiGenerated": False,
                "error": str(e)
            }