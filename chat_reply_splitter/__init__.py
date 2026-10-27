"""Small Chinese presentation splitter; stdlib only, no linguistic keyword lists."""
import re


def split_reply(text, casual=False):
    if not casual or any(s in text for s in ('http', '```', '[CQ:', '(', ')', '（', '）', '《', '》')):
        return [text]
    pairs = dict(zip('“‘「『\"\'', '”’」』\"\''))
    stack, protected = [], []
    for c in text:
        if stack and c == stack[-1]:
            protected.append(True)
            stack.pop()
        elif c in pairs:
            stack.append(pairs[c])
            protected.append(True)
        elif c in pairs.values():
            return [text]
        else:
            protected.append(bool(stack))
    if stack:
        return [text]

    def dot(i):
        return (text[i] == '.' and i > 0
                and bool(re.match(r'[\u3400-\u9fff]', text[i-1]))
                and (not text[i+1:].strip() or bool(re.match(r'\s*[\u3400-\u9fff]', text[i+1:]))))

    def clean(a, b):
        chars = []
        for i in range(a, b):
            c = text[i]
            if not protected[i] and (c == '。' or dot(i)):
                c = '，' if text[i+1:b].strip() else ''
            chars.append(c)
        return ' '.join(''.join(chars).splitlines()).strip()

    cuts = []
    if len(text) <= 50:
        for m in re.finditer(r'[。！？!?]+|\.', text):
            i = m.end()
            if (not any(protected[m.start():i])
                    and (m.group() != '.' or dot(m.start()))
                    and len(text[:i].strip()) >= 6 and len(text[i:].strip()) >= 6):
                cuts.append(i)
    if cuts:
        i = min(cuts, key=lambda i: abs(len(text)/2-i))
        return [clean(0, i), clean(i, len(text))]
    return [text if any(protected) else clean(0, len(text))]
