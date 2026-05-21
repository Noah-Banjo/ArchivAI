import os
from services.ai.text_analysis import analyze_document


class AIService:

    def __init__(self):
        self.storage_path = os.getenv("STORAGE_PATH", "./storage")

    def process_document(self, document_id: str, file_path: str,
                         content_type: str | None = None, filename: str | None = None) -> dict:
        try:
            full_path = os.path.join(self.storage_path, file_path)
            analysis = analyze_document(full_path, content_type, filename=filename)
            return {
                "documentId": document_id,
                "aiGenerated": True,
                "textContent": analysis.get("text", ""),
                "entities": analysis.get("entities", []),
                "tags": analysis.get("tags", []),
                "summary": analysis.get("summary", ""),
                "language": analysis.get("language", "unknown"),
                "characterCount": analysis.get("characterCount", 0),
                "formatInfo": analysis.get("formatInfo", {}),
            }
        except Exception as e:
            print(f"AI processing error for {document_id}: {e}")
            return {"documentId": document_id, "aiGenerated": False, "error": str(e)}
