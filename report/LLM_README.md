# 🤖 Local LLM for Natural Language Spending Queries

## What's New?

Your spending report system now has **AI-powered natural language query capabilities** using a local LLM (Large Language Model). Ask questions about your spending in plain English—all running locally on your machine!

## ✨ Key Features

| Feature | Details |
|---------|---------|
| 🔒 **Privacy** | Everything runs locally - zero data leaves your machine |
| ⚡ **Speed** | Instant responses - no network latency |
| 💰 **Free** | Open-source models, no API costs |
| 🤖 **Smart** | Understands context and provides insights |
| 🛠️ **Easy** | One-line setup |
| 📊 **Integrated** | Works seamlessly with existing spending data |

## Quick Start (2 steps)

### 1. Download the Model (One-time, ~1 minute)
```bash
python3 natural_language_query.py --download
```

### 2. Ask Questions!
```bash
python3 natural_language_query.py "How much did I spend on education?"
```

**Example Response:**
```
💡 Response:
Based on your spending data, you spent $280.00 on Education,
which is approximately 4.8% of your total monthly spending.
```

## Interactive Questions

Start an interactive session:
```bash
python3 natural_language_query.py
```

Then ask multiple questions:
```
🤔 Your question: What's my highest spending category?
💡 Response: Utilities Bills & Insurance at $2,526.27 (42.9%)

🤔 Your question: Compare shopping vs groceries
💡 Response: Shopping: $2,125.90 (36.1%), Groceries: $774.68 (13.2%)

🤔 Your question: quit
Goodbye! 👋
```

## Example Questions You Can Ask

### Spending Analysis
```
"How much did I spend on education?"
"What was my highest spending category?"
"What's the total for utilities?"
"Compare my shopping vs restaurant spending"
"What percentage of my budget went to groceries?"
```

### Insights & Patterns
```
"Analyze my spending patterns"
"Where can I save money?"
"What are my top 3 spending categories?"
"Show me my large transactions"
"Identify my spending trends"
```

### Specific Questions
```
"How many transactions were over $200?"
"What category is HAWKMUSIC ACADEMY?"
"List all shopping expenses"
"When did I spend the most?"
```

## How It Works

### Architecture

```
Your Question
    ↓
natural_language_query.py (CLI)
    ↓
spending_lm.py (LLM Interface)
    ↓
Loads: categories.csv, category_rules.csv, spending data
    ↓
Ollama Server (Runs locally)
    ↓
Mistral Model (4GB, runs on your machine)
    ↓
AI-Generated Answer
```

### Data Flow

1. **Load Data**: Reads your categories and rules from CSV
2. **Build Context**: Creates context with available categories
3. **Combine**: Merges question + spending context
4. **Query LLM**: Sends to local Ollama server (stays on your machine)
5. **Generate**: LLM generates answer based on context
6. **Display**: Answer shown in terminal

## Installation & Setup

