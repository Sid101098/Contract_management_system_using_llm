import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock
from src.document_processor import DocumentProcessor
from langchain.schema import Document

class TestDocumentProcessor:
    def test_init(self):
        """Test DocumentProcessor initialization"""
        processor = DocumentProcessor()
        assert processor.persist_directory == "./chroma_db"
        assert processor.text_splitter is not None
        assert processor.embeddings is not None

    def test_process_pdf_success(self):
        """Test successful PDF processing"""
        processor = DocumentProcessor()
        
        # Create a temporary PDF file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp.write(b'%PDF sample content')
            tmp_path = tmp.name
        
        try:
            docs = processor._process_pdf(tmp_path)
            assert len(docs) == 1
            assert isinstance(docs[0], Document)
            assert 'source' in docs[0].metadata
        finally:
            os.unlink(tmp_path)

    def test_process_pdf_failure(self):
        """Test PDF processing failure"""
        processor = DocumentProcessor()
        
        # Create an invalid PDF file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp.write(b'Not a real PDF content')
            tmp_path = tmp.name
        
        try:
            docs = processor._process_pdf(tmp_path)
            assert len(docs) == 0  # Should return empty list on error
        finally:
            os.unlink(tmp_path)

    def test_process_docx(self):
        """Test DOCX processing"""
        processor = DocumentProcessor()
        
        # Mock docx.Document to avoid external dependencies
        with patch('src.document_processor.docx') as mock_docx:
            mock_doc = MagicMock()
            mock_doc.paragraphs = [MagicMock(text="Test paragraph")]
            mock_docx.Document.return_value = mock_doc
            
            with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp:
                tmp_path = tmp.name
            
            try:
                docs = processor._process_docx(tmp_path)
                assert len(docs) == 1
                assert "Test paragraph" in docs[0].page_content
            finally:
                os.unlink(tmp_path)

    def test_chunk_documents(self):
        """Test document chunking functionality"""
        processor = DocumentProcessor()
        
        test_docs = [
            Document(page_content="This is a test document " * 50, metadata={"source": "test.txt"}),
            Document(page_content="Another document " * 40, metadata={"source": "test2.txt"})
        ]
        
        chunks = processor.chunk_documents(test_docs)
        
        assert len(chunks) > len(test_docs)  # Should have more chunks than original docs
        for chunk in chunks:
            assert len(chunk.page_content) <= 1000  # Should respect chunk size

    @patch('src.document_processor.Chroma.from_documents')
    def test_create_vectorstore(self, mock_chroma):
        """Test vector store creation"""
        processor = DocumentProcessor()
        test_docs = [Document(page_content="test", metadata={"source": "test.txt"})]
        
        mock_instance = MagicMock()
        mock_chroma.return_value = mock_instance
        
        result = processor.create_vectorstore(test_docs)
        
        mock_chroma.assert_called_once()
        assert result == mock_instance

    def test_load_nonexistent_vectorstore(self):
        """Test loading non-existent vector store"""
        processor = DocumentProcessor()
        processor.persist_directory = "/nonexistent/path"
        
        result = processor.load_vectorstore()
        assert result is None
