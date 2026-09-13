import re
import subprocess
import time

from pywinauto import Desktop


def _calculator_window():
    """Find Windows Calculator using UI Automation."""
    desktop = Desktop(backend="uia")
    windows = desktop.windows(title_re=r".*[Cc]alculator.*", visible_only=True)
    return windows[0] if windows else None


def open_calculator() -> bool:
    subprocess.Popen(["calc.exe"])

    for _ in range(30):
        time.sleep(0.2)
        window = _calculator_window()
        if window:
            try:
                window.set_focus()
            except Exception:
                pass
            return True

    return False


def _click_button(window, name):
    """Find a Calculator button by UI Automation and click it."""
    buttons = window.descendants(control_type="Button")

    for button in buttons:
        try:
            if button.window_text() == name:
                button.click_input()
                return
        except Exception:
            continue

    raise RuntimeError(f"Calculator button not found: {name}")


def calculator(expression: str):
    """Use Calculator UI buttons instead of coordinates."""
    if not re.fullmatch(r"[0-9+\-*/().%\s]+", expression):
        raise ValueError("Unsupported expression")

    if not open_calculator():
        raise RuntimeError("Calculator not found")

    window = _calculator_window()
    window.set_focus()

    mapping = {
        "0": "Zero", "1": "One", "2": "Two", "3": "Three",
        "4": "Four", "5": "Five", "6": "Six", "7": "Seven",
        "8": "Eight", "9": "Nine",
        "+": "Plus", "-": "Minus", "*": "Multiply", "/": "Divide",
    }

    for char in expression:
        if char.isspace():
            continue
        if char in mapping:
            _click_button(window, mapping[char])

    _click_button(window, "Equals")
    return f"Clicked Calculator UI for: {expression}"


TOOLS = {
    "open_calculator": open_calculator,
    "calculator": calculator,
}
