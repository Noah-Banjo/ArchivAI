import pymongo
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get MongoDB URI from environment variable
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/archivai")

def get_database():
    """Connect to MongoDB and return the database instance"""
    try:
        # Create a connection
        client = pymongo.MongoClient(MONGODB_URI)
        
        # Check connection
        client.admin.command('ping')
        print("MongoDB connection successful!")
        
        # Extract database name from URI
        if "mongodb+srv://" in MONGODB_URI:
            # Atlas connection string
            parts = MONGODB_URI.split("/")
            if len(parts) > 3:
                db_name = parts[3].split("?")[0]  # Handle query parameters
                if not db_name:
                    db_name = "archivai"
            else:
                db_name = "archivai"
        else:
            # Standard connection string
            db_name = MONGODB_URI.split("/")[-1]
            if not db_name or "?" in db_name:
                db_name = "archivai"
        
        print(f"Using database: {db_name}")
        return client[db_name]
    except Exception as e:
        print(f"Error connecting to MongoDB: {str(e)}")
        return None

def init_database():
    """Initialize database with required collections and indexes"""
    db = get_database()
    if db is None:
        return False
        
    try:
        # Create documents collection if it doesn't exist
        if "documents" not in db.list_collection_names():
            db.create_collection("documents")
        
        # Create indexes for better query performance
        db.documents.create_index("documentId", unique=True)
        db.documents.create_index("dateCreated")
        
        print("Database initialized successfully!")
        return True
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        return False