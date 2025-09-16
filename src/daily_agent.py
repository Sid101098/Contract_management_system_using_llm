
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import re
from langchain.llms import OpenAI
import logging

class DailyAgent:
    def __init__(self, vectorstore, email_config):
        self.vectorstore = vectorstore
        self.llm = OpenAI(temperature=0)
        self.email_config = email_config
        self.contract_data = {}
    
    def extract_contract_dates(self):
        """Extract contract dates from all documents"""
        try:
            # Search for date patterns in documents
            all_docs = self.vectorstore.get()['documents']
            all_metadatas = self.vectorstore.get()['metadatas']
            
            date_patterns = [
                r'expiration date:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                r'expires:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                r'end date:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                r'termination date:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
            ]
            
            approaching_expirations = []
            today = datetime.now()
            threshold = today + timedelta(days=30)
            
            for doc, metadata in zip(all_docs, all_metadatas):
                document_name = metadata.get('source', 'Unknown')
                
                for pattern in date_patterns:
                    matches = re.finditer(pattern, doc.lower())
                    for match in matches:
                        date_str = match.group(1)
                        try:
                            # Parse date (simple implementation - would need better date parsing)
                            if '/' in date_str:
                                parts = date_str.split('/')
                                if len(parts[2]) == 2:
                                    parts[2] = '20' + parts[2]
                                contract_date = datetime.strptime('/'.join(parts), '%m/%d/%Y')
                            elif '-' in date_str:
                                parts = date_str.split('-')
                                if len(parts[2]) == 2:
                                    parts[2] = '20' + parts[2]
                                contract_date = datetime.strptime('-'.join(parts), '%m-%d-%Y')
                            
                            if today <= contract_date <= threshold:
                                approaching_expirations.append({
                                    'document': document_name,
                                    'date': contract_date.strftime('%Y-%m-%d'),
                                    'days_until_expiration': (contract_date - today).days
                                })
                                
                        except ValueError:
                            continue
            
            return approaching_expirations
            
        except Exception as e:
            logging.error(f"Error extracting contract dates: {e}")
            return []
    
    def detect_conflicts(self):
        """Detect conflicting information across documents"""
        conflicts = []
        
        try:
            # Extract company information and addresses
            all_docs = self.vectorstore.get()['documents']
            all_metadatas = self.vectorstore.get()['metadatas']
            
            company_data = {}
            
            for doc, metadata in zip(all_docs, all_metadatas):
                document_name = metadata.get('source', 'Unknown')
                
                # Extract company names and addresses (simplified)
                company_matches = re.finditer(r'company:?\s*([^\n]+)', doc.lower())
                address_matches = re.finditer(r'address:?\s*([^\n]+)', doc.lower())
                
                for match in company_matches:
                    company_name = match.group(1).strip()
                    if company_name not in company_data:
                        company_data[company_name] = {'addresses': {}, 'documents': []}
                    
                    company_data[company_name]['documents'].append(document_name)
                
                for match in address_matches:
                    address = match.group(1).strip()
                    if company_name in company_data:
                        if address not in company_data[company_name]['addresses']:
                            company_data[company_name]['addresses'][address] = []
                        company_data[company_name]['addresses'][address].append(document_name)
            
            # Check for conflicts
            for company, data in company_data.items():
                if len(data['addresses']) > 1:
                    conflict = {
                        'company': company,
                        'issue': 'Multiple addresses found for the same company',
                        'addresses': data['addresses'],
                        'documents': list(set(data['documents']))
                    }
                    conflicts.append(conflict)
                    
        except Exception as e:
            logging.error(f"Error detecting conflicts: {e}")
        
        return conflicts
    
    def generate_report(self):
        """Generate daily report"""
        expirations = self.extract_contract_dates()
        conflicts = self.detect_conflicts()
        
        report = f"Daily Contract Management Report\n"
        report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        report += "=== APPROACHING CONTRACT EXPIRATIONS (Next 30 days) ===\n"
        if expirations:
            for exp in expirations:
                report += f"• {exp['document']}: Expires on {exp['date']} ({exp['days_until_expiration']} days)\n"
        else:
            report += "No contracts expiring in the next 30 days.\n"
        
        report += "\n=== CONFLICTS DETECTED ===\n"
        if conflicts:
            for conflict in conflicts:
                report += f"• Company: {conflict['company']}\n"
                report += f"  Issue: {conflict['issue']}\n"
                report += f"  Documents involved: {', '.join(conflict['documents'])}\n"
                for addr, docs in conflict['addresses'].items():
                    report += f"  Address '{addr}' found in: {', '.join(docs)}\n"
        else:
            report += "No conflicts detected.\n"
        
        return report
    
    def send_email_report(self, report):
        """Send email report"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config['from_email']
            msg['To'] = self.email_config['to_email']
            msg['Subject'] = f"Daily Contract Management Report - {datetime.now().strftime('%Y-%m-%d')}"
            
            msg.attach(MIMEText(report, 'plain'))
            
            with smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port']) as server:
                server.starttls()
                server.login(self.email_config['username'], self.email_config['password'])
                server.send_message(msg)
            
            logging.info("Email report sent successfully")
            
        except Exception as e:
            logging.error(f"Error sending email: {e}")
    
    def run_daily_check(self):
        """Run the daily check and send report"""
        logging.info("Running daily contract check...")
        report = self.generate_report()
        self.send_email_report(report)
        return report
