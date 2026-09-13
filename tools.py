import re
import subprocess
import time

import pyautogui
import pyperclip


def open_calculator() -> str:
    """Open the native Windows Calculator application."""
    subprocess.Popen(["calc.exe"])
    time.sleep(1.5)
    return "Windows Calculator opened."


def calculator(expression: str) -> str:
    """Open Calculator, paste a simple arithmetic expression, and press Enter."""
    if not re.fullmatch(r"[0-9+\-*/().%\s]+", expression):
        raise ValueError("Calculator expression contains unsupported characters")

    open_calculator()

    # Clipboard paste is more reliable than pyautogui.write for symbols such as *.
    pyperclip.copy(expression)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(0.3)
    pyautogui.press("enter")
    return f"Sent to Windows Calculator: {expression}"


TOOLS = {
    "open_calculator": open_calculator,
    "calculator": calculator,
}
