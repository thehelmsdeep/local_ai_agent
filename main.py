import os
import ast
import operator
from dotenv import load_dotenv

load_dotenv()

OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
}


def safe_calculate(expression: str):
    tree = ast.parse(expression, mode="eval")

    def walk(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            value = walk(node.operand)
            return value if isinstance(node.op, ast.UAdd) else -value
        if isinstance(node, ast.BinOp) and type(node.op) in OPS:
            return OPS[type(node.op)](walk(node.left), walk(node.right))
        raise ValueError("Unsupported expression")

    return walk(tree.body)


def run_agent(task: str):
    task = task.strip()
    if task.lower().startswith("calculate "):
        expression = task[10:].strip()
        return f"Result: {safe_calculate(expression)}"

    if task.lower() in {"hello", "hi", "test"}:
        return "Agent is working locally."

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return (
            "Demo mode: no OPENAI_API_KEY configured. "
            "Try: calculate 12 * (8 + 2)"
        )

    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    model = os.getenv("OPENAI_MODEL", "gpt-5-mini")
    response = client.responses.create(model=model, input=task)
    return response.output_text


def main():
    print("Local AI Agent — type 'exit' to quit")
    while True:
        try:
            task = input("\nYou > ")
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if task.strip().lower() == "exit":
            break

        try:
            print(f"Agent > {run_agent(task)}")
        except Exception as exc:
            print(f"Agent error > {exc}")


if __name__ == "__main__":
    main()
