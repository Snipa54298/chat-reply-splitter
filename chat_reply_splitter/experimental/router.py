"""Language-selectable, conservative chat reply splitter."""
import re
from .languages import LanguageRules, get_language, register_language
from .packs import en, ja, ar
from .. import split_reply as split_chinese

for _pack in (en.PACK, ja.PACK, ar.PACK):
    register_language(_pack)


def split_reply(text, casual=False, *, language="zh", starters=None):
    if isinstance(language, str) and language.lower().replace("_", "-").split("-")[0] == "zh":
        return split_chinese(text, casual)
    rules = get_language(language) if isinstance(language, str) else language
    if not isinstance(rules, LanguageRules):
        raise TypeError("language must be a locale string or LanguageRules instance")
    custom = rules.split(text, casual, starters=starters)
    if custom is not None:
        return custom
    if not casual:
        return [text]
    if any(x in text for x in ('http', '```', '[CQ:', '“', '”', '「', '」', '"', '(', ')', '（', '）', '«', '»')):
        return [text]
    clean = rules.cleanup
    if len(text) > rules.max_chars:
        return [clean(text)]
    def valid(a, b):
        return len(text[:a].strip()) >= rules.min_chars and len(text[b:].strip()) >= rules.min_chars
    def result(a, b):
        return [clean(text[:a]), clean(text[b:])]
    paragraphs = [(m.start(), m.end()) for m in re.finditer(r"\r?\n\s*", text) if valid(m.start(), m.end())]
    if paragraphs:
        return result(*min(paragraphs, key=lambda pair: abs(pair[0] - (len(text)-pair[1]))))
    marks = rules.exclamations + rules.questions
    if len(text) > rules.short_chars:
        marks += rules.periods
    boundaries = []
    if marks:
        for m in re.finditer("[" + re.escape(marks) + "]+", text):
            if valid(m.end(), m.end()) and rules.valid_boundary(text, m.start(), m.end()):
                boundaries.append(m.end())
    if boundaries:
        cut = min(boundaries, key=lambda i: abs(len(text)/2-i))
        return result(cut, cut)
    # No universal comma grammar: disabled unless the language policy/user provides starters.
    cues = rules.starters if starters is None else tuple(starters)
    if len(text) > rules.short_chars and rules.commas and cues:
        matches = list(re.finditer("[" + re.escape(rules.commas) + "]", text))
        choices = [m for m in matches if valid(m.start(), m.end()) and text[m.end():].lstrip().startswith(cues)] if len(matches) >= 2 else []
        if choices:
            cut = min(choices, key=lambda m: abs(len(text)/2-m.start()))
            return result(cut.start(), cut.end())
    return [clean(text)]
