import pytest
from unittest.mock import patch, MagicMock
import requests
from src.mcp_integration import MCPClient, MCPIntegratedRAG

class TestMCPIntegration:
    def test_mcp_client_init(self):
        """Test MCPClient initialization"""
        client = MCPClient("http://localhost:8000", "test-api-key")
        
        assert client.base_url == "http://localhost:8000"
        assert client.headers["Authorization"] == "Bearer test-api-key"

    @patch('src.mcp_integration.requests.post')
    def test_upload_documents_success(self, mock_post):
        """Test successful document upload"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "document_count": 3}
        mock_post.return_value = mock_response
        
        client = MCPClient("http://localhost:8000")
        test_documents = [{"name": "doc1.pdf", "content": "test content"}]
        
        result = client.upload_documents(test_documents)
        
        mock_post.assert_called_once()
        assert result["status"] == "success"
        assert result["document_count"] == 3

    @patch('src.mcp_integration.requests.post')
    def test_upload_documents_failure(self, mock_post):
        """Test document upload failure"""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = requests.HTTPError("Server error")
        mock_post.return_value = mock_response
        
        client = MCPClient("http://localhost:8000")
        test_documents = [{"name": "doc1.pdf", "content": "test content"}]
        
        with pytest.raises(requests.HTTPError):
            client.upload_documents(test_documents)

    @patch('src.mcp_integration.requests.post')
    def test_query_documents(self, mock_post):
        """Test document querying"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "answer": "Test answer",
            "sources": [{"document": "test.pdf", "page": 1}],
            "documents": ["doc1 content"]
        }
        mock_post.return_value = mock_response
        
        client = MCPClient("http://localhost:8000")
        result = client.query_documents("Test question")
        
        assert result["answer"] == "Test answer"
        assert len(result["sources"]) == 1

    @patch('src.mcp_integration.requests.get')
    def test_get_similar_documents(self, mock_get):
        """Test getting similar documents"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "similar_documents": [
                {"id": "doc2", "similarity": 0.85},
                {"id": "doc3", "similarity": 0.78}
            ]
        }
        mock_get.return_value = mock_response
        
        client = MCPClient("http://localhost:8000")
        result = client.get_similar_documents("doc1", limit=2)
        
        assert len(result["similar_documents"]) == 2
        mock_get.assert_called_with(
            "http://localhost:8000/api/similar/doc1",
            headers=client.headers,
            params={"limit": 2}
        )

    def test_mcp_integrated_rag_query(self):
        """Test MCPIntegratedRAG query functionality"""
        mock_client = MagicMock()
        mock_client.query_documents.return_value = {
            "answer": "Test answer from MCP",
            "sources": [{"document": "test.pdf", "page": 1}],
            "documents": ["relevant content"]
        }
        
        rag = MCPIntegratedRAG(mock_client)
        result = rag.query("Test question")
        
        assert result["answer"] == "Test answer from MCP"
        assert len(result["sources"]) == 1
        mock_client.query_documents.assert_called_with("Test question", None)

    def test_mcp_integrated_rag_query_error(self):
        """Test MCPIntegratedRAG error handling"""
        mock_client = MagicMock()
        mock_client.query_documents.side_effect = Exception("MCP server down")
        
        rag = MCPIntegratedRAG(mock_client)
        result = rag.query("Test question")
        
        assert "error" in result["answer"].lower()
        assert result["sources"] == []
