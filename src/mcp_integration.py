# mcp_integration.py
"""
MCP Server Integration Example

This module demonstrates how to integrate the RAG pipeline with an existing MCP server
using REST APIs. The MCP server would expose endpoints for document processing and querying.
"""

import requests
import json
from typing import List, Dict

class MCPClient:
    def __init__(self, base_url: str, api_key: str = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}' if api_key else None
        }
    
    def upload_documents(self, documents: List[Dict]) -> Dict:
        """Upload documents to MCP server for processing"""
        endpoint = f"{self.base_url}/api/documents/upload"
        response = requests.post(
            endpoint,
            headers=self.headers,
            json={"documents": documents}
        )
        response.raise_for_status()
        return response.json()
    
    def query_documents(self, question: str, filters: Dict = None) -> Dict:
        """Query documents through MCP server"""
        endpoint = f"{self.base_url}/api/query"
        payload = {
            "question": question,
            "filters": filters or {}
        }
        response = requests.post(
            endpoint,
            headers=self.headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def get_similar_documents(self, document_id: str, limit: int = 5) -> Dict:
        """Get similar documents through MCP server"""
        endpoint = f"{self.base_url}/api/similar/{document_id}"
        params = {"limit": limit}
        response = requests.get(
            endpoint,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def trigger_daily_report(self) -> Dict:
        """Trigger daily report generation on MCP server"""
        endpoint = f"{self.base_url}/api/reports/daily"
        response = requests.post(
            endpoint,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

# Example usage with the RAG pipeline
class MCPIntegratedRAG:
    def __init__(self, mcp_client: MCPClient):
        self.mcp_client = mcp_client
    
    def query(self, question: str):
        """Query through MCP server"""
        try:
            response = self.mcp_client.query_documents(question)
            return {
                "answer": response.get("answer", ""),
                "sources": response.get("sources", []),
                "relevant_documents": response.get("documents", [])
            }
        except Exception as e:
            return {
                "answer": f"Error querying MCP server: {str(e)}",
                "sources": [],
                "relevant_documents": []
            }
