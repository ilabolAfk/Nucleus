# registry.py
from difflib import SequenceMatcher

REGISTRY = []

def action(prefix, title, icon, subtitle=""):
    def deco(fn):
        REGISTRY.append(dict(prefix=prefix, title=title, icon=icon,
                             subtitle=subtitle, run=fn))
        return fn
    return deco

def search(q):
    q = q.strip()
    if not q:
        return REGISTRY[:8]
    scored = []
    for a in REGISTRY:
        s = SequenceMatcher(None, q.lower(),
                            (a["title"] + a["prefix"]).lower()).ratio()
        if q.startswith(a["prefix"]):
            s += 1.5
        if s > 0.25:
            scored.append((s, a))
    return [a for _, a in sorted(scored, key=lambda x: -x[0])][:8]