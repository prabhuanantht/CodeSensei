"""
RAG Chatbot for Codebase Analysis
Implements semantic search over codebase with code-aware chunking
"""
import os
import re
import fnmatch
from pathlib import Path
from typing import List, Dict, Tuple
import chromadb
from chromadb.utils import embedding_functions
from google import genai
import hashlib


class CodeChunker:
    """
    Advanced code-aware chunking that respects code structure
    """
    
    def __init__(self, chunk_size: int = 1500, overlap: int = 200):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_code_file(self, file_path: str, content: str) -> List[Dict]:
        """
        Chunk a code file intelligently, respecting code boundaries
        """
        chunks = []
        
        # Detect file type
        ext = Path(file_path).suffix.lower()
        
        if ext in ['.py', '.java', '.js', '.ts', '.go', '.rb', '.php']:
            # Use function/class-based chunking for these languages
            chunks = self._chunk_by_functions(file_path, content, ext)
        elif ext in ['.md', '.txt', '.rst']:
            # Use paragraph-based chunking for documentation
            chunks = self._chunk_by_paragraphs(file_path, content)
        else:
            # Use simple sliding window for other files
            chunks = self._chunk_sliding_window(file_path, content)
        
        return chunks
    
    def _chunk_by_functions(self, file_path: str, content: str, ext: str) -> List[Dict]:
        """
        Chunk code by function/class definitions
        """
        chunks = []
        lines = content.split('\n')
        
        # Patterns for different languages
        patterns = {
            '.py': r'^(class |def |async def )',
            '.js': r'^(class |function |const \w+ = |export |async )',
            '.ts': r'^(class |function |const \w+ = |export |interface |type )',
            '.java': r'^(public |private |protected |class |interface )',
            '.go': r'^(func |type |package )',
        }
        
        pattern = patterns.get(ext, r'^(def |function |class )')
        
        current_chunk = []
        current_size = 0
        chunk_start_line = 1
        
        for i, line in enumerate(lines, 1):
            # Check if line starts a new definition
            if re.match(pattern, line.strip()) and current_chunk and current_size > 300:
                # Save current chunk
                chunk_content = '\n'.join(current_chunk)
                chunks.append({
                    'content': chunk_content,
                    'metadata': {
                        'file_path': file_path,
                        'start_line': chunk_start_line,
                        'end_line': i - 1,
                        'type': 'code',
                        'language': ext[1:]
                    }
                })
                
                # Start new chunk with overlap
                overlap_lines = current_chunk[-10:] if len(current_chunk) > 10 else current_chunk
                current_chunk = overlap_lines + [line]
                current_size = sum(len(l) for l in current_chunk)
                chunk_start_line = i - len(overlap_lines)
            else:
                current_chunk.append(line)
                current_size += len(line)
                
                # If chunk too large, split it
                if current_size > self.chunk_size:
                    chunk_content = '\n'.join(current_chunk)
                    chunks.append({
                        'content': chunk_content,
                        'metadata': {
                            'file_path': file_path,
                            'start_line': chunk_start_line,
                            'end_line': i,
                            'type': 'code',
                            'language': ext[1:]
                        }
                    })
                    
                    # Keep overlap
                    overlap_lines = current_chunk[-10:]
                    current_chunk = overlap_lines
                    current_size = sum(len(l) for l in current_chunk)
                    chunk_start_line = i - len(overlap_lines) + 1
        
        # Save last chunk
        if current_chunk:
            chunk_content = '\n'.join(current_chunk)
            chunks.append({
                'content': chunk_content,
                'metadata': {
                    'file_path': file_path,
                    'start_line': chunk_start_line,
                    'end_line': len(lines),
                    'type': 'code',
                    'language': ext[1:]
                }
            })
        
        return chunks
    
    def _chunk_by_paragraphs(self, file_path: str, content: str) -> List[Dict]:
        """
        Chunk markdown/text by paragraphs
        """
        chunks = []
        paragraphs = content.split('\n\n')
        
        current_chunk = []
        current_size = 0
        
        for para in paragraphs:
            para_size = len(para)
            
            if current_size + para_size > self.chunk_size and current_chunk:
                chunks.append({
                    'content': '\n\n'.join(current_chunk),
                    'metadata': {
                        'file_path': file_path,
                        'type': 'documentation'
                    }
                })
                
                # Keep last paragraph for overlap
                current_chunk = [current_chunk[-1], para] if current_chunk else [para]
                current_size = sum(len(p) for p in current_chunk)
            else:
                current_chunk.append(para)
                current_size += para_size
        
        # Save last chunk
        if current_chunk:
            chunks.append({
                'content': '\n\n'.join(current_chunk),
                'metadata': {
                    'file_path': file_path,
                    'type': 'documentation'
                }
            })
        
        return chunks
    
    def _chunk_sliding_window(self, file_path: str, content: str) -> List[Dict]:
        """
        Simple sliding window chunking
        """
        chunks = []
        lines = content.split('\n')
        
        i = 0
        while i < len(lines):
            chunk_lines = lines[i:i + 100]  # ~100 lines per chunk
            chunk_content = '\n'.join(chunk_lines)
            
            chunks.append({
                'content': chunk_content,
                'metadata': {
                    'file_path': file_path,
                    'start_line': i + 1,
                    'end_line': min(i + 100, len(lines)),
                    'type': 'code'
                }
            })
            
            i += 80  # 20 line overlap
        
        return chunks


