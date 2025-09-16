# Contract_management_system_using_llm
# Contract Management AI System

An intelligent system for managing contracts with AI-powered monitoring, querying, and reporting.

## Features

- Document ingestion and processing (PDF, DOCX, TXT)
- RAG-powered chatbot with source citation
- Daily contract expiration monitoring
- Conflict detection across documents
- Document similarity search
- Email reporting system

## Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and configure your settings
4. Add your contract documents to the `data/sample_documents/` folder
5. Run the application: `streamlit run app/main.py`

## Usage

### Daily Monitoring
The system can be set up to run daily checks automatically:
```bash
python scripts/daily_run.py
