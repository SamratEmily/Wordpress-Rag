from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from typing import Optional, Dict, Any, List
import logging
import os
import uuid
from pathlib import Path
from ..core.config import settings

logger = logging.getLogger(__name__)

class RAGService:
    """Enhanced RAG service with document ingestion and relevance filtering"""
    
    def __init__(self):
        """Initialize RAG components"""
        self.relevance_threshold = 0.7  # Minimum relevance score to provide answer
        self._initialize_components()
    
    def _initialize_components(self) -> None:
        """Initialize and validate RAG components"""
        try:
            self.embedding = OpenAIEmbeddings()
            self.vectordb = Chroma(
                persist_directory=settings.CHROMA_PERSIST_DIRECTORY,
                embedding_function=self.embedding
            )
            
            # Configure retriever with similarity threshold
            self.retriever = self.vectordb.as_retriever(
                search_type="similarity_score_threshold",
                search_kwargs={"score_threshold": self.relevance_threshold, "k": 5}
            )
            
            self.llm = ChatOpenAI(
                model_name=settings.MODEL_NAME,
                temperature=settings.TEMPERATURE,
                max_tokens=settings.MAX_TOKENS
            )
            
            # Create text splitter for document processing
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=settings.CHUNK_SIZE,
                chunk_overlap=settings.CHUNK_OVERLAP,
                length_function=len,
            )
            
            # Custom prompt for relevance checking
            self.relevance_prompt = PromptTemplate(
                input_variables=["context", "question"],
                template="""
                Based on the following context, determine if the question can be answered accurately.
                If the context contains relevant information to answer the question, respond with "RELEVANT".
                If the context does not contain enough information to answer the question, respond with "NOT_RELEVANT".
                
                Context: {context}
                Question: {question}
                
                Response (RELEVANT or NOT_RELEVANT):
                """
            )
            
            logger.info("RAG components initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize RAG components: {str(e)}")
            raise
    
    async def add_documents(self, documents: List[Document]) -> Dict[str, Any]:
        """
        Add documents to the vector store
        
        Args:
            documents: List of Document objects to add
            
        Returns:
            Dict containing the result of the operation
        """
        try:
            if not documents:
                return {"success": False, "message": "No documents provided"}
            
            # Split documents into chunks
            chunks = self.text_splitter.split_documents(documents)
            
            # Add metadata to chunks
            for i, chunk in enumerate(chunks):
                chunk.metadata.update({
                    "chunk_id": str(uuid.uuid4()),
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                })
            
            # Add to vector store
            self.vectordb.add_documents(chunks)
            
            logger.info(f"Successfully added {len(chunks)} document chunks to vector store")
            
            return {
                "success": True,
                "message": f"Successfully processed {len(documents)} documents into {len(chunks)} chunks",
                "chunks_added": len(chunks)
            }
        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            return {"success": False, "message": f"Error adding documents: {str(e)}"}
    
    async def add_document_from_file(self, file_path: str, source_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Add a document from a file path
        
        Args:
            file_path: Path to the document file
            source_name: Optional custom source name
            
        Returns:
            Dict containing the result of the operation
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                return {"success": False, "message": f"File not found: {file_path}"}
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Create document
            source = source_name or file_path.name
            document = Document(
                page_content=content,
                metadata={"source": source, "file_path": str(file_path)}
            )
            
            return await self.add_documents([document])
        except Exception as e:
            logger.error(f"Error adding document from file: {str(e)}")
            return {"success": False, "message": f"Error adding document: {str(e)}"}
    
    async def check_relevance(self, question: str, context: str) -> bool:
        """
        Check if the context is relevant to answer the question
        
        Args:
            question: The question being asked
            context: The retrieved context
            
        Returns:
            True if relevant, False otherwise
        """
        try:
            prompt = self.relevance_prompt.format(context=context, question=question)
            response = self.llm.invoke(prompt)
            return "RELEVANT" in response.content.upper()
        except Exception as e:
            logger.error(f"Error checking relevance: {str(e)}")
            return False
    
    async def query(self, question: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Query the RAG system with a question
        
        Args:
            question: The question to ask
            context: Optional additional context
            
        Returns:
            Dict containing the answer and metadata, or None if not relevant
        """
        try:
            # Combine question with context if provided
            query = f"{context}\n{question}" if context else question
            
            # Get relevant documents with scores
            docs = self.retriever.get_relevant_documents(query)
            
            if not docs:
                return {
                    "answer": None,
                    "sources": [],
                    "confidence": 0.0,
                    "message": "No relevant information found in the documents."
                }
            
            # Check relevance of the retrieved context
            combined_context = "\n".join([doc.page_content for doc in docs])
            is_relevant = await self.check_relevance(question, combined_context)
            
            if not is_relevant:
                return {
                    "answer": None,
                    "sources": [],
                    "confidence": 0.0,
                    "message": "The available documents do not contain relevant information to answer this question."
                }
            
            # Create a simple prompt for answer generation
            answer_prompt = f"""
            Based on the following context, answer the question accurately and concisely.
            If you cannot answer based on the context, say "I cannot answer this question based on the provided information."
            
            Context: {combined_context}
            
            Question: {question}
            
            Answer:
            """
            
            # Get answer from LLM
            response = self.llm.invoke(answer_prompt)
            answer = response.content
            
            # Get source documents
            sources = [doc.metadata.get("source", "Unknown") for doc in docs]
            
            # Calculate confidence based on similarity scores
            confidence = min(0.95, max(0.1, len(docs) * 0.2))  # Simple confidence calculation
            
            return {
                "answer": answer,
                "sources": sources,
                "confidence": confidence,
                "message": "Answer found in relevant documents."
            }
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return {
                "answer": None,
                "sources": [],
                "confidence": 0.0,
                "message": f"Error processing query: {str(e)}"
            }
    
    async def get_document_count(self) -> int:
        """Get the number of documents in the vector store"""
        try:
            # This is a simple way to get document count
            # In a real implementation, you might want to track this separately
            return self.vectordb._collection.count()
        except Exception as e:
            logger.error(f"Error getting document count: {str(e)}")
            return 0

# Create singleton instance
rag_service = RAGService()