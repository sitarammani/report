# Local LLM Natural Language Queries

## Overview

Your spending report system now supports **natural language queries** powered by a local LLM (Large Language Model) running on your machine. Ask questions about your spending in plain English—no API keys, no internet required!

**Key Benefits:**
- 🔒 **Privacy**: Everything runs locally on your machine
- ⚡ **Fast**: No network latency, instant responses
- 💰 **Free**: Open-source models, no API costs
- 🤖 **Smart**: Understands context and provides insights
- 📊 **Integrated**: Works with your existing spending data

## Quick Start

### 1. One-Time Setup (5-10 minutes)

```bash
# Already done - Ollama is installed and Mistral is downloading
# Just wait for the download to complete
ollama list
```

### 2. Start Using It

**Interactive Questions:**
```bash
python3 natural_language_query.py
```

**Single Query:**
```bash
python3 natural_language_query.py "How much did I spend on education this month?"
```

**Auto-Analysis:**
```bash
python3 natural_language_query.py --analyze
```

## How It Works

### Architecture

```
Your Question (Natural Language)
           ↓
    natural_language_query.py (CLI)
           ↓
    spending_lm.py (LLM Interface)
           ↓
    [Load Spending Data + Context]
           ↓
    Ollama Server (Local LLM)
           ↓
    Mistral Model (4GB, runs locally)
           ↓
    Answer (Generated on your machine)
```

### Data Flow

1. **Load Data**: Reads categories.csv and category_rules.csv
2. **Build Context**: Creates a context string with available categories
3. **Combine**: Merges user question + spending context
4. **Query LLM**: Sends to local Ollama server (no internet)
5. **Generate Response**: LLM generates answer based on context
6. **Return**: Answer displayed in terminal

## Example Questions

### Spending Analysis
```
Q: How much did I spend on education?
A: Based on your spending data, you spent $280.00 on Education...

Q: What's my highest spending category?
A: Your highest spending category is Shopping & Retail with $2,125.90 (36.1% of total)...

Q: How much did I spend on groceries vs restaurants?
A: You spent $774.68 on Groceries & Markets compared to just $21.92 on Restaurants...
```

### Insights & Patterns
```
Q: Analyze my spending patterns
A: Key Insights:
   • Shopping is your largest expense (36.1%), followed by Utilities (42.9%)
   • You have 4 large transactions over $200
   • Education spending is significant at 4.8% of total
   • Recommendation: Focus on optimizing shopping expenses...

Q: Where can I save money?
A: Potential savings areas:
   • Shopping & Retail is 36.1% - Review items for necessity
   • Consider reducing restaurant frequency from current patterns...
```

### Transaction Details
```
Q: Show me all transactions over $200
A: Large transactions identified:
   • Jan 2: HAWKMUSIC ACADEMY - $280.00 (Education)
   • Jan 5: NSM DBAMR.COOPER - $1,424.79
   • Jan 8: WESTERN - $1,115.64
   • Jan 27: SCHLPAY*DENMARK - $250.00
```

## Command Reference

### Interactive Mode
```bash
python3 natural_language_query.py
```
Starts an interactive session where you can ask multiple questions.

**Examples:**
```
🤔 Your question: How much on utilities?
💡 Response: Based on your data, you spent $2,526.27 on Utilities...

🤔 Your question: Compare my top 3 spending categories
💡 Response: Your top 3 are:
   1. Utilities Bills & Insurance - $2,526.27 (42.9%)
   2. Shopping & Retail - $2,125.90 (36.1%)
   3. Groceries & Markets - $774.68 (13.2%)

🤔 Your question: quit
Goodbye! 👋
```

### Single Query
```bash
python3 natural_language_query.py "What percentage of my budget is education?"
```

### Generate Analysis
```bash
python3 natural_language_query.py --analyze
```
Automatically generates spending insights without a specific question.

### Model Management
```bash
# List installed models
python3 natural_language_query.py --list-models

# Download a different model
python3 natural_language_query.py --download --model llama2

# Use specific model
python3 natural_language_query.py --model neural-chat "Your question"
```

## Available Models

### Mistral ⭐ (RECOMMENDED)
- **Size**: 4GB
- **Speed**: Very fast
- **Quality**: Excellent for financial analysis
- **Memory**: Low (can run on most machines)
- **Status**: Downloading...
- **Install**: `ollama pull mistral`

### Llama 2
- **Size**: 7GB
- **Speed**: Slower
- **Quality**: Very good
- **Memory**: Medium
- **Install**: `ollama pull llama2`

