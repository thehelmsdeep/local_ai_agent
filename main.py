import ast
import json

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
    def _safe_calculate(expression: str):
        tree = ast.parse(expression, mode="eval")

        def evaluate(node):
            if isinstance(node, ast.Expression):
                return evaluate(node.body)
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                return node.value
            if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
                value = evaluate(node.operand)
                return value if isinstance(node.op, ast.UAdd) else -value
            if isinstance(node, ast.BinOp):
                left = evaluate(node.left)
                right = evaluate(node.right)
                operations = {
                    ast.Add: lambda: left + right,
                    ast.Sub: lambda: left - right,
                    ast.Mult: lambda: left * right,
                    ast.Div: lambda: left / right,
                    ast.Mod: lambda: left % right,
                }
                operation = operations.get(type(node.op))
                if operation is None:
                    raise ValueError("Unsupported arithmetic operator")
                return operation()
            raise ValueError("Unsupported arithmetic expression")

        return evaluate(tree)

    def run(self, task: str) -> str:
        task = self._normalize_task(task)
        observation = self._observe()

        for step in range(8):
            print(f"Agent [observe] > {observation}")

            decision = self.brain.think(
                task,
                observation,
                TOOL_DESCRIPTIONS,
                allow_done=True,
            )

            print(f"Agent [think] > {decision.get('message', '')}")

            if decision.get("done"):
                return str(decision.get("message", "Task completed."))

            tool_name = decision.get("tool", "")
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
