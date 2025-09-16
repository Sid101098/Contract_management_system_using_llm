import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from src.daily_agent import DailyAgent

class TestDailyAgent:
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_vectorstore = MagicMock()
        self.email_config = {
            'from_email': 'test@example.com',
            'to_email': 'recipient@example.com',
            'smtp_server': 'smtp.test.com',
            'smtp_port': 587,
            'username': 'testuser',
            'password': 'testpass'
        }
        self.agent = DailyAgent(self.mock_vectorstore, self.email_config)

    @patch('src.daily_agent.re')
    def test_extract_contract_dates(self, mock_re):
        """Test contract date extraction"""
        # Mock document data
        mock_docs = [
            "Expiration Date: 12/31/2024\nSome other content",
            "This contract expires on 01-15-2024\nMore content",
            "No date information here"
        ]
        mock_metadatas = [{"source": f"doc{i}.pdf"} for i in range(3)]
        
        self.mock_vectorstore.get.return_value = {
            'documents': mock_docs,
            'metadatas': mock_metadatas
        }
        
        # Mock regex to return dates
        mock_match = MagicMock()
        mock_match.group.return_value = "12/31/2024"
        mock_re.finditer.return_value = [mock_match]
        
        dates = self.agent.extract_contract_dates()
        
        assert len(dates) > 0
        mock_re.finditer.assert_called()

    def test_extract_contract_dates_error(self):
        """Test date extraction error handling"""
        self.mock_vectorstore.get.side_effect = Exception("Vector store error")
        
        dates = self.agent.extract_contract_dates()
        
        assert dates == []  # Should return empty list on error

    def test_detect_conflicts(self):
        """Test conflict detection"""
        mock_docs = [
            "Company: Test Corp\nAddress: 123 Main St\nContract details",
            "Company: Test Corp\nAddress: 456 Oak Ave\nDifferent contract",
            "Company: Another Corp\nAddress: 789 Pine Rd\nUnrelated contract"
        ]
        mock_metadatas = [
            {"source": "contract1.pdf"},
            {"source": "contract2.pdf"},
            {"source": "contract3.pdf"}
        ]
        
        self.mock_vectorstore.get.return_value = {
            'documents': mock_docs,
            'metadatas': mock_metadatas
        }
        
        conflicts = self.agent.detect_conflicts()
        
        assert len(conflicts) == 1
        assert conflicts[0]['company'] == 'test corp'
        assert 'Multiple addresses' in conflicts[0]['issue']

    def test_detect_conflicts_no_conflicts(self):
        """Test conflict detection when no conflicts exist"""
        mock_docs = [
            "Company: Test Corp\nAddress: 123 Main St\nContract details",
            "Company: Another Corp\nAddress: 456 Oak Ave\nDifferent contract"
        ]
        mock_metadatas = [
            {"source": "contract1.pdf"},
            {"source": "contract2.pdf"}
        ]
        
        self.mock_vectorstore.get.return_value = {
            'documents': mock_docs,
            'metadatas': mock_metadatas
        }
        
        conflicts = self.agent.detect_conflicts()
        
        assert len(conflicts) == 0  # No conflicts should be detected

    @patch('src.daily_agent.DailyAgent.extract_contract_dates')
    @patch('src.daily_agent.DailyAgent.detect_conflicts')
    def test_generate_report(self, mock_detect_conflicts, mock_extract_dates):
        """Test report generation"""
        # Mock expiring contracts
        mock_extract_dates.return_value = [
            {'document': 'contract1.pdf', 'date': '2024-01-31', 'days_until_expiration': 16},
            {'document': 'contract2.pdf', 'date': '2024-02-15', 'days_until_expiration': 31}
        ]
        
        # Mock conflicts
        mock_detect_conflicts.return_value = [
            {
                'company': 'Test Corp',
                'issue': 'Multiple addresses found',
                'addresses': {'123 Main St': ['contract1.pdf'], '456 Oak Ave': ['contract2.pdf']},
                'documents': ['contract1.pdf', 'contract2.pdf']
            }
        ]
        
        report = self.agent.generate_report()
        
        assert "APPROACHING CONTRACT EXPIRATIONS" in report
        assert "CONFLICTS DETECTED" in report
        assert "contract1.pdf" in report
        assert "Test Corp" in report

    @patch('smtplib.SMTP')
    def test_send_email_report_success(self, mock_smtp):
        """Test successful email sending"""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        test_report = "Test report content"
        
        result = self.agent.send_email_report(test_report)
        
        mock_smtp.assert_called_with('smtp.test.com', 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_with('testuser', 'testpass')
        mock_server.send_message.assert_called_once()
        assert result is True

    @patch('smtplib.SMTP')
    def test_send_email_report_failure(self, mock_smtp):
        """Test email sending failure"""
        mock_smtp.side_effect = Exception("SMTP error")
        
        test_report = "Test report content"
        
        result = self.agent.send_email_report(test_report)
        
        assert result is False
