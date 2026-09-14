import json
import os
import re

from dotenv import load_dotenv

from tools import TOOLS

load_dotenv()


FUNCTION_TOOLS = [
    {
        "type": "function",
        "name": "open_calculator",
        "description": "Open the native Windows Calculator application.",
        "parameters": {"type": "object", "properties": {}, "required": [], "additionalProperties": False},
        "strict": True,
    },
    {
        "type": "function",
        "name": "list_windows",
        "description": "List visible top-level Windows application window titles.",
        "parameters": {"type": "object", "properties": {}, "required": [], "additionalProperties": False},
        "strict": True,
    },
    {
        "type": "function",
        "name": "focus_window",
        "description": "Find a visible Windows application window by title or partial title and bring it to the foreground.",
        "parameters": {"type": "object", "properties": {"title": {"type": "string", "description": "Exact or partial visible window title"}}, "required": ["title"], "additionalProperties": False},
        "strict": True,
    },
    {
        "type": "function",
        "name": "click_element",
        "description": "Find a visible UI element by name inside a Windows application window and click it.",
        "parameters": {"type": "object", "properties": {"window_title": {"type": "string", "description": "Exact or partial application window title"}, "element_name": {"type": "string", "description": "Visible name of the UI element to click"}}, "required": ["window_title", "element_name"], "additionalProperties": False},
        "strict": True,
    },
    {
        "type": "function",
        "name": "type_text",
        "description": "Focus a visible Windows application window and type text into the currently focused UI control.",
        "parameters": {"type": "object", "properties": {"window_title": {"type": "string", "description": "Exact or partial application window title"}, "text": {"type": "string", "description": "Text to type"}}, "required": ["window_title", "text"], "additionalProperties": False},
        "strict": True,
    },
    {
        "type": "function",
        "name": "read_ui",
        "description": "Read visible text from UI elements inside a Windows application window.",
        "parameters": {"type": "object", "properties": {"window_title": {"type": "string", "description": "Exact or partial application window title"}}, "required": ["window_title"], "additionalProperties": False},
        "strict": True,
    },
    {
        "type": "function",
        "name": "calculator",
        "description": "Open Windows Calculator and enter a simple arithmetic expression.",
        "parameters": {"type": "object", "properties": {"expression": {"type": "string", "description": "Arithmetic expression such as 25 * 4"}}, "required": ["expression"], "additionalProperties": False},
        "strict": True,
    },
]


SYSTEM_INSTRUCTIONS = """
You are a local-first Windows AI agent.
You can inspect visible Windows application windows and control Windows UI elements through tools.
Work as an agent: observe the current UI state, reason about the next action, perform the action, then observe again when needed.
Use multiple tool calls when a task requires multiple steps. Do not stop after one successful action if the user's task is not complete.
When the user asks what applications/windows are open, call list_windows.
When the user asks to focus, activate, or bring a visible application window to the foreground, call focus_window.
When the user asks to click a named UI element inside an application, call click_element.
When the user asks to type text into a visible application, call type_text.
When the user asks to read, inspect, or get visible text from an application, call read_ui.
When the user asks to open Calculator, call open_calculator.
When the user asks to calculate something using Calculator, call calculator.
After performing UI actions, use read_ui when verification is useful or when the task requires knowing the resulting UI state.
Do not claim an action succeeded unless the tool returned successfully.
""".strip()


def _ollama_tools():
    return [
        {
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool["parameters"],
            },
        }
        for tool in FUNCTION_TOOLS
    ]


