"""
RAG Pipeline — Document Loader
Supports: PDF, TXT, DOCX, CSV, Markdown
"""

import os
from pathlib import Path
from typing import List, Dict, Any

try:
    from langchain_core.documents import Document
except ImportError:
    class Document:
        def __init__(self, page_content: str, metadata: Dict[str, Any] = None):
            self.page_content = page_content
            self.metadata = metadata or {}


def load_document(file_path: str) -> List[Document]:
    """Load a document from the given file path and return Documents."""
    path = Path(file_path)
    ext = path.suffix.lower()

    if ext == ".pdf":
        return _load_pdf(file_path)
    elif ext == ".txt":
        return _load_txt(file_path)
    elif ext == ".docx":
        return _load_docx(file_path)
    elif ext == ".csv":
        return _load_csv(file_path)
    elif ext in (".md", ".markdown"):
        return _load_markdown(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")


def _load_pdf(file_path: str) -> List[Document]:
    from pypdf import PdfReader

    reader = PdfReader(file_path)
    docs = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        if text.strip():
            docs.append(Document(
                page_content=text,
                metadata={"source": file_path, "page": i + 1, "type": "pdf"}
            ))
    return docs


def _load_txt(file_path: str) -> List[Document]:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()
    return [Document(page_content=text, metadata={"source": file_path, "type": "txt"})]


def _load_docx(file_path: str) -> List[Document]:
    from docx import Document as DocxDocument

    doc = DocxDocument(file_path)
    paragraphs = [para.text.strip() for para in doc.paragraphs if para.text.strip()]
    
    # Also extract text from all tables in the DOCX
    table_texts = []
    for table in doc.tables:
        for row in table.rows:
            row_cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
            if row_cells:
                # Deduplicate identical adjacent cells (due to cell merges)
                deduped = []
                for cell_str in row_cells:
                    if not deduped or deduped[-1] != cell_str:
                        deduped.append(cell_str)
                table_texts.append(" | ".join(deduped))
    
    combined = []
    if paragraphs:
        combined.extend(paragraphs)
    if table_texts:
        combined.append("\n### Document Tables Data:\n" + "\n".join(table_texts))
        
    full_text = "\n\n".join(combined)
    return [Document(page_content=full_text, metadata={"source": file_path, "type": "docx"})]


def _load_csv(file_path: str) -> List[Document]:
    import pandas as pd

    df = pd.read_csv(file_path)
    rows = []
    for idx, row in df.iterrows():
        row_text = " | ".join([f"{col}: {val}" for col, val in row.items()])
        rows.append(Document(
            page_content=row_text,
            metadata={"source": file_path, "type": "csv", "row": idx}
        ))
    return rows


def _load_markdown(file_path: str) -> List[Document]:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()
    return [Document(page_content=text, metadata={"source": file_path, "type": "markdown"})]
