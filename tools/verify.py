import re, html, pathlib, sys
root = pathlib.Path(__file__).resolve().parent.parent
page = (root / "index.html").read_text(encoding="utf-8")
if "<table" in page: sys.exit("FAIL: table element found")
text = re.sub(r"<script.*?</script>|<style.*?</style>", "", page, flags=re.S)
text = html.unescape(re.sub(r"<[^>]+>", " ", text))
norm = lambda s: re.sub(r"\s+", " ", s).strip()
T = norm(text)
num = lambda s: re.sub(r"^\d+(\.\d+)*\.? ", "", s)
miss = 0; total = 0
def chk(s):
    global miss, total
    s = norm(re.sub(r"\*\*(.+?)\*\*", r"\1", s))
    if not s: return
    total += 1
    if s not in T:
        miss += 1; print("MISSING:", s[:100])
for f in ["BCS Profile Content (Odoo-First).md"]:
    old = False
    for l in (root / f).read_text(encoding="utf-8").splitlines():
        l = l.strip()
        if not l or re.match(r"^\|[ \-|:]+\|$", l): continue
        if old and (l.startswith("# ") or l.startswith("Nov ")): continue
        if l.startswith("#"):
            h = l.lstrip("#").strip()
            chk(num(h) if not old else re.sub(r"^\d+(\.\d+)*\.? ", "", h)); continue
        if l.startswith("|"):
            for c in l.strip("|").split("|"): chk(c)
        elif l.startswith("- "): 
            m = re.match(r"^- \*\*(.+?):\*\*\s*(.*)", l)
            if m: chk(m.group(1)); chk(m.group(2))
            else: chk(l[2:])
        else:
            m = re.match(r"^\*\*(Objective:)\*\*\s*(.*)", l)
            if m: chk(m.group(2))
            elif l in ("**Key activities**", "**Gate exit deliverables**"): continue
            else: chk(l)
for w in [r"\bgrowing\b", r"\bsmall\b", r"\bSMEs?\b", r"\bversus\b", r"compared with"]:
    if re.search(w, T, re.I): print("BANNED:", w); miss += 1
ids = set(re.findall(r'id="([^"]+)"', page))
for a in re.findall(r'href="#([^"]+)"', page):
    if a != "top" and a not in ids: print("BAD ANCHOR", a); miss += 1
print(f"checked {total} items, {miss} problems")
sys.exit(1 if miss else 0)