def _parse_local_calculation(task: str):
    normalized = task.strip().lower()
    if "calculator" not in normalized and "حساب" not in normalized and "محاسبه" not in normalized:
        return None

    expression = None
    patterns = [
        r"(-?\d+(?:\.\d+)?)\s*([+\-*/x×÷])\s*(-?\d+(?:\.\d+)?)",
        r"(-?\d+)\s*(جمع|به علاوه|منهای|ضرب|تقسیم)\s*(-?\d+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, normalized)
        if match:
            left, op, right = match.groups()
            op_map = {"x": "*", "×": "*", "÷": "/", "جمع": "+", "به علاوه": "+", "منهای": "-", "ضرب": "*", "تقسیم": "/"}
            expression = f"{left}{op_map.get(op, op)}{right}"
            break
    return expression


def _local_calculator_agent(task: str):
    expression = _parse_local_calculation(task)
    if not expression:
        return None

    print("Agent [local planner] > Observe: checking Calculator")
    try:
        read_before = TOOLS["read_ui"]("Calculator")
        print(f"Agent [observe] > {read_before}")
    except Exception:
        print("Agent [observe] > Calculator not found; opening it")
        TOOLS["open_calculator"]()
        read_before = TOOLS["read_ui"]("Calculator")
        print(f"Agent [observe] > {read_before}")

    print(f"Agent [think] > Plan: enter {expression} and verify the result")
    print("Agent [act] > calculator")
    result = TOOLS["calculator"](expression)
    print(f"Agent [observe] > {TOOLS['read_ui']('Calculator')}")
    return result


def demo_agent(task: str) -> str:
    local_result = _local_calculator_agent(task)
    if local_result is not None:
        return str(local_result)

    text = task.strip().lower()
    if text in {"hello", "hi", "test"}:
        return "Agent is working locally."
    if "open calculator" in text or "calculator رو باز" in text:
        return TOOLS["open_calculator"]()
    if "list windows" in text or "open windows" in text:
        return str(TOOLS["list_windows"]())
    if text.startswith("focus "):
        return TOOLS["focus_window"](task.strip()[6:].strip())
    if text.startswith("click "):
        parts = task.strip()[6:].strip().split(" | ", 1)
        if len(parts) != 2:
            return "Demo mode: use 'click Window Title | Element Name'."
        return TOOLS["click_element"](parts[0], parts[1])
    if text.startswith("type "):
        parts = task.strip()[5:].strip().split(" | ", 1)
        if len(parts) != 2:
            return "Demo mode: use 'type Window Title | text'."
        return TOOLS["type_text"](parts[0], parts[1])
    if text.startswith("read "):
        return str(TOOLS["read_ui"](task.strip()[5:].strip()))
    if text.startswith("calculate "):
        return TOOLS["calculator"](task.strip()[10:].strip())

    return "Demo mode: no local brain configured. Try a supported Windows task such as 'open calculator', 'read Calculator', or 'calculate 25 * 4'."


def run_with_ollama(task: str) -> str:
    import ollama

    model = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
    messages = [
        {"role": "system", "content": SYSTEM_INSTRUCTIONS},
        {"role": "user", "content": task},
    ]

    for _ in range(8):
        response = ollama.chat(model=model, messages=messages, tools=_ollama_tools())
        message = response.message
        messages.append(message)

        tool_calls = getattr(message, "tool_calls", None) or []
        if not tool_calls:
            return message.content or "Agent finished without a text response."

        for call in tool_calls:
            try:
                args = call.function.arguments or {}
                result = TOOLS[call.function.name](**args)
            except Exception as exc:
                result = f"Tool error: {exc}"
            messages.append({
                "role": "tool",
                "content": str(result),
            })

    return "Local agent stopped after reaching the tool-call limit."


def run_with_llm(task: str) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    model = os.getenv("OPENAI_MODEL", "gpt-5-mini")
    input_items = [{"role": "user", "content": [{"type": "input_text", "text": task}]}]

    for _ in range(8):
        response = client.responses.create(model=model, instructions=SYSTEM_INSTRUCTIONS, tools=FUNCTION_TOOLS, input=input_items)
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
            input_items.append({"type": "function_call_output", "call_id": call.call_id, "output": str(result)})

    return "Agent stopped after reaching the tool-call limit."


def run_agent(task: str) -> str:
    if os.getenv("OPENAI_API_KEY"):
        return run_with_llm(task)
    if os.getenv("LOCAL_BRAIN", "ollama").lower() == "ollama":
        try:
            return run_with_ollama(task)
        except Exception as exc:
            print(f"Agent [local brain] > Ollama unavailable: {exc}")
    return demo_agent(task)


def main():
    print("Local AI Agent — type 'exit' to quit")
    print("Windows tools: observe / focus / click / type / read / calculate")
    print(f"Local brain: {os.getenv('LOCAL_BRAIN', 'ollama')}")

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
