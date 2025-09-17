from langchain.document_loaders import (
    TextLoader,
    DirectoryLoader,
    UnstructuredMarkdownLoader,
    UnstructuredHTMLLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
import logging
from pathlib import Path
from typing import List, Optional
from tqdm import tqdm
import os

from .config import settings
from .utils import handle_api_error, validate_api_key, logger

SUPPORTED_EXTENSIONS = {
    '.txt': TextLoader,
    '.md': UnstructuredMarkdownLoader,
    '.html': UnstructuredHTMLLoader,
    '.htm': UnstructuredHTMLLoader
}

def get_loader_for_file(file_path: str):
    """Get the appropriate loader for a file based on its extension"""
    ext = os.path.splitext(file_path)[1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file extension: {ext}")
    return SUPPORTED_EXTENSIONS[ext]

def load_documents(docs_path: str) -> List:
    """Load documents from a file or directory"""
    path = Path(docs_path)
    
    if path.is_file():
        logger.info(f"Loading single file: {docs_path}")
        loader = get_loader_for_file(docs_path)
        return loader(docs_path).load()
    
    elif path.is_dir():
        logger.info(f"Loading directory: {docs_path}")
        loaders = []
        for ext, loader_class in SUPPORTED_EXTENSIONS.items():
            loaders.append(
                DirectoryLoader(
                    docs_path,
                    glob=f"**/*{ext}",
                    loader_cls=loader_class
                )
            )
        
        all_docs = []
        for loader in loaders:
            try:
                all_docs.extend(loader.load())
            except Exception as e:
                logger.warning(f"Error loading documents with {loader.__class__.__name__}: {str(e)}")
        return all_docs
    
    else:
        raise FileNotFoundError(f"Path not found: {docs_path}")

def index_documents(
    docs_path: str = "docs/wordpress_docs.txt",
    chunk_size: Optional[int] = None,
    chunk_overlap: Optional[int] = None
) -> None:
    """
    Index documents into ChromaDB
    Args:
        docs_path: Path to the documentation file or directory
        chunk_size: Optional override for chunk size
        chunk_overlap: Optional override for chunk overlap
    """
    try:
        # Validate API key
        validate_api_key(settings.OPENAI_API_KEY)

        # Check if path exists
        if not Path(docs_path).exists():
            raise FileNotFoundError(f"Path not found: {docs_path}")

        # Load and process documents
        logger.info(f"Loading documents from {docs_path}")
        raw_docs = load_documents(docs_path)
        
        if not raw_docs:
            raise ValueError("No documents found to index")

        # Split documents
        logger.info("Splitting documents into chunks")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size or settings.CHUNK_SIZE,
            chunk_overlap=chunk_overlap or settings.CHUNK_OVERLAP
        )
        docs = text_splitter.split_documents(raw_docs)

        # Create and persist vector store
        logger.info("Creating vector store")
        vectordb = Chroma.from_documents(
            docs,
            OpenAIEmbeddings(),
            persist_directory=settings.CHROMA_PERSIST_DIRECTORY
        )
        vectordb.persist()
        logger.info(f"Successfully indexed {len(docs)} chunks from {len(raw_docs)} documents")

    except Exception as e:
        handle_api_error(e)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Index documents for the RAG system")
    parser.add_argument("--path", default="docs/wordpress_docs.txt", help="Path to document or directory")
    parser.add_argument("--chunk-size", type=int, help="Override default chunk size")
    parser.add_argument("--chunk-overlap", type=int, help="Override default chunk overlap")
    
    args = parser.parse_args()
    index_documents(args.path, args.chunk_size, args.chunk_overlap) 