import re
import subprocess
import time

from pywinauto import Desktop


def _desktop():
    return Desktop(backend="uia")


def _calculator_window():
    desktop = _desktop()
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
    windows = _desktop().windows(visible_only=True)

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


def focus_window(title: str):
    """Find a visible top-level window by title and bring it to the foreground."""
    query = title.strip().lower()
    if not query:
        raise ValueError("Window title cannot be empty")

    windows = _desktop().windows(visible_only=True)

    exact_match = None
    partial_match = None

    for window in windows:
        try:
            window_title = window.window_text().strip()
            normalized = window_title.lower()

            if normalized == query:
                exact_match = window
                break

            if query in normalized and partial_match is None:
                partial_match = window
        except Exception:
            continue

    window = exact_match or partial_match
    if window is None:
        raise RuntimeError(f"Window not found: {title}")

    window.set_focus()
    return f"Focused window: {window.window_text().strip()}"


def click_element(window_title: str, element_name: str):
    """Click a visible UI element by its name inside a matching window."""
    query = window_title.strip().lower()
    target = element_name.strip().lower()

    if not query:
        raise ValueError("Window title cannot be empty")
    if not target:
        raise ValueError("Element name cannot be empty")

    windows = _desktop().windows(visible_only=True)
    window = None

    for candidate in windows:
        try:
            title = candidate.window_text().strip().lower()
            if title == query or query in title:
                window = candidate
                if title == query:
                    break
        except Exception:
            continue

    if window is None:
        raise RuntimeError(f"Window not found: {window_title}")

    window.set_focus()

    for control in window.descendants():
        try:
            text = control.window_text().strip()
            if text and (target in text.lower() or text.lower() in target):
                control.click_input()
                return f"Clicked '{text}' in '{window.window_text().strip()}'"
        except Exception:
            continue

    raise RuntimeError(f"UI element not found: {element_name}")


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
    "focus_window": focus_window,
    "click_element": click_element,
    "calculator": calculator,
}
