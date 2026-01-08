#!/usr/bin/env python3
"""
RAG-Chatbot Main Application
A Retrieval-Augmented Generation chatbot for holdings and trades data
"""

from chatbot import RAGChatbot
import sys

def main_interactive():
    """Run chatbot in interactive mode"""
    print("\n" + "="*70)
    print("RAG CHATBOT - Interactive Mode")
    print("="*70)
    print("\nWelcome! Ask questions about holdings and trades data.")
    print("Commands: 'quit' to exit, 'history' to see conversation history\n")
    
    # Initialize chatbot
    try:
        chatbot = RAGChatbot("holdings.csv", "trades.csv")
    except FileNotFoundError:
        print("Error: Could not find holdings.csv or trades.csv files.")
        print("Please ensure both CSV files are in the current directory.")
        return
    
    # Chat loop
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            # Handle special commands
            if user_input.lower() == 'quit':
                print("\nGoodbye!\n")
                break
            
            if user_input.lower() == 'history':
                history = chatbot.get_history()
                if history:
                    print("\n--- Conversation History ---")
                    for idx, item in enumerate(history, 1):
                        print(f"{idx}. Q: {item['query']}")
                        print(f"   A: {item['response']}\n")
                else:
                    print("No conversation history yet.\n")
                continue
            
            if user_input.lower() == 'summary':
                summary = chatbot.get_data_summary()
                print(f"\nData Summary:")
                print(f"Holdings: {summary.get('holdings_summary', {})}")
                print(f"Trades: {summary.get('trades_summary', {})}\n")
                continue
            
            # Generate response
            response = chatbot.chat(user_input)
            print(f"Bot: {response}\n")
        
        except KeyboardInterrupt:
            print("\n\nGoodbye!\n")
            break
        except Exception as e:
            print(f"Error: {str(e)}\n")

def demo_mode():
    """Run chatbot in demo mode with predefined questions"""
    print("\n" + "="*70)
    print("RAG CHATBOT - DEMO MODE")
    print("="*70 + "\n")
    
    # Initialize chatbot
    try:
        chatbot = RAGChatbot("holdings.csv", "trades.csv")
    except FileNotFoundError:
        print("Error: Could not find holdings.csv or trades.csv files.")
        return
    
    # Demo queries
    demo_queries = [
        "What portfolios are in the holdings data?",
        "Tell me about trades in the database",
        "Show me a summary of the data",
        "What securities are available?",
        "Tell me about the weather today"  # This should trigger fallback
    ]
    
    for query in demo_queries:
        print(f"Q: {query}")
        response = chatbot.chat(query)
        print(f"A: {response}")
        print("-" * 70 + "\n")

if __name__ == "__main__":
    # Run interactive mode by default
    # Use 'python main.py demo' for demo mode
    if len(sys.argv) > 1 and sys.argv[1] == 'demo':
        demo_mode()
    else:
        main_interactive()
