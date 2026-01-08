from rag_system import RAGSystem
from typing import Dict, List, Optional
import re

class RAGChatbot:
    """RAG-based Chatbot using holdings and trades data"""
    
    def __init__(self, holdings_path: str, trades_path: str):
        """Initialize chatbot with data files"""
        self.rag_system = RAGSystem(holdings_path, trades_path)
        self.conversation_history = []
        self.max_history = 20
    
    def chat(self, query: str) -> str:
        """Process user query and generate response"""
        if not query or not query.strip():
            return "Please enter a valid question."
        
        # Check if query is relevant to the data
        if not self.rag_system.is_query_relevant(query):
            return "Sorry can not find the answer"
        
        # Extract query intent
        intent = self.rag_system.extract_intent(query)
        
        # Retrieve context and search data
        context = self.rag_system.retrieve_context(query)
        search_results = self.rag_system.search_data(query)
        
        # Generate response
        response = self._generate_response(query, intent, context, search_results)
        
        # Add to conversation history
        self._add_to_history(query, response)
        
        return response
    
    def _generate_response(self, query: str, intent: str, context: List[Dict], results: Dict) -> str:
        """Generate response based on intent and search results"""
        query_lower = query.lower()
        
        # Handle summary/overview queries
        if intent == "summary":
            return self._handle_summary_query(results)
        
        # Handle trade queries
        elif intent == "trade":
            return self._handle_trade_query(query, results)
        
        # Handle portfolio queries
        elif intent == "portfolio":
            return self._handle_portfolio_query(query, results)
        
        # General queries
        else:
            return self._handle_general_query(query, results, context)
    
    def _handle_summary_query(self, results: Dict) -> str:
        """Handle summary/overview queries"""
        if not results.get("both"):
            return "Sorry can not find the answer"
        
        summaries = results["both"]
        holdings_summary = None
        trades_summary = None
        
        for summary in summaries:
            if summary.get("type") == "holdings_summary":
                holdings_summary = summary.get("data", {})
            elif summary.get("type") == "trades_summary":
                trades_summary = summary.get("data", {})
        
        if holdings_summary and trades_summary:
            h_records = holdings_summary.get("total_records", 0)
            t_records = trades_summary.get("total_records", 0)
            return f"Data Summary: Holdings contains {h_records} records across multiple portfolios and securities. Trades contains {t_records} transaction records with buy/sell allocations."
        elif holdings_summary:
            return f"Holdings Summary: Total {holdings_summary.get('total_records', 0)} position records."
        elif trades_summary:
            return f"Trades Summary: Total {trades_summary.get('total_records', 0)} trade records."
        
        return "Sorry can not find the answer"
    
    def _handle_trade_query(self, query: str, results: Dict) -> str:
        """Handle trade-related queries"""
        if not results.get("trades"):
            # Check if general data exists
            if results.get("holdings") or results.get("both"):
                return "Trades data is available in the database. Query example: 'Show me trades for specific portfolio or security'."
            return "Sorry can not find the answer"
        
        trades = results["trades"]
        if trades:
            num_trades = len(trades)
            return f"Found {num_trades} relevant trade records in the database. Trades include buy/sell transactions with portfolio allocation details, custodian information, and settlement data."
        
        return "Sorry can not find the answer"
    
    def _handle_portfolio_query(self, query: str, results: Dict) -> str:
        """Handle portfolio-related queries"""
        if not results.get("holdings"):
            if results.get("trades") or results.get("both"):
                return "Portfolio data is available. Holdings include securities, bonds, equities, funds, and other assets across multiple portfolios."
            return "Sorry can not find the answer"
        
        holdings = results["holdings"]
        if holdings:
            num_holdings = len(holdings)
            return f"Found {num_holdings} portfolio holdings. The data includes various security types like equities, bonds, assets, and other instruments managed across different portfolios with custodians."
        
        return "Sorry can not find the answer"
    
    def _handle_general_query(self, query: str, results: Dict, context: List[Dict]) -> str:
        """Handle general queries"""
        # Check if we have search results
        if results.get("holdings") or results.get("trades"):
            if results.get("holdings"):
                return f"Found relevant holdings data. The database contains detailed portfolio and security information matching your query."
            elif results.get("trades"):
                return f"Found relevant trading data. The database contains transaction and allocation information matching your query."
        
        # Check if we have context from knowledge base
        if context:
            return f"Based on the data: {context[0].get('content', 'Information available in holdings and trades data.')}"
        
        return "Sorry can not find the answer"
    
    def _add_to_history(self, query: str, response: str):
        """Add query and response to conversation history"""
        self.conversation_history.append({
            "query": query,
            "response": response
        })
        
        # Maintain history size
        if len(self.conversation_history) > self.max_history:
            self.conversation_history.pop(0)
    
    def get_history(self) -> List[Dict]:
        """Get conversation history"""
        return self.conversation_history
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    def get_data_summary(self) -> Dict:
        """Get summary of available data"""
        return {
            "holdings_summary": self.rag_system.data_loader.get_holdings_summary(),
            "trades_summary": self.rag_system.data_loader.get_trades_summary()
        }
