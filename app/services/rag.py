import logging
import time
import re
from typing import List, Dict, Any
from .chat import chat_service
from ..data.default_documents import DEFAULT_DOCUMENTS

logger = logging.getLogger(__name__)


class RAGService:
    """Simplified RAG service orchestrating the complete pipeline (Ponytail rules)."""
    
    def __init__(self):
        """Initialize RAG service."""
        self.chat_service = chat_service
        self.documents = DEFAULT_DOCUMENTS
    
    async def seed_documents(self, documents: List[Dict[str, str]] = None) -> int:
        """
        Seed the knowledge base with documents.
        
        Args:
            documents: Optional list of documents. If None, uses default documents.
            
        Returns:
            Number of chunks successfully inserted
        """
        start_time = time.time()
        
        if documents is not None:
            self.documents = documents
            
        elapsed_ms = int((time.time() - start_time) * 1000)
        logger.info(f"Seeding completed in {elapsed_ms}ms: {len(self.documents)} documents stored in-memory.")
        
        return len(self.documents)
    
    async def answer_query(self, query: str, top_k: int = 6) -> Dict[str, Any]:
        """
        Process a query through the simplified RAG pipeline.
        
        Args:
            query: User's question
            top_k: Number of chunks to retrieve
            
        Returns:
            Dictionary with answer, citations, and debug info
        """
        start_time = time.time()
        
        try:
            # Step 1: "Search" (Just returning all documents or a subset if needed, here we return all since they fit in context)
            context_blocks = self.documents[:top_k]
            
            # Step 2: Generate answer
            answer_text = await self.chat_service.generate_answer(query, context_blocks)
            
            # Step 3: Extract citations from answer
            citations = self._extract_citations(answer_text, context_blocks)
            
            elapsed_ms = int((time.time() - start_time) * 1000)
            
            result = {
                'text': answer_text,
                'citations': citations,
                'debug': {
                    'top_doc_ids': [block.get('chunk_id', 'unknown') for block in context_blocks],
                    'latency_ms': elapsed_ms
                }
            }
            
            logger.info(f"Query processed in {elapsed_ms}ms with {len(citations)} citations")
            return result
            
        except Exception as e:
            logger.error(f"Query processing failed: {e}", exc_info=True)
            return {
                'text': "I encountered an error while processing your question. Please try again.",
                'citations': [],
                'debug': {
                    'top_doc_ids': [],
                    'latency_ms': int((time.time() - start_time) * 1000)
                }
            }
    
    def _extract_citations(self, answer_text: str, context_blocks: List[Dict[str, Any]]) -> List[str]:
        """
        Extract citation chunk_ids from the generated answer.
        """
        citation_pattern = r'\[([^\]]+)\]'
        found_citations = re.findall(citation_pattern, answer_text)
        
        valid_chunk_ids = {block.get('chunk_id') for block in context_blocks if block.get('chunk_id')}
        valid_citations = [cite for cite in found_citations if cite in valid_chunk_ids]
        
        unique_citations = []
        for cite in valid_citations:
            if cite not in unique_citations:
                unique_citations.append(cite)
        
        return unique_citations

rag_service = RAGService()
