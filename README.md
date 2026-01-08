# RAG-Chatbot

A Retrieval-Augmented Generation (RAG) based chatbot trained on holdings and trades data. The bot can answer questions related to portfolio positions, transactions, securities, and allocations from the provided CSV files.

## Features

✅ **RAG Architecture**: Retrieves relevant information from your CSV files before generating responses  
✅ **Intelligent Query Understanding**: Identifies user intent (summary, trades, portfolio, general)  
✅ **Fallback Response**: Returns "Sorry can not find the answer" for out-of-domain queries  
✅ **Context-Aware**: Understands questions about portfolios, trades, securities, and allocations  
✅ **Conversation History**: Maintains previous interactions  
✅ **Error Handling**: Graceful handling of invalid inputs  
✅ **Flexible Search**: Searches both holdings and trades data based on query intent  

## Architecture

The chatbot is built with a modular architecture:

```
data_loader.py       -> Loads and manages CSV data
    ↓
rag_system.py        -> RAG engine with query understanding
    ↓
chatbot.py           -> Main chatbot class with response generation
    ↓
main.py              -> Application entry point
```

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Vinay1094/RAG-Chatbot.git
   cd RAG-Chatbot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Place CSV files**
   - `holdings.csv` - Portfolio holdings data
   - `trades.csv` - Trading transactions data

## Usage

### Interactive Mode
```bash
python main.py
```

Then ask questions:
```
You: What portfolios are in the holdings?
Bot: Found relevant holdings data. The database contains detailed portfolio and security information matching your query.

You: Tell me about trades
Bot: Found relevant trading data. The database contains transaction and allocation information matching your query.

You: Show me a summary
Bot: Data Summary: Holdings contains XXXX records across multiple portfolios and securities. Trades contains XXXX transaction records with buy/sell allocations.
```

### Demo Mode
```bash
python main.py demo
```

Runs predefined sample queries.

## Special Commands

- `quit` - Exit the chatbot
- `history` - View conversation history
- `summary` - Get data summary statistics

## Query Examples

The chatbot handles various query types:

**Portfolio Queries:**
- "What portfolios are in the holdings?"
- "Show me the portfolio positions"
- "Which securities are in the portfolio?"

**Trade Queries:**
- "Tell me about trades in the database"
- "Show me recent transactions"
- "What buy/sell orders are there?"

**Summary Queries:**
- "Show me a summary of the data"
- "How many records are in the database?"
- "What's the total count of holdings?"

**Out-of-Domain Queries:**
- "Tell me about the weather" → "Sorry can not find the answer"
- "What's the stock market news?" → "Sorry can not find the answer"

## File Structure

```
RAG-Chatbot/
├── data_loader.py       # Data loading and management
├── rag_system.py        # RAG engine and query understanding
├── chatbot.py           # Main chatbot class
├── main.py              # Application entry point
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

## Key Components

### DataLoader
- Loads holdings and trades data from CSV files
- Provides summary statistics
- Implements search functionality

### RAGSystem
- Builds knowledge base from data
- Retrieves relevant context
- Extracts query intent
- Checks query relevance

### RAGChatbot
- Orchestrates RAG system
- Generates context-aware responses
- Maintains conversation history
- Handles different query types

## Dependencies

- **pandas** >= 2.0.0 - Data manipulation and analysis
- **numpy** >= 1.24.0 - Numerical computing

## How It Works

1. **User Query** → Chatbot receives user question
2. **Relevance Check** → Determines if query relates to data
3. **Intent Extraction** → Identifies query type (summary/trade/portfolio)
4. **Context Retrieval** → Retrieves relevant information from knowledge base
5. **Data Search** → Searches holdings and trades data
6. **Response Generation** → Generates context-aware response
7. **History Management** → Adds to conversation history

## Response Logic

- ✅ **Relevant Query** → Searches data and provides information
- ❌ **Irrelevant Query** → Returns "Sorry can not find the answer"
- 📊 **Summary Query** → Provides data statistics
- 💹 **Trade Query** → Shows transaction information
- 📁 **Portfolio Query** → Shows holdings information

## Limitations

- Answers are limited to the provided CSV data
- No internet access for external data
- Limited to English language queries
- Response quality depends on data quality and completeness

## Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest improvements
- Add new features
- Improve documentation

## License

MIT License - Feel free to use this project for your needs.

## Author

Vinay Singh - AI Trainer & Prompt Engineer  
[GitHub Profile](https://github.com/Vinay1094)
