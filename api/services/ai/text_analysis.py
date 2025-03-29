import os
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist
import PyPDF2

# Ensure NLTK data is downloaded
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file"""
    try:
        text = ""
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {str(e)}")
        return ""

def extract_text_from_file(file_path, content_type=None):
    """Extract text from a file based on its content type"""
    if not os.path.exists(file_path):
        return ""
    
    ext = os.path.splitext(file_path)[1].lower()
    
    # Handle PDFs
    if ext == '.pdf' or (content_type and 'pdf' in content_type):
        return extract_text_from_pdf(file_path)
    
    # Handle text files
    if ext in ['.txt', '.md', '.csv', '.html'] or (content_type and 'text' in content_type):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    return file.read()
            except Exception as e:
                print(f"Error reading text file: {str(e)}")
                return ""
    
    # For other files, return empty text
    return ""

def extract_simple_entities(text):
    """Extract simple entities like emails, dates, etc."""
    entities = []
    
    # Extract email addresses
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    for email in emails:
        entities.append({
            "text": email,
            "type": "EMAIL",
            "confidence": 0.9
        })
    
    # Extract dates (simple pattern)
    date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'
    dates = re.findall(date_pattern, text)
    for date in dates:
        entities.append({
            "text": date,
            "type": "DATE",
            "confidence": 0.8
        })
    
    return entities

def generate_tags(text, max_tags=8):
    """Generate tags from text content"""
    if not text:
        return []
    
    # Tokenize text
    tokens = word_tokenize(text.lower())
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [token for token in tokens if token.isalpha() and token not in stop_words and len(token) > 3]
    
    # Count word frequencies
    freq_dist = FreqDist(filtered_tokens)
    
    # Get most common words as tags
    tags = [word for word, freq in freq_dist.most_common(max_tags)]
    
    return tags

def analyze_document(file_path, content_type=None):
    """Analyze a document and extract metadata"""
    # Extract text (only for text-based files)
    text = extract_text_from_file(file_path, content_type)
    
    # If no text was extracted (likely an image or binary file)
    if not text:
        # Just return basic info based on file type
        ext = os.path.splitext(file_path)[1].lower()
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
            return {
                "text": "",
                "entities": [],
                "tags": ["image", ext[1:], "visual"],
                "summary": "Image file - no text extracted",
                "language": "unknown",
                "characterCount": 0
            }
        return {
            "text": "",
            "entities": [],
            "tags": [ext[1:] if ext else "unknown"],
            "summary": "No text content extracted",
            "language": "unknown",
            "characterCount": 0
        }
    
    # Process extracted text
    entities = extract_simple_entities(text)
    tags = generate_tags(text)
    
    # Create summary (simple first few characters)
    summary = text[:250] + "..." if len(text) > 250 else text
    
    return {
        "text": text[:1000] + "..." if len(text) > 1000 else text,
        "entities": entities,
        "tags": tags,
        "summary": summary,
        "language": "en",  # Default to English
        "characterCount": len(text)
    }