class CodebaseRAG:
    """
    RAG system for codebase analysis
    """
    
    def __init__(self, gemini_api_key: str = None, project_id: str = None):
        """Initialize RAG system"""
        self.gemini_api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        self.project_id = project_id or os.getenv("GEMINI_PROJECT_ID")
        
        # Initialize Gemini client
        if self.project_id:
            self.client = genai.Client(
                vertexai=True,
                project=self.project_id,
                location=os.getenv("GEMINI_LOCATION", "us-central1")
            )
        elif self.gemini_api_key:
            self.client = genai.Client(api_key=self.gemini_api_key)
        else:
            raise ValueError("Either GEMINI_API_KEY or GEMINI_PROJECT_ID must be set")
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.Client()
        
        # Use sentence transformers for embeddings (fast and accurate)
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        self.collection = None
        self.chunker = CodeChunker()
        self.indexed_files = set()
    
    def create_collection(self, collection_name: str = "codebase"):
        """Create or get collection"""
        try:
            self.chroma_client.delete_collection(name=collection_name)
        except:
            pass
        
        self.collection = self.chroma_client.create_collection(
            name=collection_name,
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"}
        )
    
    def index_codebase(self, directory: str, include_patterns: List[str] = None, 
                      exclude_patterns: List[str] = None) -> Dict:
        """
        Index a codebase directory
        """
        if include_patterns is None:
            include_patterns = [
                '*.py', '*.js', '*.jsx', '*.ts', '*.tsx', '*.java', '*.go', '*.rb', '*.php', '*.c', '*.cpp', '*.h',
                '*.md', '*.txt', '*.json', '*.yaml', '*.yml', '*.toml', 'Dockerfile*', 'Makefile*'
            ]
        
        if exclude_patterns is None:
            exclude_patterns = [
                'node_modules', '__pycache__', '.git', 'venv', 'env',
                '.next', 'build', 'dist', 'target', '.DS_Store'
            ]
        
        directory_path = Path(directory)
        all_chunks = []
        file_count = 0
        
        print(f"Scanning directory: {directory}")
        
        found_files = list(directory_path.rglob('*'))
        print(f"Found {len(found_files)} total paths (including directories)")
        
        for file_path in directory_path.rglob('*'):
            if not file_path.is_file():
                continue
            
            # Check if file should be excluded
            if any(excl in str(file_path) for excl in exclude_patterns):
                continue
            
            # Check if file matches include patterns
            # Use fnmatch for proper glob matching on full path
            file_str = str(file_path)
            matches = any(fnmatch.fnmatch(file_str, f"**/{pattern}") for pattern in include_patterns)
            
            if not matches:
                # Debug: print which files are being skipped
                if file_count < 5:  # Only print first few to avoid spam
                    print(f"Skipping {file_path.name}: doesn't match include patterns")
                continue
            
            # Debug: print files being processed
            if file_count < 5:
                print(f"Processing: {file_str}")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Skip empty files
                if not content.strip():
                    continue
                
                # Chunk the file
                relative_path = str(file_path.relative_to(directory_path))
                chunks = self.chunker.chunk_code_file(relative_path, content)
                
                all_chunks.extend(chunks)
                file_count += 1
                self.indexed_files.add(relative_path)
                
                if file_count % 10 == 0:
                    print(f"Indexed {file_count} files, {len(all_chunks)} chunks so far...")
                
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                continue
        
        # Add chunks to vector DB
        if all_chunks:
            print(f"\nAdding {len(all_chunks)} chunks to vector database...")
            
            documents = [chunk['content'] for chunk in all_chunks]
            metadatas = [chunk['metadata'] for chunk in all_chunks]
            ids = [f"chunk_{i}_{hashlib.md5(doc.encode()).hexdigest()[:8]}" 
                   for i, doc in enumerate(documents)]
            
            # Add in batches
            batch_size = 100
            for i in range(0, len(documents), batch_size):
                batch_docs = documents[i:i + batch_size]
                batch_metas = metadatas[i:i + batch_size]
                batch_ids = ids[i:i + batch_size]
                
                self.collection.add(
                    documents=batch_docs,
                    metadatas=batch_metas,
                    ids=batch_ids
                )
                
                print(f"Added batch {i//batch_size + 1}/{(len(documents) + batch_size - 1)//batch_size}")
        
        stats = {
            'total_files': file_count,
            'total_chunks': len(all_chunks),
            'indexed_files': list(self.indexed_files)
        }
        
        print(f"\n✅ Indexing complete!")
        print(f"   Files indexed: {file_count}")
        print(f"   Chunks created: {len(all_chunks)}")
        
        return stats
    
    def retrieve_relevant_chunks(self, query: str, n_results: int = 5) -> List[Dict]:
        """
        Retrieve relevant code chunks for a query
        """
        if not self.collection:
            raise ValueError("No collection created. Call create_collection() first.")
        
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        chunks = []
        for i in range(len(results['documents'][0])):
            # Calculate similarity from distance
            distance = results['distances'][0][i] if 'distances' in results and results['distances'][0] else 1.0
            similarity = 1.0 - distance  # Convert distance to similarity score
            
            # Adaptive filtering: include chunks with similarity >= 0.4 (40%)
            # This is more lenient to include more relevant chunks
            if similarity >= 0.4:
                chunks.append({
                    'content': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': distance,
                    'similarity': similarity
                })
        
        # Safety fallback: if no chunks pass threshold, return top 5 most similar ones
        if len(chunks) == 0 and len(results['documents'][0]) > 0:
            print("⚠️ No chunks passed similarity threshold, using top 5 most similar chunks as fallback")
            for i in range(min(5, len(results['documents'][0]))):
                distance = results['distances'][0][i] if 'distances' in results and results['distances'][0] else 1.0
                similarity = 1.0 - distance
                chunks.append({
                    'content': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': distance,
                    'similarity': similarity
                })
        
        return chunks
    
    def answer_query(self, query: str, n_results: int = 20) -> Dict:
        """
        Answer a user query about the codebase
        Uses adaptive retrieval - retrieves more chunks then filters by similarity
        """
        # Retrieve relevant chunks (will be filtered by similarity threshold internally)
        relevant_chunks = self.retrieve_relevant_chunks(query, n_results)
        
        # Check if we have relevant chunks
        if not relevant_chunks:
            return {
                'answer': "I couldn't find relevant code for your query in the codebase. The query might not match any of the indexed files, or the codebase might not contain information related to your question. Try rephrasing your question or asking about pipeline components, business logic, user interfaces, or similar themes.",
                'sources': []
            }
        
        print(f"📊 Found {len(relevant_chunks)} relevant chunks for the query")
        
        # Build context from chunks
        context_parts = []
        for i, chunk in enumerate(relevant_chunks, 1):
            file_path = chunk['metadata'].get('file_path', 'unknown')
            start_line = chunk['metadata'].get('start_line', '')
            end_line = chunk['metadata'].get('end_line', '')
            
            location = f"{file_path}"
            if start_line and end_line:
                location += f" (lines {start_line}-{end_line})"
            
            context_parts.append(f"### Relevant Code Chunk {i} - {location}\n```\n{chunk['content']}\n```\n")
        
        context = "\n\n".join(context_parts)
        
        # Create prompt for Gemini
        prompt = f"""You are a helpful AI assistant analyzing a codebase. Answer the user's question based on the provided code context.

**User Question:**
{query}

**Relevant Code Context:**
{context}

**Instructions:**
1. Analyze the provided code chunks carefully
2. Answer the user's question clearly and concisely
3. Reference specific files and line numbers when relevant
4. If you find issues, explain them clearly with examples
5. If the context doesn't contain enough information, say so
6. Use markdown formatting for code snippets
7. Be beginner-friendly in explanations

**Your Answer:**"""
        
        # Get response from Gemini
        model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
        response = self.client.models.generate_content(
            model=model,
            contents=[prompt]
        )
        
        return {
            'answer': response.text,
            'relevant_chunks': relevant_chunks,
            'sources': [chunk['metadata'].get('file_path', 'unknown') for chunk in relevant_chunks]
        }
    
    def get_stats(self) -> Dict:
        """Get statistics about indexed codebase"""
        if not self.collection:
            return {'status': 'No collection created'}
        
        count = self.collection.count()
        return {
            'total_chunks': count,
            'total_files': len(self.indexed_files),
            'files': list(self.indexed_files)
        }

