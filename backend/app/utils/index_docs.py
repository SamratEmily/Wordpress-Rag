from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import DirectoryLoader, TextLoader
from .chroma_setup import init_chroma
import logging
from ..core.config import settings

logger = logging.getLogger(__name__)

def load_documents(docs_dir: str):
    """Load documents from directory"""
    try:
        loader = DirectoryLoader(
            docs_dir,
            glob="**/*.txt",  # Adjust pattern based on your document types
            loader_cls=TextLoader
        )
        documents = loader.load()
        logger.info(f"Loaded {len(documents)} documents from {docs_dir}")
        return documents
    except Exception as e:
        logger.error(f"Failed to load documents: {str(e)}")
        raise

def split_documents(documents):
    """Split documents into chunks"""
    try:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )
        chunks = text_splitter.split_documents(documents)
        logger.info(f"Split documents into {len(chunks)} chunks")
        return chunks
    except Exception as e:
        logger.error(f"Failed to split documents: {str(e)}")
        raise

def index_documents(docs_dir: str):
    """Index documents into ChromaDB"""
    try:
        # Initialize ChromaDB
        vectordb = init_chroma()
        
        # Load and split documents
        documents = load_documents(docs_dir)
        chunks = split_documents(documents)
        
        # Add documents to ChromaDB
        vectordb.add_documents(chunks)
        vectordb.persist()
        
        logger.info("Documents indexed successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to index documents: {str(e)}")
        return False

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Index documents
    docs_dir = "docs"  # Adjust path to your documentation directory
    if index_documents(docs_dir):
        print("Document indexing successful!")
    else:
        print("Document indexing failed!") 