import re
from pathlib import Path
from typing import List, Dict, Any
from src.config import logger

class MarkdownParser:
    """Parses Markdown files into chunks while preserving section hierarchy and metadata."""
    
    def __init__(self, max_chunk_size: int = 800, overlap: int = 150):
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap
        
    def _clean_header(self, header_text: str) -> str:
        """Removes markdown hashes and leading/trailing whitespace."""
        return re.sub(r'^#+\s+', '', header_text).strip()

    def parse_file(self, filepath: Path) -> List[Dict[str, Any]]:
        """Parses a single Markdown file into list of chunks with metadata."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Failed to read file {filepath}: {e}")
            return []
            
        doc_id = filepath.stem
        # Extract title from the first level-1 heading or use the filename
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        doc_name = title_match.group(1).strip() if title_match else doc_id
        
        chunks = []
        lines = content.splitlines()
        
        current_headers = {1: "", 2: "", 3: "", 4: ""}
        current_section_text = []
        current_char_offset = 0
        
        def build_section_path(headers: dict) -> str:
            path_parts = [headers[i] for i in sorted(headers.keys()) if headers[i]]
            return " > ".join(path_parts) if path_parts else "Introduction"

        def add_chunks_for_section(text: str, section_path: str, base_offset: int):
            if not text.strip():
                return
                
            # If text is small enough, make it a single chunk
            if len(text) <= self.max_chunk_size:
                chunks.append({
                    "doc_id": doc_id,
                    "doc_name": doc_name,
                    "section": section_path,
                    "text": text.strip(),
                    "char_offset": base_offset,
                    "length": len(text.strip())
                })
                return
                
            # Otherwise, split into overlapping chunks by paragraphs
            paragraphs = text.split("\n\n")
            current_chunk = []
            current_len = 0
            chunk_offset = base_offset
            
            for para in paragraphs:
                para = para.strip()
                if not para:
                    continue
                    
                para_len = len(para)
                
                # If a single paragraph is extremely long, split it by sentences
                if para_len > self.max_chunk_size:
                    sentences = re.split(r'(?<=[.!?])\s+', para)
                    for sent in sentences:
                        sent_len = len(sent)
                        if current_len + sent_len > self.max_chunk_size and current_chunk:
                            chunk_text = " ".join(current_chunk)
                            chunks.append({
                                "doc_id": doc_id,
                                "doc_name": doc_name,
                                "section": section_path,
                                "text": chunk_text.strip(),
                                "char_offset": chunk_offset,
                                "length": len(chunk_text.strip())
                            })
                            # Keep overlap
                            overlap_words = []
                            overlap_len = 0
                            for item in reversed(current_chunk):
                                if overlap_len + len(item) < self.overlap:
                                    overlap_words.insert(0, item)
                                    overlap_len += len(item)
                                else:
                                    break
                            current_chunk = overlap_words
                            current_len = overlap_len
                            chunk_offset = base_offset + text.find(sent) # approximate
                            
                        current_chunk.append(sent)
                        current_len += sent_len + 1
                else:
                    if current_len + para_len > self.max_chunk_size and current_chunk:
                        chunk_text = "\n\n".join(current_chunk)
                        chunks.append({
                            "doc_id": doc_id,
                            "doc_name": doc_name,
                            "section": section_path,
                            "text": chunk_text.strip(),
                            "char_offset": chunk_offset,
                            "length": len(chunk_text.strip())
                        })
                        # Keep overlap
                        overlap_paras = []
                        overlap_len = 0
                        for item in reversed(current_chunk):
                            if overlap_len + len(item) < self.overlap:
                                overlap_paras.insert(0, item)
                                overlap_len += len(item)
                            else:
                                break
                        current_chunk = overlap_paras
                        current_len = overlap_len
                        chunk_offset = base_offset + text.find(para)
                        
                    current_chunk.append(para)
                    current_len += para_len + 2
                    
            if current_chunk:
                chunk_text = "\n\n".join(current_chunk)
                chunks.append({
                    "doc_id": doc_id,
                    "doc_name": doc_name,
                    "section": section_path,
                    "text": chunk_text.strip(),
                    "char_offset": chunk_offset,
                    "length": len(chunk_text.strip())
                })

        accumulated_offset = 0
        for line in lines:
            # Check if line is a header
            header_match = re.match(r'^(#+)\s+(.+)$', line)
            if header_match:
                # Process accumulated text for previous section
                previous_section_text = "\n".join(current_section_text)
                section_path = build_section_path(current_headers)
                add_chunks_for_section(previous_section_text, section_path, current_char_offset)
                
                # Reset tracking
                current_section_text = []
                current_char_offset = accumulated_offset
                
                # Update current header hierarchy
                hashes, header_text = header_match.groups()
                level = len(hashes)
                clean_txt = self._clean_header(header_text)
                
                # Set current level and clear deeper levels
                current_headers[level] = clean_txt
                for i in range(level + 1, 5):
                    current_headers[i] = ""
            else:
                current_section_text.append(line)
                
            accumulated_offset += len(line) + 1 # +1 for newline character
            
        # Process the final section
        if current_section_text:
            previous_section_text = "\n".join(current_section_text)
            section_path = build_section_path(current_headers)
            add_chunks_for_section(previous_section_text, section_path, current_char_offset)
            
        logger.info(f"Parsed {filepath.name} into {len(chunks)} chunks.")
        return chunks

    def parse_directory(self, dirpath: Path) -> List[Dict[str, Any]]:
        """Parses all Markdown files in a directory."""
        all_chunks = []
        for file in dirpath.glob("*.md"):
            all_chunks.extend(self.parse_file(file))
        return all_chunks
