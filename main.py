import json
import os

from dotenv import load_dotenv

from tools import TOOLS

load_dotenv()


FUNCTION_TOOLS = [
    {
        "type": "function",
        "name": "open_calculator",
        "description": "Open the native Windows Calculator application.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "calculator",
        "description": "Open Windows Calculator and enter a simple arithmetic expression.",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Arithmetic expression such as 25 * 4",
                }
            },
            "required": ["expression"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]


SYSTEM_INSTRUCTIONS = """
You are a local-first Windows AI agent.
You can control the user's Windows Calculator through tools.
When the user asks to open Calculator, call open_calculator.
When the user asks to calculate something using Calculator, call calculator.
Do not claim that you opened or controlled an application unless the tool returned successfully.
""".strip()


def demo_agent(task: str) -> str:
    """Small local demo mode that works without an API key."""
    text = task.strip().lower()

    if text in {"hello", "hi", "test"}:
        return "Agent is working locally."

    if "open calculator" in text or "calculator رو باز" in text:
        return TOOLS["open_calculator"]()

    if text.startswith("calculate "):
        expression = task.strip()[10:].strip()
        return TOOLS["calculator"](expression)

    return (
        "Demo mode: no OPENAI_API_KEY configured. "
        "Try 'open calculator' or 'calculate 25 * 4'."
    )


def run_with_llm(task: str) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    model = os.getenv("OPENAI_MODEL", "gpt-5-mini")

    input_items = [
        {
            "role": "user",
            "content": [{"type": "input_text", "text": task}],
        }
    ]

    for _ in range(5):
        response = client.responses.create(
            model=model,
            instructions=SYSTEM_INSTRUCTIONS,
            tools=FUNCTION_TOOLS,
            input=input_items,
        )

        input_items += response.output
        function_calls = [item for item in response.output if item.type == "function_call"]

        if not function_calls:
            return response.output_text

        for call in function_calls:
            try:
                args = json.loads(call.arguments or "{}")
                result = TOOLS[call.name](**args)
            except Exception as exc:
                result = f"Tool error: {exc}"

            input_items.append(
                {
                    "type": "function_call_output",
                    "call_id": call.call_id,
                    "output": str(result),
                }
            )

    return "Agent stopped after reaching the tool-call limit."


def run_agent(task: str) -> str:
    if not os.getenv("OPENAI_API_KEY"):
        return demo_agent(task)
    return run_with_llm(task)


def main():
    print("Local AI Agent — type 'exit' to quit")
    print("Windows tools: open Calculator / calculate with Calculator")

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
