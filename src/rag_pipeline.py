
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import BaseRetriever
import logging

class RAGPipeline:
    def __init__(self, vectorstore):
        self.vectorstore = vectorstore
        self.llm = OpenAI(temperature=0)
        self.retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5}
        )
        
        self.prompt_template = PromptTemplate(
            template="""You are a contract management assistant. Use the following context to answer the question.
            Always cite your sources by mentioning the document name and page number when available.

            Context: {context}

            Question: {question}

            Answer:""",
            input_variables=["context", "question"]
        )
    
    def query(self, question):
        """Query the RAG pipeline"""
        try:
            # Retrieve relevant documents
            relevant_docs = self.retriever.get_relevant_documents(question)
            
            # Format context with source information
            context = ""
            for doc in relevant_docs:
                source = doc.metadata.get('source', 'Unknown document')
                page_info = f" (Page {doc.metadata.get('page', 'N/A')})" if 'page' in doc.metadata else ""
                context += f"From {source}{page_info}:\n{doc.page_content}\n\n"
            
            # Generate answer
            prompt = self.prompt_template.format(context=context, question=question)
            answer = self.llm(prompt)
            
            # Extract sources for citation
            sources = []
            for doc in relevant_docs:
                source_info = {
                    "document": doc.metadata.get('source', 'Unknown'),
                    "page": doc.metadata.get('page', 'N/A')
                }
                if source_info not in sources:
                    sources.append(source_info)
            
            return {
                "answer": answer,
                "sources": sources,
                "relevant_documents": relevant_docs
            }
            
        except Exception as e:
            logging.error(f"Error in RAG query: {e}")
            return {
                "answer": "Sorry, I encountered an error while processing your query.",
                "sources": [],
                "relevant_documents": []
            }
