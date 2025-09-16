import pytest
from unittest.mock import patch, MagicMock
from src.rag_pipeline import RAGPipeline

class TestRAGPipeline:
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_vectorstore = MagicMock()
        self.rag_pipeline = RAGPipeline(self.mock_vectorstore)

    def test_init(self):
        """Test RAGPipeline initialization"""
        assert self.rag_pipeline.llm is not None
        assert self.rag_pipeline.retriever is not None
        assert self.rag_pipeline.prompt_template is not None

    @patch('src.rag_pipeline.OpenAI')
    def test_query_success(self, mock_openai):
        """Test successful query execution"""
        # Mock the retriever
        mock_doc = MagicMock()
        mock_doc.page_content = "Test content"
        mock_doc.metadata = {"source": "test.pdf", "page": 1}
        self.mock_vectorstore.as_retriever.return_value.get_relevant_documents.return_value = [mock_doc]
        
        # Mock the LLM response
        mock_llm_instance = MagicMock()
        mock_llm_instance.return_value = "Test answer"
        mock_openai.return_value = mock_llm_instance
        
        result = self.rag_pipeline.query("Test question")
        
        assert "answer" in result
        assert "sources" in result
        assert "relevant_documents" in result
        assert result["answer"] == "Test answer"
        assert len(result["sources"]) == 1

    def test_query_with_retriever_error(self):
        """Test query handling when retriever fails"""
        self.mock_vectorstore.as_retriever.return_value.get_relevant_documents.side_effect = Exception("Retriever error")
        
        result = self.rag_pipeline.query("Test question")
        
        assert "Sorry, I encountered an error" in result["answer"]
        assert result["sources"] == []

    @patch('src.rag_pipeline.OpenAI')
    def test_query_with_llm_error(self, mock_openai):
        """Test query handling when LLM fails"""
        # Mock the retriever
        mock_doc = MagicMock()
        mock_doc.page_content = "Test content"
        mock_doc.metadata = {"source": "test.pdf"}
        self.mock_vectorstore.as_retriever.return_value.get_relevant_documents.return_value = [mock_doc]
        
        # Mock LLM to raise exception
        mock_llm_instance = MagicMock()
        mock_llm_instance.side_effect = Exception("LLM error")
        mock_openai.return_value = mock_llm_instance
        
        result = self.rag_pipeline.query("Test question")
        
        assert "error" in result["answer"].lower()
        assert result["sources"] == []

    def test_source_extraction(self):
        """Test source extraction from documents"""
        mock_docs = [
            MagicMock(page_content="content1", metadata={"source": "doc1.pdf", "page": 1}),
            MagicMock(page_content="content2", metadata={"source": "doc2.pdf", "page": 2}),
            MagicMock(page_content="content3", metadata={"source": "doc1.pdf", "page": 3})  # Duplicate source
        ]
        
        self.mock_vectorstore.as_retriever.return_value.get_relevant_documents.return_value = mock_docs
        
        with patch('src.rag_pipeline.OpenAI') as mock_openai:
            mock_llm_instance = MagicMock()
            mock_llm_instance.return_value = "Test answer"
            mock_openai.return_value = mock_llm_instance
            
            result = self.rag_pipeline.query("Test question")
            
            # Should have 2 unique sources (doc1.pdf appears twice but should be deduplicated)
            assert len(result["sources"]) == 2
            source_names = [s["document"] for s in result["sources"]]
            assert "doc1.pdf" in source_names
            assert "doc2.pdf" in source_names
