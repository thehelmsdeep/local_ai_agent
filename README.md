# Windows Agent

A local-first AI agent for controlling and interacting with Windows applications.

The project combines a small local language model with Windows UI automation so the agent can understand a task, observe the current Windows state, choose a tool, perform an action, and continue until the task is completed.

## Vision

Build a practical Windows AI agent that can understand:

- Persian
- English
- Finglish
- Mixed Persian / English commands

The long-term goal is to turn the prototype into a standalone Windows application that can interact with everyday desktop software through natural language.

## Architecture

```text
User
  ↓
Persian / English / Finglish / Mixed
  ↓
Local Brain (Qwen)
  ↓
Agent Planner
  ↓
Observe 👀
  ↓
Choose Tool 🧠
  ↓
Act 🖱️⌨️
  ↓
Verify ✅
  ↺
```

## Current Stack

- **Python** — agent runtime
- **Qwen2.5-1.5B-Instruct** — local language model
- **llama.cpp** — local GGUF model runtime
- **pywinauto** — Windows UI Automation
- **PyAutoGUI** — mouse and keyboard automation
- **pyperclip** — clipboard support
- **python-dotenv** — local configuration

No OpenAI API key or Ollama is required.

## Current Capabilities

The current prototype includes tools for:

- Opening Calculator
- Listing visible Windows
- Focusing a Windows application
- Reading UI text
- Clicking UI elements
- Typing text
- Performing calculator operations

The agent uses an iterative loop:

**Observe → Think → Act → Observe → ...**

## Requirements

- Windows 10/11
- Python 3.11+
- llama.cpp installed and available as `llama`
- Enough RAM to run the selected local model

## Installation

Clone the repository:

```bash
git clone https://github.com/thehelmsdeep/windows_agent.git
cd windows_agent
```

Create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

Install Python dependencies:

```powershell
pip install -r requirements.txt
```

## Local Model

The agent uses Qwen2.5-1.5B-Instruct in GGUF format through llama.cpp.

You can test the model directly with:

```powershell
llama cli -hf Qwen/Qwen2.5-1.5B-Instruct-GGUF:Q4_K_M
```

On the first run, llama.cpp may download the model automatically.

## Configuration

Copy the example environment file:

```powershell
copy .env.example .env
```

Default configuration:

```env
LLAMA_CLI_PATH=llama
LOCAL_MODEL_PATH=models/qwen2.5-1.5b-instruct-q4_k_m.gguf
LOCAL_MODEL_REF=Qwen/Qwen2.5-1.5B-Instruct-GGUF:Q4_K_M
LOCAL_MAX_TOKENS=256
```

If the local GGUF file does not exist, the agent can use the Hugging Face model reference through llama.cpp.

## Run

Start the agent:

```powershell
python main.py
```

Then enter a natural-language task, for example:

```text
7 + 5 رو داخل Calculator حساب کن
```

or:

```text
Open Calculator and calculate 25 * 4
```

## Project Structure

```text
windows_agent/
├── brain.py          # Local Qwen + llama.cpp brain
├── main.py           # Agent loop and planner
├── tools.py          # Windows automation tools
├── .env.example      # Configuration template
├── requirements.txt  # Python dependencies
└── README.md
```

## Roadmap

- [x] Local agent loop
- [x] Windows UI observation
- [x] Mouse and keyboard actions
- [x] Calculator automation
- [x] Local Qwen planner
- [x] Persian / English / Finglish prompt support
- [ ] Better task planning
- [ ] Stronger verification and recovery
- [ ] More Windows application tools
- [ ] Persistent memory
- [ ] Permission and safety layer
- [ ] Background agent mode
- [ ] Standalone Windows GUI
- [ ] Packaged Windows executable

## Project Status

**Early prototype.**

The current version is intended for development and testing in VS Code. The architecture is deliberately kept modular so the local brain, planner, tools, and future GUI can evolve independently.

## License

License will be added as the project matures.
