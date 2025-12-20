import nltk
import re
import hashlib
import uuid
from typing import List, Dict, Any, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import logging


class ChunkingService:
    """Service for semantic chunking of documents with configurable overlap"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.max_chunk_size = self.config.get("max_chunk_size", 1000)
        self.chunk_overlap = self.config.get("chunk_overlap", 100)
        self.min_chunk_size = self.config.get("min_chunk_size", 100)
        self.similarity_threshold = self.config.get("similarity_threshold", 0.7)
        
        self.logger = logging.getLogger(__name__)
        
        # Download NLTK data if needed
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        
        try:
            nltk.data.find('tokenizers/punkt_tab')
        except LookupError:
            nltk.download('punkt_tab')
    
    def chunk_document(self, document_id: str, content: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Chunk a document into semantically coherent pieces
        
        Args:
            document_id: ID of the document
            content: Text content to chunk
            metadata: Additional metadata for chunks
            
        Returns:
            List of chunk dictionaries
        """
        try:
            # Validate content
            if not content or len(content.strip()) < self.min_chunk_size:
                self.logger.warning(f"Content too short for chunking: {len(content)} chars")
                return []
            
            # Clean and normalize content
            clean_content = self._clean_content(content)
            
            # Split into sentences
            sentences = self._split_into_sentences(clean_content)
            
            if not sentences:
                self.logger.warning("No sentences found in content")
                return []
            
            # Create semantic chunks
            chunks = self._create_semantic_chunks(document_id, sentences, metadata)
            
            self.logger.info(f"Created {len(chunks)} chunks from {len(sentences)} sentences")
            return chunks
            
        except Exception as e:
            self.logger.error(f"Failed to chunk document: {e}")
            return []
    
    def _clean_content(self, content: str) -> str:
        """Clean and normalize content"""
        # Remove extra whitespace
        content = re.sub(r'\s+', ' ', content)
        
        # Remove excessive line breaks
        content = re.sub(r'\n\s*\n', '\n\n', content)
        
        # Strip leading/trailing whitespace
        content = content.strip()
        
        return content
    
    def _split_into_sentences(self, content: str) -> List[str]:
        """Split content into sentences using NLTK"""
        try:
            # Use NLTK for sentence splitting
            sentences = nltk.sent_tokenize(content)
            
            # Clean sentences
            cleaned_sentences = []
            for sentence in sentences:
                sentence = sentence.strip()
                if sentence:
                    cleaned_sentences.append(sentence)
            
            return cleaned_sentences
            
        except Exception as e:
            self.logger.error(f"Failed to split sentences: {e}")
            # Fallback to simple regex-based splitting
            return self._fallback_sentence_split(content)
    
    def _fallback_sentence_split(self, content: str) -> List[str]:
        """Fallback sentence splitting using regex"""
        # Simple sentence split on periods, question marks, exclamation marks
        sentence_endings = r'[.!?]+'
        sentences = re.split(sentence_endings, content)
        
        # Clean up
        cleaned_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and len(sentence) > 10:  # Skip very short fragments
                cleaned_sentences.append(sentence)
        
        return cleaned_sentences
    
    def _create_semantic_chunks(self, document_id: str, sentences: List[str], metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Create semantically coherent chunks using similarity analysis"""
        try:
            chunks = []
            current_chunk_sentences = []
            current_chunk_length = 0
            chunk_index = 0
            
            for sentence in sentences:
                sentence_length = len(sentence)
                
                # Check if adding this sentence would exceed max chunk size
                if (current_chunk_length + sentence_length > self.max_chunk_size and 
                    current_chunk_sentences):
                    
                    # Create chunk from current sentences
                    chunk_content = ' '.join(current_chunk_sentences)
                    chunk = self._create_chunk(document_id, chunk_index, chunk_content, metadata)
                    if chunk:
                        chunks.append(chunk)
                    
                    # Start new chunk with overlap
                    current_chunk_sentences = self._apply_overlap(
                        current_chunk_sentences, sentence, self.chunk_overlap
                    )
                    current_chunk_length = sum(len(s) for s in current_chunk_sentences)
                    chunk_index += 1
                
                else:
                    current_chunk_sentences.append(sentence)
                    current_chunk_length += sentence_length
            
            # Don't forget the last chunk
            if current_chunk_sentences:
                chunk_content = ' '.join(current_chunk_sentences)
                if len(chunk_content) >= self.min_chunk_size:
                    chunk = self._create_chunk(document_id, chunk_index, chunk_content, metadata)
                    if chunk:
                        chunks.append(chunk)
            
            # If we have too few chunks, try semantic grouping
            if len(chunks) < 2 and len(sentences) > 3:
                chunks = self._create_semantic_groups(document_id, sentences, metadata)
            
            return chunks
            
        except Exception as e:
            self.logger.error(f"Failed to create semantic chunks: {e}")
            # Fallback to simple chunking
            return self._fallback_chunking(document_id, content, metadata)
    
    def _apply_overlap(self, current_sentences: List[str], new_sentence: str, overlap: int) -> List[str]:
        """Apply overlap by keeping the last few sentences"""
        if overlap <= 0 or not current_sentences:
            return [new_sentence]
        
        # Calculate how many characters to include from previous sentences
        overlap_chars = min(overlap, sum(len(s) for s in current_sentences))
        overlap_sentences = []
        
        # Start from the end and work backwards
        accumulated_chars = 0
        for sentence in reversed(current_sentences):
            if accumulated_chars + len(sentence) <= overlap_chars:
                overlap_sentences.insert(0, sentence)
                accumulated_chars += len(sentence)
            else:
                # Partial sentence needed
                remaining_chars = overlap_chars - accumulated_chars
                if remaining_chars > 0:
                    partial_sentence = sentence[-remaining_chars:]
                    overlap_sentences.insert(0, partial_sentence)
                break
        
        return overlap_sentences + [new_sentence]
    
    def _create_chunk(self, document_id: str, chunk_index: int, content: str, metadata: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Create a chunk dictionary with metadata"""
        try:
            # Generate chunk hash for deduplication
            chunk_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
            
            # Calculate character positions
            start_char = 0  # We'll calculate this properly in a more sophisticated version
            end_char = len(content)
            
            chunk = {
                "id": str(uuid.uuid4()),
                "document_id": document_id,
                "content": content,
                "chunk_index": chunk_index,
                "start_char": start_char,
                "end_char": end_char,
                "chunk_hash": chunk_hash,
                "metadata": metadata or {},
                "created_at": None  # Will be set by caller
            }
            
            return chunk
            
        except Exception as e:
            self.logger.error(f"Failed to create chunk: {e}")
            return None
    
    def _create_semantic_groups(self, document_id: str, sentences: List[str], metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Create chunks using semantic similarity grouping"""
        try:
            if len(sentences) < 3:
                # Too few sentences for semantic grouping
                return self._simple_chunking(document_id, sentences, metadata)
            
            # Create TF-IDF vectors for similarity calculation
            vectorizer = TfidfVectorizer(stop_words='english')
            try:
                tfidf_matrix = vectorizer.fit_transform(sentences)
            except:
                # Fallback if vectorization fails
                return self._simple_chunking(document_id, sentences, metadata)
            
            # Calculate similarity matrix
            similarity_matrix = cosine_similarity(tfidf_matrix)
            
            # Group sentences based on similarity
            chunks = []
            used_sentences = set()
            chunk_index = 0
            
            for i, sentence in enumerate(sentences):
                if i in used_sentences:
                    continue
                
                # Start a new group with this sentence
                group_sentences = [sentence]
                used_sentences.add(i)
                
                # Find similar sentences
                for j in range(i + 1, len(sentences)):
                    if j in used_sentences:
                        continue
                    
                    similarity = similarity_matrix[i][j]
                    if similarity > self.similarity_threshold:
                        group_sentences.append(sentences[j])
                        used_sentences.add(j)
                
                # Create chunk from group if it's substantial enough
                chunk_content = ' '.join(group_sentences)
                if len(chunk_content) >= self.min_chunk_size:
                    chunk = self._create_chunk(document_id, chunk_index, chunk_content, metadata)
                    if chunk:
                        chunks.append(chunk)
                    chunk_index += 1
            
            return chunks
            
        except Exception as e:
            self.logger.error(f"Failed to create semantic groups: {e}")
            return self._simple_chunking(document_id, sentences, metadata)
    
    def _simple_chunking(self, document_id: str, sentences: List[str], metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Simple fixed-size chunking as fallback"""
        chunks = []
        current_chunk = ""
        chunk_index = 0
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) > self.max_chunk_size and current_chunk:
                # Create chunk
                chunk = self._create_chunk(document_id, chunk_index, current_chunk, metadata)
                if chunk:
                    chunks.append(chunk)
                
                # Start new chunk with overlap
                current_chunk = sentence[-self.chunk_overlap:] + " " + sentence if self.chunk_overlap > 0 else sentence
                chunk_index += 1
            else:
                current_chunk += " " + sentence if current_chunk else sentence
        
        # Don't forget the last chunk
        if current_chunk and len(current_chunk) >= self.min_chunk_size:
            chunk = self._create_chunk(document_id, chunk_index, current_chunk, metadata)
            if chunk:
                chunks.append(chunk)
        
        return chunks
    
    def _fallback_chunking(self, document_id: str, content: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Fallback chunking for when everything else fails"""
        sentences = self._fallback_sentence_split(content)
        return self._simple_chunking(document_id, sentences, metadata)