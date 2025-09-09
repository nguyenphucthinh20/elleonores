from llama_index.readers.file import (
    DocxReader,
    PDFReader,
    MarkdownReader,
    PptxReader,
    UnstructuredReader,
    XMLReader,
    CSVReader
)

from llama_index.core import Document
from app.loaders.excel import PandasExcelReader
from app.loaders.url import SeleniumWebReader
from typing import List
from pathlib import Path

LOADERS = {
    ".csv": (CSVReader, {}),
    ".docx": (DocxReader, {}),
    ".eml": (UnstructuredReader, {}),
    ".epub": (UnstructuredReader, {}),
    ".html": (UnstructuredReader, {}),
    ".md": (MarkdownReader, {}),
    ".odt": (PandasExcelReader, {}),
    ".pdf": (PDFReader, {}),
    ".pptx": (PptxReader, {}),
    ".txt": (UnstructuredReader, {}),
    ".xls": (PandasExcelReader, {}),
    ".xlsx": (PandasExcelReader, {}),
    ".xml": (XMLReader, {}),
    ".url": (SeleniumWebReader, {"browser": "chrome", "headless": True}),
}

def load_file(file_path: str, **kwargs) -> List[Document]:
    """
    Loads and processes a file using appropriate loader based on file extension.
    
    Args:
        file_path (str): Path to the file to be loaded
        **kwargs: Additional arguments to pass to the loader
        
    Returns:
        List[Document]: List of Document objects containing the processed content
    """
    if isinstance(file_path, list):
        loader = SeleniumWebReader(browser="chrome", headless=True)
        return loader.load_data(file_path)
    file_path = Path(file_path)
    ext = file_path.suffix.lower()

    if ext not in LOADERS:
        raise ValueError(f"Unsupported file extension: {ext}")
    loader_class, loader_config = LOADERS[ext]
    loader = loader_class(**loader_config)

    try:
        documents = loader.load_data(file_path)
        return documents
    except Exception as e:
        print(f"Error loading file {file_path}: {e}")
        return []