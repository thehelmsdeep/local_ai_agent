import json
import re

from brain import LocalBrain
from tools import TOOLS


TOOL_DESCRIPTIONS = [
    {"name": "open_calculator", "description": "Open Windows Calculator.", "args": {}},
    {"name": "list_windows", "description": "List visible top-level Windows window titles.", "args": {}},
    {"name": "focus_window", "description": "Focus a visible window by exact or partial title.", "args": {"title": "string"}},
    {"name": "click_element", "description": "Click a visible UI element by name inside a window.", "args": {"window_title": "string", "element_name": "string"}},
    {"name": "type_text", "description": "Type text into the currently focused control of a window.", "args": {"window_title": "string", "text": "string"}},
    {"name": "read_ui", "description": "Read visible UI text from a window.", "args": {"window_title": "string"}},
    {"name": "calculator", "description": "Open Calculator and enter a simple arithmetic expression.", "args": {"expression": "string"}},
]


class WindowsAgent:
    def __init__(self):
        self.brain = LocalBrain()

    def _observe(self):
        try:
            return json.dumps(TOOLS["list_windows"](), ensure_ascii=False)
        except Exception as exc:
            return f"Observation error: {exc}"

    @staticmethod
    def _normalize_task(task: str) -> str:
        text = task.strip()
        while text.lower().startswith("you >"):
            text = text[5:].strip()
        return text

    @staticmethod
    def _simple_calculator_task(task: str):
        text = WindowsAgent._normalize_task(task)
        match = re.fullmatch(
            r"(?:calculate|calc|محاسبه|حساب کن)\s+([0-9+\-*/().%\s]+)",
            text,
            re.IGNORECASE,
        )
        if match:
            return match.group(1).strip()
        return None

    def run(self, task: str) -> str:
        task = self._normalize_task(task)
        observation = self._observe()
        forced_tool = self._simple_calculator_task(task)

        for step in range(8):
            print(f"Agent [observe] > {observation}")

            if forced_tool is not None and step == 0:
                decision = {
                    "done": False,
                    "message": "Arithmetic task detected; using calculator.",
                    "tool": "calculator",
                    "args": {"expression": forced_tool},
                }
            else:
                decision = self.brain.think(
                    task,
                    observation,
                    TOOL_DESCRIPTIONS,
                    allow_done=step > 0 and "Tool error" not in observation,
                )

            print(f"Agent [think] > {decision.get('message', '')}")

            if decision.get("done"):
                return str(decision.get("message", "Task completed."))

            tool_name = decision.get("tool")
            args = decision.get("args") or {}

            if tool_name not in TOOLS:
                return f"Agent error: unknown tool '{tool_name}'."

            print(f"Agent [act] > {tool_name} {args}")

            try:
                result = TOOLS[tool_name](**args)
            except Exception as exc:
                result = f"Tool error: {exc}"

            observation = str(result)

        return "Agent stopped after reaching the planning step limit."


def main():
    print("Local AI Agent — Qwen + llama.cpp — type 'exit' to quit")
    print("Languages: Persian / English / Finglish / Mixed")

    agent = WindowsAgent()

    while True:
        try:
            task = input("\nYou > ")
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if task.strip().lower() == "exit":
            break

        try:
            print(f"Agent > {agent.run(task)}")
        except Exception as exc:
            print(f"Agent error > {exc}")


if __name__ == "__main__":
    main()
