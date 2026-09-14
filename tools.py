import re
import subprocess
import time

from pywinauto import Desktop


def _calculator_window():
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


def list_windows():
    """Return visible top-level Windows application titles."""
    desktop = Desktop(backend="uia")
    windows = desktop.windows(visible_only=True)

    titles = []
    seen = set()

    for window in windows:
        try:
            title = window.window_text().strip()
            if title and title not in seen:
                seen.add(title)
                titles.append(title)
        except Exception:
            continue

    return titles


def _click_button(window, names):
    """Find a Calculator button using possible UI names."""
    buttons = window.descendants(control_type="Button")

    for button in buttons:
        try:
            text = button.window_text().strip().lower()
            if any(name.lower() in text or text in name.lower() for name in names):
                button.click_input()
                return
        except Exception:
            continue

    available = []
    for button in buttons:
        try:
            available.append(button.window_text())
        except Exception:
            pass

    raise RuntimeError(f"Calculator button not found: {names}. Available: {available}")


def calculator(expression: str):
    if not re.fullmatch(r"[0-9+\-*/().%\s]+", expression):
        raise ValueError("Unsupported expression")

    if not open_calculator():
        raise RuntimeError("Calculator not found")

    window = _calculator_window()
    window.set_focus()

    mapping = {
        "0": ["Zero", "0"], "1": ["One", "1"], "2": ["Two", "2"],
        "3": ["Three", "3"], "4": ["Four", "4"], "5": ["Five", "5"],
        "6": ["Six", "6"], "7": ["Seven", "7"], "8": ["Eight", "8"],
        "9": ["Nine", "9"],
        "+": ["Plus", "+"],
        "-": ["Minus", "−", "-"],
        "*": ["Multiply", "Multiplication", "×", "*"],
        "/": ["Divide", "Division", "÷", "/"],
    }

    for char in expression:
        if char.isspace():
            continue
        if char in mapping:
            _click_button(window, mapping[char])

    _click_button(window, ["Equals", "="])
    return f"Clicked Calculator UI for: {expression}"


TOOLS = {
    "open_calculator": open_calculator,
    "list_windows": list_windows,
    "calculator": calculator,
}
