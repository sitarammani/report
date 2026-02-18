# Copilot / AI Assistant Instructions

Purpose: short, actionable notes to help an AI agent be immediately productive in this repository.

1) Big picture
- This folder implements a standalone Spending Report System: CLI-first Python scripts, a local-LLM analysis layer, and an email/report generator. Core responsibilities are split across small scripts:
  - startup/launcher: `start.py` (checks deps, optionally starts Ollama, then runs `app.py`).
  - LLM layer: `spending_lm.py`, `natural_language_query.py`, `setup_llm.py` (interfaces with a local Ollama instance).
  - Reporting/email: `generate_reports_email.py` (uses Gmail OAuth2; see `README.md`).
  - Helpers: `metrics_logger.py`, `transaction_logger.py`, categorization CSVs (`categories.csv`, `category_rules.csv`).

2) Key invariants & conventions
- Runs locally. LLM integration uses an on-host Ollama server (HTTP at `http://localhost:11434`). Do not add network-API keys in code.
- Config and runtime artifacts live under the user config dir: `~/.config/SpendingApp/` (contains `config.json`, `logs/`, `token.json`).
- Preferred model: `mistral` (recommended for speed/size). Scripts default to `mistral` and often call `ollama pull mistral` when needed.
- Metrics and telemetry: calls into `metrics_logger.py` and `transaction_logger.py` are expected around LLM usage and categorization—keep those calls when modifying LLM interactions.

3) Developer workflows (commands you can run)
- Install deps: `pip install -r requirements.txt` (virtualenv recommended).
- Run app launcher: `python3 start.py` — does prechecks and then runs `app.py`.
- LLM setup: `python3 setup_llm.py` (verifies Ollama, pulls `mistral`, tests connection).
- Start Ollama server manually: `ollama serve` (required before LLM queries).
- Interactive LLM: `python3 natural_language_query.py` (or one-off: `python3 natural_language_query.py "How much on groceries?"`).
- Download model: `python3 natural_language_query.py --download` or `python3 setup_llm.py`.
- Run report/email generator: `python3 generate_reports_email.py` (follow the Gmail OAuth flow—put `credentials.json` in the repo dir before first run).

4) Integration points & external dependencies
- Ollama: required for all LLM features. Scripts call `ollama` CLI and the local HTTP endpoints `/api/tags` and `/api/generate` (see `spending_lm.py`).
- Gmail OAuth2: `generate_reports_email.py` expects `credentials.json` (downloaded from Google Cloud) and produces `token.json` after auth. README.md includes the exact steps.
- Python libs: `pandas`, `requests`, `openpyxl`, `xlsxwriter` (see `start.py` dependency checks and `requirements.txt`).

5) Project-specific patterns to follow
- Prompt construction lives in `spending_lm.py` (methods: `query()`, `compare_months_with_llm()`, `_build_context_with_transactions()`). When changing prompts, preserve how context is built (categories, rules, transactions) and ensure metrics logging (`metrics_logger`) remains.
- Data discovery: many scripts assume CSV files in the working dir (transaction statements, `categories.csv`, `category_rules.csv`, `category_map.csv`). Match existing heuristics for vendor/amount column detection (see `_build_context_with_transactions`).
- CLI-first edits: update help text and examples in `natural_language_query.py` and `setup_llm.py` when adding flags or altering behavior.

6) Examples (concrete edits / PR hints)
- To add a new LLM prompt variant, edit `spending_lm.py::query()` and add a metrics call: `metrics.log_llm_query_start(...)` and `metrics.log_llm_inference_complete(...)`.
- To add a new CLI flag for LLM analysis, mirror the pattern in `spending_lm.py`'s `argparse` block and update `natural_language_query.py` help text.

7) Quick checks for PR validation
- Run `python3 start.py` locally to exercise startup checks and any Ollama-related behavior.
- For LLM changes: ensure `ollama serve` is running and test with `python3 natural_language_query.py "test question" --model mistral`.
- For email/report changes: follow README.md's Gmail OAuth steps and run `python3 generate_reports_email.py`.

8) Where to look for more context
- High-level: [README.md](README.md)
- Startup: [start.py](start.py#L1-L200)
- LLM core: [spending_lm.py](spending_lm.py#L1-L120)
- LLM CLI & examples: [natural_language_query.py](natural_language_query.py#L1-L200)
- LLM setup: [setup_llm.py](setup_llm.py#L1-L200)
- Email/reporting notes: [README.md](README.md) and `generate_reports_email.py`

If anything in these notes is unclear or you want additional examples (unit tests, prompt templates, or a short runnable demo), tell me which part to expand.
