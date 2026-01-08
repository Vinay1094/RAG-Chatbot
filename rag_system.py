from data_loader import DataLoader
from typing import List, Dict, Tuple
import re
from difflib import SequenceMatcher

class RAGSystem:
    """Retrieval-Augmented Generation system for the chatbot"""
    
    def __init__(self, holdings_path: str, trades_path: str):
        self.data_loader = DataLoader(holdings_path, trades_path)
        self.knowledge_base = self._build_knowledge_base()
        self.relevant_keywords = self._build_keyword_mapping()
    
    def _build_knowledge_base(self) -> List[Dict]:
        """Build searchable knowledge base from data"""
        kb = []
        
        # Add holdings insights
        holdings_summary = self.data_loader.get_holdings_summary()
        if holdings_summary:
            kb.append({
                "type": "summary",
                "source": "holdings",
                "content": f"Holdings data contains {holdings_summary.get('total_records', 0)} portfolio records",
                "keywords": ["holdings", "portfolio", "security", "asset", "position", "quantity"],
                "relevance": 0.9
            })
        
        # Add trades insights
        trades_summary = self.data_loader.get_trades_summary()
        if trades_summary:
            kb.append({
                "type": "summary",
                "source": "trades",
                "content": f"Trades data contains {trades_summary.get('total_records', 0)} transaction records",
                "keywords": ["trades", "transaction", "buy", "sell", "transaction", "allocation"],
                "relevance": 0.9
            })
        
        return kb
    
    def _build_keyword_mapping(self) -> Dict[str, list]:
        """Build mapping of keywords to data types"""
        return {
            "portfolio": ["holdings", "PortfolioName"],
            "trade": ["trades", "TradeTypeNameSecurityIdSecurityTypeNameTickerCUSIPISINTradeDateSettleDate"],
            "transaction": ["trades", "Buy", "Sell"],
            "buy": ["trades", "Buy"],
            "sell": ["trades", "Sell"],
            "security": ["holdings", "SecurityTypeNameSecNameStartQtyStartPrice"],
            "bond": ["holdings", "Bond"],
            "equity": ["holdings", "Equity"],
            "asset": ["holdings", "asset", "position"],
            "allocation": ["trades", "AllocationQTY"],
            "custodian": ["trades", "CustodianName"],
            "strategy": ["both", "Strategy"],
            "price": ["holdings", "Price"],
            "quantity": ["holdings", "Qty"],
            "fund": ["holdings", "Fund Holding"],
            "option": ["holdings", "Option"],
            "loan": ["holdings", "Loan"],
            "repo": ["holdings", "Repo"],
            "swap": ["holdings", "Swap"],
            "summary": ["both", "overview"],
            "total": ["both", "count"],
            "count": ["both", "records"],
        }
    
    def retrieve_context(self, query: str, top_k: int = 3) -> List[Dict]:
        """Retrieve relevant context from knowledge base"""
        query_lower = query.lower()
        scores = []
        
        for idx, item in enumerate(self.knowledge_base):
            score = 0
            # Check keyword matches
            for keyword in item.get('keywords', []):
                if keyword in query_lower:
                    score += 1
            
            # Add relevance score
            score += item.get('relevance', 0.5)
            scores.append((idx, score))
        
        scores.sort(key=lambda x: x[1], reverse=True)
        return [self.knowledge_base[idx] for idx, _ in scores[:top_k] if _ > 0]
    
    def search_data(self, query: str) -> Dict:
        """Search data based on query intent"""
        query_lower = query.lower()
        results = {"holdings": [], "trades": [], "both": []}
        
        # Portfolio/holdings queries
        if any(word in query_lower for word in ["portfolio", "holding", "position", "security", "asset"]):
            results["holdings"] = self.data_loader.search_holdings(query_lower)[:3]
        
        # Trade/transaction queries
        if any(word in query_lower for word in ["trade", "transaction", "buy", "sell", "allocation"]):
            results["trades"] = self.data_loader.search_trades(query_lower)[:3]
        
        # Summary/overview queries
        if any(word in query_lower for word in ["summary", "overview", "total", "count", "records"]):
            results["both"] = [
                {"type": "holdings_summary", "data": self.data_loader.get_holdings_summary()},
                {"type": "trades_summary", "data": self.data_loader.get_trades_summary()}
            ]
        
        return results
    
    def is_query_relevant(self, query: str) -> bool:
        """Check if query is relevant to the data"""
        query_lower = query.lower()
        
        # List of all relevant keywords
        relevant_keywords = [
            "holdings", "portfolio", "security", "trade", "transaction",
            "buy", "sell", "bond", "equity", "fund", "asset", "position",
            "quantity", "qty", "price", "allocation", "custodian", "strategy",
            "loan", "option", "repo", "swap", "cds", "summary", "total",
            "count", "records", "data", "portfolio", "cash", "dividend",
            "coupon", "principal", "interest"
        ]
        
        # Check if query contains at least one relevant keyword
        return any(keyword in query_lower for keyword in relevant_keywords)
    
    def extract_intent(self, query: str) -> str:
        """Extract the intent of the query"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["summary", "overview", "total"]):
            return "summary"
        elif any(word in query_lower for word in ["buy", "sell", "trade", "transaction"]):
            return "trade"
        elif any(word in query_lower for word in ["portfolio", "holding", "position"]):
            return "portfolio"
        else:
            return "general"
