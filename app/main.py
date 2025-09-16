# app.py (Streamlit Interface)
import streamlit as st
import os
from document_processor import DocumentProcessor
from rag_pipeline import RAGPipeline
from daily_agent import DailyAgent
import tempfile

# Initialize session state
if 'vectorstore' not in st.session_state:
    st.session_state.vectorstore = None
if 'rag_pipeline' not in st.session_state:
    st.session_state.rag_pipeline = None

def initialize_system():
    """Initialize the document processing system"""
    processor = DocumentProcessor()
    
    # Check if vector store exists
    vectorstore = processor.load_vectorstore()
    if vectorstore is None:
        st.warning("No vector store found. Please upload documents first.")
        return None, None
    
    rag_pipeline = RAGPipeline(vectorstore)
    return vectorstore, rag_pipeline

def main():
    st.title("🤖 Contract Management AI Assistant")
    
    # Sidebar for document upload
    st.sidebar.header("Document Management")
    uploaded_files = st.sidebar.file_uploader(
        "Upload contract documents",
        type=['pdf', 'docx', 'txt'],
        accept_multiple_files=True
    )
    
    if uploaded_files and st.sidebar.button("Process Documents"):
        with st.spinner("Processing documents..."):
            processor = DocumentProcessor()
            
            # Save uploaded files temporarily
            temp_dir = tempfile.mkdtemp()
            for file in uploaded_files:
                with open(os.path.join(temp_dir, file.name), "wb") as f:
                    f.write(file.getbuffer())
            
            # Process documents
            documents = processor.load_documents(temp_dir)
            if documents:
                chunked_docs = processor.chunk_documents(documents)
                vectorstore = processor.create_vectorstore(chunked_docs)
                st.session_state.vectorstore = vectorstore
                st.session_state.rag_pipeline = RAGPipeline(vectorstore)
                st.sidebar.success(f"Processed {len(documents)} documents successfully!")
            else:
                st.sidebar.error("No documents could be processed.")
    
    # Main interface
    tab1, tab2, tab3 = st.tabs(["Chatbot", "Document Similarity", "Daily Report"])
    
    with tab1:
        st.header("💬 Contract Chatbot")
        
        if st.session_state.rag_pipeline is None:
            st.info("Please upload and process documents first to use the chatbot.")
        else:
            question = st.text_input("Ask a question about your contracts:")
            
            if question:
                with st.spinner("Searching for relevant information..."):
                    result = st.session_state.rag_pipeline.query(question)
                    
                    st.subheader("Answer:")
                    st.write(result['answer'])
                    
                    if result['sources']:
                        st.subheader("Sources:")
                        for source in result['sources']:
                            st.write(f"• {source['document']} (Page {source['page']})")
    
    with tab2:
        st.header("📄 Document Similarity")
        
        if st.session_state.vectorstore is None:
            st.info("Please upload and process documents first.")
        else:
            doc_names = [meta['source'] for meta in st.session_state.vectorstore.get()['metadatas']]
            selected_doc = st.selectbox("Select a document:", list(set(doc_names)))
            
            if selected_doc and st.button("Find Similar Documents"):
                # Find document chunks
                similar_docs = st.session_state.vectorstore.similarity_search(
                    f"document about {selected_doc}", k=5
                )
                
                st.subheader("Similar Documents:")
                for i, doc in enumerate(similar_docs):
                    if doc.metadata['source'] != selected_doc:
                        st.write(f"{i+1}. {doc.metadata['source']}")
                        st.caption(f"Similarity score: {doc.metadata.get('score', 'N/A')}")
    
    with tab3:
        st.header("📊 Daily Report")
        
        if st.session_state.vectorstore is None:
            st.info("Please upload and process documents first.")
        else:
            email_config = {
                'from_email': 'contract-bot@example.com',
                'to_email': 'test@example.com',  # Test email
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'username': 'your-email@gmail.com',
                'password': 'your-app-password'
            }
            
            agent = DailyAgent(st.session_state.vectorstore, email_config)
            
            if st.button("Generate Daily Report"):
                with st.spinner("Generating report..."):
                    report = agent.generate_report()
                    st.text_area("Report Content:", report, height=400)
                    
                    if st.button("Send Report via Email"):
                        agent.send_email_report(report)
                        st.success("Report sent successfully!")

if __name__ == "__main__":
    main()
