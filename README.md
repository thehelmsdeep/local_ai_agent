# Local AI Agent

A minimal local-first AI agent prototype.

## Goal

Run an agent locally, give it a task, let it reason through a simple tool loop, and keep the project easy to extend.

## Requirements

- Python 3.11+

## Run

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Configuration

Set `OPENAI_API_KEY` if you want to use an OpenAI-compatible LLM. Without a key, the project runs in demo mode so the basic agent loop can be tested locally.

## Current prototype

- CLI interface
- Agent loop
- Tool registry
- Calculator tool
- Local demo mode
- Optional LLM integration
