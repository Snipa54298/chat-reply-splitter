"""Replaceable language policies. Selection is explicit, never global per-user state."""
from dataclasses import dataclass
import re

@dataclass(frozen=True)
class LanguageRules:
    code: str
    commas: str = ","
    periods: str = "."
    exclamations: str = "!"
    questions: str = "?"
    min_chars: int = 6
    max_chars: int = 240
    short_chars: int = 24
    starters: tuple[str, ...] = ()
    abbreviations: tuple[str, ...] = ()

    def split(self, text, casual=False, *, starters=None):
        """Return segments to override the engine, or None to use generic rules."""
        return None

    def valid_boundary(self, text, start, end):
        # ASCII dot: decimals, dotted identifiers, initials, ellipses and common abbreviations.
        mark = text[start:end].strip()
        if "." in mark:
            if mark.count(".") > 1:
                return False
            if start and text[start-1].isdigit() and end < len(text) and text[end].isdigit():
                return False
            if end < len(text) and not text[end].isspace():
                return False
            prefix = text[:end].casefold()
            if any(prefix.endswith(word.casefold()) for word in self.abbreviations):
                return False
            if re.search(r"\b[A-Za-z]\.$", text[:end]):
                return False
        return True

    def cleanup(self, text):
        # Other languages retain their punctuation; Chinese styling is opt-in via zh implementation.
        return " ".join(text.strip().splitlines()).strip()

_REGISTRY = {}

def register_language(rules, *, replace=False):
    if not isinstance(rules, LanguageRules):
        raise TypeError("Expected LanguageRules")
    key = rules.code.lower().replace("_", "-")
    if key.split("-")[0] == "zh":
        raise ValueError("Chinese is reserved for the unchanged lightweight core")
    if not key or rules.min_chars < 1 or rules.max_chars < rules.min_chars * 2 or rules.short_chars < 0:
        raise ValueError("Invalid language policy")
    if key in _REGISTRY and not replace:
        raise ValueError("Language already registered: " + key)
    _REGISTRY[key] = rules

def get_language(code):
    key = code.lower().replace("_", "-")
    if key in _REGISTRY:
        return _REGISTRY[key]
    base = key.split("-")[0]
    if base in _REGISTRY:
        return _REGISTRY[base]
    raise ValueError("Unsupported language: " + code)

