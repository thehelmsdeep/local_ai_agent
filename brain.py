import json
import os
import subprocess
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


class LocalBrain:
    """Small local planner powered by Qwen GGUF through llama.cpp."""

    def __init__(self):
        self.llama_cli = os.getenv("LLAMA_CLI_PATH", "llama")
        self.model_path = Path(
            os.getenv(
                "LOCAL_MODEL_PATH",
                "models/qwen2.5-1.5b-instruct-q4_k_m.gguf",
            )
        )
        self.model_ref = os.getenv(
            "LOCAL_MODEL_REF",
            "Qwen/Qwen2.5-1.5B-Instruct-GGUF:Q4_K_M",
        )
        self.max_tokens = int(os.getenv("LOCAL_MAX_TOKENS", "256"))

    def _base_command(self):
        executable = Path(self.llama_cli).name.lower()
        if executable in {"llama", "llama.exe"}:
            return [self.llama_cli, "cli"]
        return [self.llama_cli]

    def _model_args(self):
        if self.model_path.exists():
            return ["-m", str(self.model_path)]
        return ["-hf", self.model_ref]

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
        prompt = self._prompt(task, observation, tools)
        command = self._base_command() + self._model_args() + [
            "-n",
            str(self.max_tokens),
            "-ngl",
            "0",
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
