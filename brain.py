import json
import os
import subprocess
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


class LocalBrain:
    """Small local planner powered by Qwen GGUF through llama.cpp."""

    def __init__(self):
        self.llama_cli = os.getenv("LLAMA_CLI_PATH", "llama-cli")
        self.model_path = Path(
            os.getenv(
                "LOCAL_MODEL_PATH",
                "models/qwen2.5-1.5b-instruct-q4_k_m.gguf",
            )
        )
        self.max_tokens = int(os.getenv("LOCAL_MAX_TOKENS", "256"))

    def available(self):
        return self.model_path.exists()

    def _prompt(self, task, observation, tools):
        tool_text = json.dumps(tools, ensure_ascii=False, indent=2)
        return f"""You are the planning brain of a Windows computer agent.
Understand Persian, English, Finglish, and mixed-language commands.
Choose ONE next action at a time. The Python agent will execute it and give you a new observation.
Never invent tool names. If the task is complete, return done=true.
Return ONLY valid JSON. No markdown.

Available tools:
{tool_text}

Current observation:
{observation}

User task:
{task}

JSON format:
{{"done":false,"message":"short reasoning/result","tool":"tool_name","args":{{}}}}
OR
{{"done":true,"message":"final answer"}}
"""

    def think(self, task, observation, tools):
        if not self.available():
            raise FileNotFoundError(
                f"Local model not found: {self.model_path}. Download the Qwen GGUF model first."
            )

        prompt = self._prompt(task, observation, tools)
        command = [
            self.llama_cli,
            "-m",
            str(self.model_path),
            "-n",
            str(self.max_tokens),
            "-p",
            prompt,
        ]

        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
        )

        if completed.returncode != 0:
            raise RuntimeError(completed.stderr.strip() or "llama.cpp failed")

        output = completed.stdout.strip()
        start = output.find("{")
        end = output.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ValueError(f"Local brain returned non-JSON output: {output[-500:]}")

        return json.loads(output[start : end + 1])
