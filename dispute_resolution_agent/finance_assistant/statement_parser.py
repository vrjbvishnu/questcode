"""
Statement Parser for Personal Finance Assistant
Extracts and standardizes data from various statement formats
"""

import re
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

class StatementParser:
    """
    Parses financial statements from various formats:
    - PDF text extraction
    - CSV transaction exports  
    - JSON API responses
    - Manual text input
    """
    
    def __init__(self):
        # Common patterns for extracting financial data
        self.patterns = {
            'balance': r'(?:balance|amount due|total)[:\s]*\$?([\d,]+\.?\d*)',
            'payment': r'(?:payment|paid)[:\s]*\$?([\d,]+\.?\d*)',
            'interest': r'(?:interest|finance charge)[:\s]*\$?([\d,]+\.?\d*)',
            'date': r'(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
            'amount': r'\$?([\d,]+\.\d{2})',
            'category': r'(dining|restaurant|gas|grocery|travel|shopping|retail)',
        }
    
    def parse_statement_text(self, statement_text: str) -> Dict[str, Any]:
        """
        Parse statement from raw text (OCR, copy-paste, etc.)
        
        Args:
            statement_text: Raw text from statement
            
        Returns:
            Structured statement data
        """
        statement_data = {
            'raw_text': statement_text,
            'parsed_at': datetime.now().isoformat(),
            'parsing_method': 'text_extraction'
        }
        
        # Extract key financial figures
        lines = statement_text.lower().split('\n')
        
        for line in lines:
            # Previous balance
            if 'previous balance' in line or 'last balance' in line:
                amount = self._extract_amount(line)
                if amount:
                    statement_data['previous_balance'] = amount
            
            # Current balance
            elif 'current balance' in line or 'new balance' in line:
                amount = self._extract_amount(line)
                if amount:
                    statement_data['current_balance'] = amount
            
            # Payments
            elif 'payment' in line and 'minimum' not in line:
                amount = self._extract_amount(line)
                if amount:
                    statement_data['payments'] = amount
            
            # Minimum payment
            elif 'minimum payment' in line:
                amount = self._extract_amount(line)
                if amount:
                    statement_data['minimum_payment'] = amount
            
            # Interest charges
            elif 'interest' in line or 'finance charge' in line:
                amount = self._extract_amount(line)
                if amount:
                    statement_data['interest_charged'] = amount
            
            # Due date
            elif 'due date' in line or 'payment due' in line:
                date = self._extract_date(line)
                if date:
                    statement_data['due_date'] = date
            
            # Credit limit
            elif 'credit limit' in line:
                amount = self._extract_amount(line)
                if amount:
                    statement_data['credit_limit'] = amount
            
            # Available credit
            elif 'available credit' in line:
                amount = self._extract_amount(line)
                if amount:
                    statement_data['available_credit'] = amount
        
        # Calculate missing fields
        statement_data = self._calculate_derived_fields(statement_data)
        
        return statement_data
    
    def parse_csv_transactions(self, csv_text: str) -> List[Dict[str, Any]]:
        """
        Parse transaction data from CSV export
        
        Args:
            csv_text: CSV content as string
            
        Returns:
            List of transaction dictionaries
        """
        transactions = []
        lines = csv_text.strip().split('\n')
        
        if not lines:
            return transactions
        
        # Assume first line is header
        headers = [h.strip().lower() for h in lines[0].split(',')]
        
        for line in lines[1:]:
            if not line.strip():
                continue
                
            values = [v.strip().strip('"') for v in line.split(',')]
            
            if len(values) != len(headers):
                continue  # Skip malformed lines
            
            transaction = {}
            for i, header in enumerate(headers):
                if i < len(values):
                    transaction[header] = values[i]
            
            # Standardize transaction format
            standardized = self._standardize_transaction(transaction)
            if standardized:
                transactions.append(standardized)
        
        return transactions
    
    def _extract_amount(self, text: str) -> Optional[float]:
        """Extract monetary amount from text"""
        # Remove common non-numeric characters and find amount
        amount_pattern = r'\$?([\d,]+\.?\d*)'
        matches = re.findall(amount_pattern, text)
        
        if matches:
            # Take the last/largest amount found
            amount_str = matches[-1].replace(',', '')
            try:
                return float(amount_str)
            except ValueError:
                return None
        return None
    
    def _extract_date(self, text: str) -> Optional[str]:
        """Extract date from text"""
        date_patterns = [
            r'(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})',
            r'(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2})',
            r'(\w{3,9}\s+\d{1,2},?\s+\d{4})'  # Month Day, Year
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return None
    
    def _standardize_transaction(self, transaction: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Standardize transaction format"""
        standard_fields = ['date', 'merchant', 'amount', 'category', 'description']
        standardized = {}
        
        # Map common field names
        field_mappings = {
            'date': ['date', 'transaction date', 'trans date'],
            'merchant': ['merchant', 'description', 'vendor', 'payee'],
            'amount': ['amount', 'debit', 'credit', 'transaction amount'],
            'category': ['category', 'type', 'classification'],
            'description': ['description', 'memo', 'details']
        }
        
        for standard_field, possible_names in field_mappings.items():
            for name in possible_names:
                if name in transaction:
                    value = transaction[name]
                    
                    # Clean up the value
                    if standard_field == 'amount':
                        # Convert to float
                        if isinstance(value, str):
                            value = value.replace('$', '').replace(',', '').replace('(', '-').replace(')', '')
                        try:
                            standardized[standard_field] = float(value)
                        except (ValueError, TypeError):
                            continue
                    else:
                        standardized[standard_field] = str(value).strip()
                    break
        
        # Only return if we have essential fields
        if 'amount' in standardized and ('merchant' in standardized or 'description' in standardized):
            return standardized
        
        return None
    
    def _calculate_derived_fields(self, statement_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate fields that can be derived from others"""
        
        # Calculate new charges if not present
        if ('new_charges' not in statement_data and 
            'current_balance' in statement_data and 
            'previous_balance' in statement_data and 
            'payments' in statement_data):
            
            new_charges = (statement_data['current_balance'] - 
                          statement_data['previous_balance'] + 
                          statement_data['payments'] - 
                          statement_data.get('interest_charged', 0))
            statement_data['new_charges'] = max(0, new_charges)
        
        # Calculate available credit if not present
        if ('available_credit' not in statement_data and 
            'credit_limit' in statement_data and 
            'current_balance' in statement_data):
            
            statement_data['available_credit'] = (statement_data['credit_limit'] - 
                                                statement_data['current_balance'])
        
        # Estimate interest rate if not present (and interest was charged)
        if ('interest_rate' not in statement_data and 
            'interest_charged' in statement_data and 
            'previous_balance' in statement_data and 
            statement_data['interest_charged'] > 0):
            
            # Rough monthly rate calculation
            monthly_rate = statement_data['interest_charged'] / statement_data['previous_balance']
            annual_rate = monthly_rate * 12
            statement_data['interest_rate'] = min(annual_rate, 0.30)  # Cap at 30%
        
        return statement_data
    
    def categorize_transactions(self, transactions: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Categorize transactions and sum by category
        
        Args:
            transactions: List of transaction dictionaries
            
        Returns:
            Dictionary of category totals
        """
        categories = {}
        
        # Category keywords
        category_keywords = {
            'Dining & Restaurants': ['restaurant', 'dining', 'food', 'cafe', 'pizza', 'burger', 'starbucks'],
            'Gas & Auto': ['gas', 'shell', 'chevron', 'exxon', 'bp', 'auto', 'car'],
            'Groceries': ['grocery', 'supermarket', 'whole foods', 'safeway', 'kroger', 'walmart'],
            'Shopping & Retail': ['amazon', 'target', 'walmart', 'mall', 'store', 'retail', 'shopping'],
            'Travel': ['airline', 'hotel', 'travel', 'uber', 'lyft', 'rental', 'airport'],
            'Utilities': ['electric', 'gas company', 'water', 'internet', 'phone', 'cable'],
            'Entertainment': ['movie', 'theater', 'netflix', 'spotify', 'game', 'entertainment'],
            'Healthcare': ['medical', 'doctor', 'pharmacy', 'hospital', 'health'],
            'Other': []
        }
        
        for transaction in transactions:
            amount = abs(transaction.get('amount', 0))  # Use absolute value
            merchant = transaction.get('merchant', '').lower()
            description = transaction.get('description', '').lower()
            existing_category = transaction.get('category', '').lower()
            
            # Check if category is already provided
            if existing_category:
                category = existing_category.title()
            else:
                # Categorize based on merchant/description
                category = 'Other'
                text_to_check = f"{merchant} {description}"
                
                for cat_name, keywords in category_keywords.items():
                    if any(keyword in text_to_check for keyword in keywords):
                        category = cat_name
                        break
            
            # Add to category total
            if category in categories:
                categories[category] += amount
            else:
                categories[category] = amount
        
        return categories

# Helper functions for easy statement parsing
def parse_statement_from_text(statement_text: str) -> Dict[str, Any]:
    """Quick function to parse statement from text"""
    parser = StatementParser()
    return parser.parse_statement_text(statement_text)

def parse_transactions_from_csv(csv_content: str) -> List[Dict[str, Any]]:
    """Quick function to parse transactions from CSV"""
    parser = StatementParser()
    return parser.parse_csv_transactions(csv_content)
