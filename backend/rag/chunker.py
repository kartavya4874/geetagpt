"""
RAG Pipeline — Text Chunker
Splits documents into overlapping chunks for better retrieval.
"""

from typing import List, Dict, Any

try:
    from langchain_core.documents import Document
except ImportError:
    class Document:
        def __init__(self, page_content: str, metadata: Dict[str, Any] = None):
            self.page_content = page_content
            self.metadata = metadata or {}

# Support LangChain 0.3+ (langchain_text_splitters) and older versions (langchain.text_splitter)
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    try:
        from langchain.text_splitter import RecursiveCharacterTextSplitter
    except ImportError:
        # Built-in lightweight fallback splitter
        class RecursiveCharacterTextSplitter:
            def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200, **kwargs):
                self.chunk_size = chunk_size
                self.chunk_overlap = chunk_overlap

            def split_documents(self, documents: List[Document]) -> List[Document]:
                chunks = []
                for doc in documents:
                    text = doc.page_content
                    start = 0
                    while start < len(text):
                        end = min(start + self.chunk_size, len(text))
                        chunk_text = text[start:end]
                        if chunk_text.strip():
                            chunks.append(Document(
                                page_content=chunk_text,
                                metadata=dict(doc.metadata)
                            ))
                        if end >= len(text):
                            break
                        start += max(1, self.chunk_size - self.chunk_overlap)
                return chunks


def chunk_documents(
    documents: List[Document],
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> List[Document]:
    """
    Split documents into chunks using RecursiveCharacterTextSplitter.

    Args:
        documents: List of Document objects.
        chunk_size: Max tokens/characters per chunk.
        chunk_overlap: Overlap between consecutive chunks.

    Returns:
        List of chunked Document objects.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    chunks = splitter.split_documents(documents)
    # Tag each chunk with its index
    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_index"] = i
    return chunks