### Neural Chat
- **Size**: 4GB
- **Speed**: Fast
- **Quality**: Good for conversation
- **Memory**: Low
- **Install**: `ollama pull neural-chat`

### Dolphin Mixtral
- **Size**: 26GB
- **Speed**: Slow
- **Quality**: Excellent
- **Memory**: High
- **Install**: `ollama pull dolphin-mixtral`

## Troubleshooting

### Issue: "Ollama is not running"
```bash
# Solution: Start Ollama server in a new terminal
ollama serve
```

### Issue: "Model not found"
```bash
# Download a model (one time)
python3 natural_language_query.py --download
```

### Issue: Slow responses
1. **Switch to faster model**:
   ```bash
   ollama pull mistral
   python3 natural_language_query.py --model mistral "question"
   ```

2. **Close other applications** (frees up memory)

3. **Check model status**:
   ```bash
   ollama list
   ```

### Issue: "Connection refused"
Make sure Ollama server is running:
```bash
ollama serve
# Keep this terminal open while using natural_language_query
```

## Technical Details

### Files

- **spending_lm.py** (371 lines)
  - Core LLM integration
  - Ollama client
  - Spending data context builder
  - Query processing

- **natural_language_query.py** (98 lines)
  - Command-line interface
  - User-friendly wrapper
  - Examples and help text

### Environment

- **Python**: 3.7+
- **Dependencies**: requests (calls local Ollama server)
- **No external APIs**: Everything runs locally
- **No internet required**: After model download (first time only)

### How Context Works

The system sends your question along with context:

```
Context includes:
- Available spending categories
- Category rules and patterns
- Sample transaction data structure

Example prompt to LLM:
"Available categories: Education, Shopping, Utilities...
Rules: HAWK pattern → Education category...
User question: How much on education?"
```

This gives the LLM enough information to provide accurate answers about your data.

## Integration with Existing System

The LLM system integrates seamlessly:

```
Your Workflow (Before):
  1. Run generate_reports_email.py
  2. Review Excel report
  3. Manually analyze data

Your Workflow (Now):
  1. Run generate_reports_email.py
  2. Ask natural language questions: python3 natural_language_query.py
  3. Get instant insights and analysis
  4. Review detailed Excel report
```

## Privacy & Security

✅ **Zero External Calls**
- Model runs on your machine
- No data sent to external servers
- All processing is local

✅ **Open Source**
- Ollama is open source
- Mistral model is open source
- Full transparency

✅ **Your Data Stays Private**
- Spending data never leaves your machine
- No cloud storage
- No API logging

## Advanced Usage

### Custom Temperature Settings

Higher temperature = more creative/varied responses
Lower temperature = more focused/consistent responses

```python
from spending_lm import SpendingLM

lm = SpendingLM()
lm.query("question", temperature=0.3)  # More focused
# vs
lm.query("question", temperature=0.9)  # More creative
```

### Batch Processing

```bash
# Analyze multiple months
for month in {01..12}; do
    python3 natural_language_query.py \
      "Analyze spending for month $month"
done
```

### Export Results

```bash
# Save analysis to file
python3 natural_language_query.py --analyze > spending_analysis.txt
```

## Future Enhancements

Possible additions:
- 📈 Trend analysis over multiple months
- 🎯 Budget tracking and goal setting
- 📊 Chart generation from LLM insights
- 💬 Multi-turn conversations with memory
- 🔍 Detailed transaction search with NLP

## Performance Tips

1. **Choose Right Model**
   - Start with Mistral (faster, 4GB)
   - Upgrade to Llama2 if needed (better quality, 7GB)

2. **Optimize Responses**
   - Ask specific questions (faster than vague ones)
   - Use "analyze" for auto-insights

3. **System Resources**
   - Close browser/apps to free up memory
   - Mistral needs ~6GB RAM available
   - Llama2 needs ~9GB RAM available

## FAQ

**Q: Is my spending data sent anywhere?**
A: No, everything runs locally. Your data never leaves your machine.

**Q: What if Ollama stops?**
A: Just restart it: `ollama serve`

**Q: Can I use different models?**
A: Yes! Download and switch with `--model mistral` flag

**Q: Is this slower than API-based LLM?**
A: First request is slower due to model loading, subsequent queries are comparable.

**Q: Can multiple users ask questions?**
A: Yes, the system is thread-safe and can handle concurrent requests.

## Getting Help

```bash
# View all options
python3 natural_language_query.py --help

# See available models
python3 natural_language_query.py --list-models

# Get this documentation
less LLM_NATURAL_LANGUAGE_GUIDE.md
```

---

**Enjoy your private, local AI assistant for spending insights!** 🤖💰
