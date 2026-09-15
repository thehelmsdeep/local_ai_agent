import json
import os
import subprocess
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


class LocalBrain:
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

        self.max_tokens = int(
            os.getenv("LOCAL_MAX_TOKENS", "64")
        )

    def _base_command(self):
        executable = Path(self.llama_cli).name.lower()
        if executable in {"llama", "llama.exe"}:
            return [self.llama_cli, "cli"]
        return [self.llama_cli]

    def _model_args(self):
        if self.model_path.exists():
            return ["-m", str(self.model_path)]
        return ["-hf", self.model_ref]

    def _schema(self, tools):
        tool_names = [
            tool["name"]
            for tool in tools
            if isinstance(tool, dict) and isinstance(tool.get("name"), str)
        ]

        return {
            "type": "object",
            "properties": {
                "done": {
                    "type": "boolean"
                },
                "message": {
                    "type": "string"
                },
                "tool": {
                    "type": "string",
                    "enum": [""] + tool_names
                },
                "args": {
                    "type": "object"
                }
            },
            "required": [
                "done",
                "message",
                "tool",
                "args"
            ]
        }

    def _prompt(self, task, observation, tools):
        tools_json = json.dumps(
            tools,
            ensure_ascii=False,
            indent=2,
        )

        return f"""You are the planning brain of a Windows computer agent.
Understand Persian, English, Finglish, and mixed-language commands.

Your job is to decide the next action.

Available tools:
{tools_json}

Current observation:
{observation}

User task:
{task}

Rules:
1. If a tool is needed, set done=false.
2. Select exactly one tool from Available tools.
3. Use the exact tool name.
4. Put all tool parameters inside args.
5. If the task is already complete, set done=true and tool="".
6. Keep message short.
"""

    def think(self, task, observation, tools):
        prompt = self._prompt(task, observation, tools)
        schema = self._schema(tools)

        command = (
            self._base_command()
            + self._model_args()
            + [
                "-n",
                str(self.max_tokens),
                "-ngl",
                "0",
                "--no-jinja",
                "--single-turn",
                "--simple-io",
                "--json-schema",
                json.dumps(schema),
            ]
        )

        result = subprocess.run(
            command,
            input=prompt + "\n",
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"llama.cpp failed: {result.returncode}\n"
                f"STDOUT:\n{result.stdout[-1000:]}\n"
                f"STDERR:\n{result.stderr[-1000:]}"
            )

        output = result.stdout.strip()

        start = output.find("{")
        end = output.rfind("}")

        if start == -1 or end == -1 or end <= start:
            raise ValueError(
                "Local brain returned no JSON:\n"
                + output[-1000:]
            )

        try:
            data = json.loads(
                output[start:end + 1]
            )
        except json.JSONDecodeError as exc:
            raise ValueError(
                "Local brain returned invalid JSON:\n"
                + output[-1000:]
            ) from exc

        if not isinstance(data, dict):
            raise ValueError(
                "Local brain JSON is not an object:\n"
                + output[-1000:]
            )

        data["done"] = bool(
            data.get("done", False)
        )

        data["message"] = str(
            data.get("message", "")
        )

        tool = data.get("tool", "")
        if not isinstance(tool, str):
            tool = ""

        data["tool"] = tool.strip().lower()

        if not isinstance(data.get("args"), dict):
            data["args"] = {}

        valid_tools = {
            tool["name"].strip().lower()
            for tool in tools
            if isinstance(tool, dict)
            and isinstance(tool.get("name"), str)
        }

        if data["tool"] and data["tool"] not in valid_tools:
            raise ValueError(
                f"Unknown tool selected by local brain: {data['tool']}\n"
                f"Valid tools: {sorted(valid_tools)}"
            )

        if data["done"]:
            data["tool"] = ""
            data["args"] = {}

        return data
