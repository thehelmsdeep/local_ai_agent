import re
import subprocess
import time

import pyautogui
from pywinauto import Desktop


def _calculator_window():
    """Find the native Windows Calculator window using UI Automation."""
    desktop = Desktop(backend="uia")
    windows = desktop.windows(title_re=r".*[Cc]alculator.*", visible_only=True)
    if not windows:
        return None
    return windows[0]


def _focus_calculator() -> bool:
    """Bring Calculator to the foreground and give it keyboard focus."""
    window = _calculator_window()
    if window is None:
        return False

    try:
        window.restore()
    except Exception:
        pass

    try:
        window.set_focus()
    except Exception:
        return False

    time.sleep(0.2)
    return True


def open_calculator() -> str:
    """Open the native Windows Calculator application and focus it."""
    subprocess.Popen(["calc.exe"])

    for _ in range(30):
        time.sleep(0.2)
        if _focus_calculator():
            return "Windows Calculator opened and focused."

    return "Windows Calculator opened, but its window could not be focused."


def calculator(expression: str) -> str:
    """Open Calculator, focus it, type an arithmetic expression, and press Enter."""
    if not re.fullmatch(r"[0-9+\-*/().%\s]+", expression):
        raise ValueError("Calculator expression contains unsupported characters")

    open_calculator()

    if not _focus_calculator():
        raise RuntimeError("Could not focus Windows Calculator")

    # Type through the focused Calculator window instead of using clipboard paste.
    # This works with the modern Windows Calculator UI where Ctrl+V is unreliable.
    pyautogui.write(expression, interval=0.05)
    pyautogui.press("enter")
    return f"Sent to Windows Calculator: {expression}"


TOOLS = {
    "open_calculator": open_calculator,
    "calculator": calculator,
}
