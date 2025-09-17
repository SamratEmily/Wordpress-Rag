from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from ..core.config import settings
import logging

logger = logging.getLogger(__name__)

def init_chroma():
    """Initialize ChromaDB with OpenAI embeddings"""
    try:
        # Initialize embeddings
        embeddings = OpenAIEmbeddings()
        
        # Initialize ChromaDB
        vectordb = Chroma(
            persist_directory=settings.CHROMA_PERSIST_DIRECTORY,
            embedding_function=embeddings
        )
        
        logger.info(f"ChromaDB initialized at {settings.CHROMA_PERSIST_DIRECTORY}")
        return vectordb
    except Exception as e:
        logger.error(f"Failed to initialize ChromaDB: {str(e)}")
        raise

def test_chroma():
    """Test ChromaDB connection and functionality"""
    try:
        vectordb = init_chroma()
        
        # Test adding a document
        test_text = "This is a test document for ChromaDB"
        vectordb.add_texts([test_text])
        
        # Test similarity search
        results = vectordb.similarity_search("test document", k=1)
        
        logger.info("ChromaDB test successful")
        return True
    except Exception as e:
        logger.error(f"ChromaDB test failed: {str(e)}")
        return False

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Test ChromaDB
    if test_chroma():
        print("ChromaDB setup successful!")
    else:
        print("ChromaDB setup failed!") 