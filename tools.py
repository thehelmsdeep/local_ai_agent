import re
import subprocess
import time

import pyautogui


def open_calculator() -> str:
    """Open the native Windows Calculator application."""
    subprocess.Popen(["calc.exe"])
    time.sleep(1.2)
    return "Windows Calculator opened."


def calculator(expression: str) -> str:
    """Open Calculator, enter a simple arithmetic expression, and press Enter."""
    if not re.fullmatch(r"[0-9+\-*/().%\s]+", expression):
        raise ValueError("Calculator expression contains unsupported characters")

    open_calculator()
    pyautogui.write(expression, interval=0.03)
    pyautogui.press("enter")
    return f"Sent to Windows Calculator: {expression}"


TOOLS = {
    "open_calculator": open_calculator,
    "calculator": calculator,
}