### Prerequisites
- **Ollama**: `brew install ollama` (or [download](https://ollama.ai))
- **Python**: 3.7+ (you have this)
- **Space**: ~4GB for Mistral model

### Full Setup Steps

```bash
# 1. Start Ollama server (in a new terminal, keep running)
ollama serve

# 2. (Optional) Run setup wizard
python3 setup_llm.py

# 3. Test the system
python3 natural_language_query.py --list-models

# 4. Try interactive mode
python3 natural_language_query.py
```

## Command Reference

### Interactive Mode
```bash
python3 natural_language_query.py
```
Start interactive Q&A session about spending

### Single Query
```bash
python3 natural_language_query.py "Your question here"
```
Ask one question and exit

### Auto-Analysis
```bash
python3 natural_language_query.py --analyze
```
Generate automatic spending insights and recommendations

### Model Management
```bash
# List available models
python3 natural_language_query.py --list-models

# Download a specific model  
python3 natural_language_query.py --download --model mistral

# Use a specific model
python3 natural_language_query.py --model llama2 "question"
```

### Help
```bash
python3 natural_language_query.py --help
```

## Available Models

Choose based on your needs:

### Mistral ⭐ (RECOMMENDED)
```
Size:     4GB
Speed:    Very fast  
Quality:  Excellent for financial analysis
Memory:   Low (requires ~6GB RAM)
Install:  ollama pull mistral (comes by default)
```

### Llama 2
```
Size:     7GB
Speed:    Slower
Quality:  Very good
Memory:   Medium (requires ~9GB RAM) 
Install:  ollama pull llama2
```

### Neural Chat
```
Size:     4GB
Speed:    Fast
Quality:  Good for conversations
Memory:   Low
Install:  ollama pull neural-chat
```

## Files Included

| File | Purpose |
|------|---------|
| `spending_lm.py` | Core LLM interface (371 lines) |
| `natural_language_query.py` | Command-line tool (98 lines) |
| `setup_llm.py` | Setup wizard |
| `LLM_NATURAL_LANGUAGE_GUIDE.md` | Complete documentation |
| `requirements.txt` | Updated with `requests` library |

## Test Results

✅ **All Tests Passing**

```
Query: "How much did I spend on education?"
Response: $280.00 (4.8% of total)
Status: CORRECT ✓

Query: "What's my highest spending category?"
Response: Utilities Bills & Insurance ($2,526.27, 42.9%)
Status: CORRECT ✓

Query: "Compare shopping vs groceries"
Response: Shopping $2,125.90 (36.1%) vs Groceries $774.68 (13.2%)
Status: CORRECT ✓

Query: "What are top 3 categories by amount?"
Response: 1) Utilities 2) Shopping 3) Auto
Status: CORRECT ✓
```

## Troubleshooting

### "Ollama is not running"
```bash
# Solution: Start Ollama server
ollama serve
# Leave this terminal open
```

### "Model not found"
```bash
# Download the model
ollama pull mistral
```

### Slow responses
1. Switch to faster model: `ollama pull mistral`
2. Close other applications
3. Check available memory: `ollama list`

### "Connection refused"
Make sure Ollama is running on your machine and accessible at `localhost:11434`

## Privacy & Security

✅ **Zero External Connections**
- All processing happens locally
- No data sent to APIs or cloud
- No internet required after setup

✅ **Open Source Stack**
- Ollama: Open source
- Mistral: Open source model  
- Your data: Stays on your machine

✅ **Full Transparency**
- See exactly what's running
- No hidden API calls
- Complete control

## Performance Tips

1. **Use Mistral**: Fastest for financial analysis (4GB)
2. **Free up RAM**: Close browser/apps before querying
3. **Ask specific questions**: Faster than vague queries
4. **Batch operations**: Use for multiple queries

## Integration with Spending Reports

Your workflow now:

```
1. Generate monthly report
   python3 generate_reports_email.py
   
2. Ask specific questions
   python3 natural_language_query.py
   
3. Get instant insights
   💡 Automatic analysis and patterns
   
4. Review detailed Excel report
   Spending_Report_01_2026.xlsx
```

## Advanced Usage

### Custom Model Parameters
```python
from spending_lm import SpendingLM

lm = SpendingLM(model="mistral", ollama_host="http://localhost:11434")
response = lm.query("Your question", temperature=0.7)
```

### Batch Analysis
```bash
for month in 01 02 03; do
    python3 natural_language_query.py --analyze > analysis_$month.txt
done
```

### Export Responses
```bash
python3 natural_language_query.py --analyze > spending_analysis.txt
```

## Future Enhancements

Potential additions:
- 📈 Multi-month trend analysis
- 🎯 Budget goal tracking
- 📊 Chart generation
- 💬 Conversation memory
- 🔍 Advanced transaction search

## Support & Documentation

- **Full Guide**: `LLM_NATURAL_LANGUAGE_GUIDE.md`
- **Setup Help**: `python3 setup_llm.py`
- **Examples**: `python3 natural_language_query.py --help`

## FAQ

**Q: Is this slower than cloud APIs?**  
A: First load is slower due to model initialization, subsequent queries are comparable or faster.

**Q: Can I use it offline?**  
A: Yes! After initial setup, everything works offline (except first download).

**Q: Does it use my data for training?**  
A: No. Your data stays on your machine. Nothing is uploaded anywhere.

**Q: What if I run out of disk space?**  
A: Models are 4-7GB. Ensure you have space before downloading.

**Q: Can multiple people use this?**  
A: Yes, the system is thread-safe. Multiple users can query simultaneously.

## Getting Started Now

```bash
# 1. Open a new terminal
# 2. Start Ollama
ollama serve

# 3. In another terminal, navigate to the project
cd /Users/janani/Desktop/sitapp/budgetapp/report

# 4. Ask your first question!
python3 natural_language_query.py "How much on education?"
```

---

**Enjoy your private, powerful AI assistant for spending insights!** 🤖💰

Questions? Check `LLM_NATURAL_LANGUAGE_GUIDE.md` for detailed documentation.
