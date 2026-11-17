import re, html, pathlib

root = pathlib.Path(__file__).resolve().parent.parent
SRC = root / "BCS Profile Content (Odoo-First).md"

def esc(s):
    s = html.escape(s.strip(), quote=False)
    return re.sub(r"\*\*(.+?)\*\*", r'<strong class="font-semibold text-bcs-navy">\1</strong>', s)

def esc_dark(s):
    s = html.escape(s.strip(), quote=False)
    return re.sub(r"\*\*(.+?)\*\*", r'<strong class="font-bold text-bcs-yellow">\1</strong>', s)

def plain(s):
    return re.sub(r"\*\*(.+?)\*\*", r"\1", s).strip()

def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]

def parse(path):
    L = path.read_text(encoding="utf-8").splitlines()
    out, i = [], 0
    while i < len(L):
        l = L[i]
        if not l.strip():
            i += 1; continue
        m = re.match(r"^(#{1,4}) (.*)", l)
        if m:
            out.append(("h", len(m.group(1)), m.group(2).strip())); i += 1
        elif l.startswith("|"):
            rows = []
            while i < len(L) and L[i].startswith("|"):
                rows.append(L[i]); i += 1
            out.append(("table", cells(rows[0]), [cells(r) for r in rows[2:]]))
        elif l.startswith("- "):
            items = []
            while i < len(L) and L[i].startswith("- "):
                items.append(L[i][2:].strip()); i += 1
            out.append(("ul", items))
        else:
            out.append(("p", l.strip())); i += 1
    return out

blocks = parse(SRC)

ICONS = {
    "manufacturing": '<path d="M3 21V9l6 4V9l6 4V5h3v16z"/>',
    "supply": '<path d="M3 7l9-4 9 4v10l-9 4-9-4zM3 7l9 4 9-4M12 11v10"/>',
    "finance": '<path d="M4 20V10M10 20V4M16 20v-8M22 20H2"/>',
    "budget": '<circle cx="12" cy="12" r="9"/><path d="M12 12V3M12 12l6 6"/>',
    "sales": '<circle cx="9" cy="8" r="3.5"/><path d="M2 21c0-4 3-6 7-6s7 2 7 6M17 11a3 3 0 100-6M22 20c0-3-2-5-5-5"/>',
    "analytics": '<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M7 15l3-4 3 2 4-6"/>',
    "roles": '<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-6 8-6s8 2 8 6"/>',
    "default": '<circle cx="12" cy="12" r="9"/><path d="M8 12l3 3 5-6"/>',
}

def icon_for(t):
    t = t.lower()
    for k, key in [
        ("manufactur", "manufacturing"), ("supply", "supply"), ("inventory", "supply"),
        ("finance", "finance"), ("budget", "budget"), ("sales", "sales"),
        ("analytics", "analytics"), ("planning, projects", "budget"), ("roles", "roles")
    ]:
        if k in t:
            return ICONS[key]
    return ICONS["default"]

def svg(p, cls="w-5 h-5"):
    return f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{p}</svg>'

def grid_wrap(n):
    if n in (2, 4, 10):
        return "grid grid-cols-1 md:grid-cols-2 gap-5"
    if n == 5:
        return "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-5"
    return "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5"

def grid_span(idx, n):
    if n == 3 and idx == 0:
        return "md:col-span-2 lg:col-span-1"
    if n == 5:
        if idx == 0:
            return "md:col-span-2 lg:col-span-3"
        if idx == 1:
            return "lg:col-span-3"
        return "lg:col-span-2"
    return ""

def render_spec_panel(h, data):
    rows_html = []
    for idx, (a, b) in enumerate(data):
        zebra = "bg-white" if idx % 2 == 0 else "bg-slate-50/60"
        rows_html.append(
            f'<div class="grid grid-cols-1 md:grid-cols-12 gap-1.5 md:gap-6 px-5 sm:px-6 py-4 {zebra} hover:bg-bcs-cream/40 transition-colors">'
            f'<div class="md:col-span-4 font-semibold text-bcs-blue text-[0.95rem]">{esc(a)}</div>'
            f'<div class="md:col-span-8 text-slate-700 text-[0.94rem] leading-relaxed">{esc(b)}</div>'
            f'</div>'
        )
    return (
        '<div class="spec-panel rounded-xl border border-slate-200 bg-white shadow-xs overflow-hidden divide-y divide-slate-200">'
        f'<div class="hidden md:grid md:grid-cols-12 gap-6 px-6 py-3 bg-bcs-blue text-white text-xs font-bold uppercase tracking-wider">'
        f'<div class="md:col-span-4">{esc(h[0])}</div>'
        f'<div class="md:col-span-8">{esc(h[1])}</div>'
        f'</div>'
        + "".join(rows_html) +
        '</div>'
    )

def render_matrix_panel(h, data):
    rows_html = []
    is_gov = (h[0] == "Level")
    for idx, row in enumerate(data):
        zebra = "bg-white" if idx % 2 == 0 else "bg-slate-50/60"
        c2_cls = "md:col-span-4" if is_gov else "md:col-span-3"
        c3_cls = "md:col-span-5" if is_gov else "md:col-span-6"
        c2_val = esc(row[1]) if is_gov else f'<span class="inline-block rounded-full bg-bcs-blue/10 text-bcs-blue text-xs font-bold px-2.5 py-0.5">{esc(row[1])}</span>'
        rows_html.append(
            f'<div class="grid grid-cols-1 md:grid-cols-12 gap-3 md:gap-6 px-5 sm:px-6 py-4 {zebra}">'
            f'<div class="md:col-span-3 font-bold text-bcs-navy text-[0.95rem]">{esc(row[0])}</div>'
            f'<div class="{c2_cls} text-slate-700 text-[0.93rem]"><span class="md:hidden block text-[11px] font-bold uppercase tracking-wider text-bcs-gold mb-0.5">{esc(h[1])}</span>{c2_val}</div>'
            f'<div class="{c3_cls} text-slate-700 text-[0.93rem]"><span class="md:hidden block text-[11px] font-bold uppercase tracking-wider text-bcs-gold mb-0.5">{esc(h[2])}</span>{esc(row[2])}</div>'
            f'</div>'
        )
    c2_h = "md:col-span-4" if is_gov else "md:col-span-3"
    c3_h = "md:col-span-5" if is_gov else "md:col-span-6"
    return (
        '<div class="spec-panel rounded-xl border border-slate-200 bg-white shadow-xs overflow-hidden divide-y divide-slate-200">'
        f'<div class="hidden md:grid md:grid-cols-12 gap-6 px-6 py-3 bg-bcs-navy text-white text-xs font-bold uppercase tracking-wider border-b-2 border-bcs-yellow">'
        f'<div class="md:col-span-3">{esc(h[0])}</div>'
        f'<div class="{c2_h}">{esc(h[1])}</div>'
        f'<div class="{c3_h}">{esc(h[2])}</div>'
        f'</div>'
        + "".join(rows_html) +
        '</div>'
    )

def render_lifecycle_stepper(h, data):
    cards = []
    n = len(data)
    for idx, row in enumerate(data):
        num = idx + 1
        title_txt = re.sub(r"^\d+\.\s*", "", row[0])
        span = "sm:col-span-2 lg:col-span-1" if idx == 0 else ""
        cards.append(
            f'<article class="card {span} flex flex-col justify-between rounded-xl border border-slate-200 bg-white p-5 shadow-xs hover:shadow-md hover:border-bcs-yellow/80 transition-all relative overflow-hidden">'
            f'<div class="absolute top-0 inset-x-0 h-1 bg-gradient-to-r from-bcs-blue to-bcs-yellow"></div>'
            f'<div>'
            f'<div class="flex items-center gap-2.5 mb-3">'
            f'<span class="w-8 h-8 rounded-lg bg-bcs-blue text-bcs-yellow font-extrabold text-sm grid place-items-center shrink-0">{num}</span>'
            f'<h5 class="font-bold text-bcs-navy text-base leading-snug">{esc(title_txt)}</h5>'
            f'</div>'
            f'<div class="mb-4">'
            f'<span class="block text-[10px] font-bold uppercase tracking-wider text-bcs-gold mb-1">{esc(h[1])}</span>'
            f'<p class="text-sm text-slate-600 leading-relaxed">{esc(row[1])}</p>'
            f'</div>'
            f'</div>'
            f'<div class="pt-3 border-t border-slate-100">'
            f'<span class="block text-[10px] font-bold uppercase tracking-wider text-bcs-gold mb-1">{esc(h[2])}</span>'
            f'<span class="inline-block rounded-md bg-bcs-cream border border-bcs-yellow/50 text-bcs-navy text-xs font-bold px-2.5 py-1">{esc(row[2])}</span>'
            f'</div>'
            f'</article>'
        )
    return '<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">' + "".join(cards) + '</div>'

def render_table(h, data, cur_h3):
    # Dense specification tables render as bordered corporate panels
    if len(h) == 2 and any(cur_h3.startswith(p) for p in ("5.4", "5.5", "6.3", "6.4")):
        return render_spec_panel(h, data)
    if len(h) == 3 and h[0] in ("Level", "Role"):
        return render_matrix_panel(h, data)
    if len(h) == 3 and h[0] == "Phase":
        return render_lifecycle_stepper(h, data)

    n = len(data)
    wrap_cls = grid_wrap(n)
    cards = []

    if len(h) == 2:
        numbered = cur_h3.startswith("5.2")
        for idx, (a, b) in enumerate(data):
            span = grid_span(idx, n)
            num_badge = (
                f'<span class="shrink-0 w-7 h-7 rounded-md bg-bcs-blue/10 text-bcs-blue font-bold text-xs grid place-items-center">{idx+1:02d}</span>'
                if numbered else
                '<span class="w-8 h-1 rounded-full bg-bcs-yellow mb-3 block"></span>'
            )
            title_row = (
                f'<div class="flex items-start gap-3 mb-2">{num_badge}<h5 class="font-bold text-bcs-blue text-[1.02rem] leading-snug">{esc(a)}</h5></div>'
                if numbered else
                f'{num_badge}<h5 class="font-bold text-bcs-blue text-[1.04rem] leading-snug mb-2">{esc(a)}</h5>'
            )
            cards.append(
                f'<article class="card {span} h-full flex flex-col rounded-xl border border-slate-200 bg-white p-5 sm:p-6 shadow-xs hover:shadow-md hover:border-bcs-yellow transition-all">'
                f'{title_row}'
                f'<p class="text-[0.94rem] text-slate-600 leading-relaxed">{esc(b)}</p>'
                f'</article>'
            )
    else:
        is_platforms = (h[0] == "Platform")
        for idx, row in enumerate(data):
            span = grid_span(idx, n)
            is_odoo_highlight = (is_platforms or h[0] == "Partner") and row[0].startswith("Odoo")
            border_cls = "border-bcs-yellow ring-1 ring-bcs-yellow/40 bg-bcs-cream/30" if is_odoo_highlight else "border-slate-200 bg-white"
            top_bar = "bg-bcs-yellow" if is_odoo_highlight else "bg-bcs-blue"

            badge = ""
            rest = list(zip(h[1:], row[1:]))
            if h[1] in ("Status", "Industry"):
                badge = f'<span class="inline-block self-start rounded-full bg-bcs-blue text-bcs-yellow text-[11px] font-bold px-3 py-0.5 mb-3 tracking-wide">{esc(row[1])}</span>'
                rest = list(zip(h[2:], row[2:]))
            elif is_platforms and is_odoo_highlight:
                badge = '<span class="inline-block self-start rounded-full bg-bcs-yellow text-bcs-navy text-[11px] font-extrabold px-3 py-0.5 mb-3 uppercase tracking-wider">Lead Enterprise ERP</span>'

            fields = []
            for lab, val in rest:
                fields.append(
                    f'<div class="mt-3 pt-3 border-t border-slate-100 first:mt-0 first:pt-0 first:border-t-0">'
                    f'<span class="block text-[11px] font-bold uppercase tracking-wider text-bcs-gold mb-1">{esc(lab)}</span>'
                    f'<p class="text-[0.93rem] text-slate-700 leading-relaxed">{esc(val)}</p>'
                    f'</div>'
                )

            cards.append(
                f'<article class="card {span} h-full flex flex-col rounded-xl border {border_cls} p-5 sm:p-6 shadow-xs hover:shadow-md transition-all relative overflow-hidden">'
                f'<div class="absolute top-0 inset-x-0 h-1 {top_bar}"></div>'
                f'<h5 class="font-bold text-bcs-navy text-[1.06rem] leading-snug mb-2">{esc(row[0])}</h5>'
                f'{badge}'
                f'<div class="flex-1 flex flex-col justify-between gap-2">{"".join(fields)}</div>'
                f'</article>'
            )

    return f'<div class="{wrap_cls}">' + "".join(cards) + '</div>'

def render_ul(items):
    if all(re.match(r"^\*\*.+?:\*\*", it) for it in items):
        n = len(items)
        wrap_cls = grid_wrap(n)
        cards = []
        for idx, it in enumerate(items):
            m = re.match(r"^\*\*(.+?):\*\*\s*(.*)", it)
            span = grid_span(idx, n)
            cards.append(
                f'<article class="card {span} h-full flex flex-col rounded-xl border border-slate-200 border-l-4 border-l-bcs-yellow bg-white p-5 shadow-xs hover:shadow-md transition-all">'
                f'<h5 class="font-bold text-bcs-blue text-[1.02rem] leading-snug mb-1.5">{esc(m.group(1))}</h5>'
                f'<p class="text-[0.93rem] text-slate-600 leading-relaxed">{esc(m.group(2))}</p>'
                f'</article>'
            )
        return f'<div class="{wrap_cls}">' + "".join(cards) + '</div>'
    return '<ul class="list-disc pl-5 space-y-2 text-slate-700">' + "".join(f"<li>{esc(i)}</li>" for i in items) + '</ul>'

def render_phase(title, inner):
    num = re.search(r"Phase (\d)", title).group(1)
    obj, acts, dels, mode = "", [], [], None
    for b in inner:
        if b[0] == "p":
            t = b[1]
            if t.startswith("**Objective:**"):
                obj = t.replace("**Objective:**", "").strip()
            elif t.startswith("**Key activities**"):
                mode = "a"
            elif t.startswith("**Gate exit deliverables**"):
                mode = "d"
        elif b[0] == "ul":
            (acts if mode == "a" else dels).extend(b[1])

    act_li = "".join(f'<li class="flex items-start gap-2.5 text-[0.94rem] text-slate-700"><span class="mt-2 w-1.5 h-1.5 rounded-full bg-bcs-yellow shrink-0"></span><span>{esc(a)}</span></li>' for a in acts)
    del_chips = "".join(f'<span class="inline-flex items-center rounded-lg bg-bcs-bg border border-slate-200 border-l-3 border-l-bcs-yellow px-3 py-1.5 text-xs sm:text-[0.83rem] font-medium text-bcs-navy">{esc(d)}</span>' for d in dels)

    return (
        f'<article class="phase-card relative pl-10 sm:pl-14" id="phase-{num}">'
        f'<div class="absolute left-0 top-5 w-8 h-8 sm:w-10 sm:h-10 rounded-full bg-bcs-yellow text-bcs-navy font-extrabold text-sm sm:text-base grid place-items-center ring-4 ring-white shadow-sm z-10">{num}</div>'
        f'<div class="rounded-xl border border-slate-200 bg-white p-5 sm:p-6 shadow-xs hover:shadow-md transition-shadow">'
        f'<div class="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-6">'
        f'<div class="lg:w-7/12">'
        f'<h3 class="text-lg sm:text-xl font-bold text-bcs-navy mb-2">{esc(title)}</h3>'
        f'<p class="text-[0.95rem] text-slate-700 mb-4"><strong class="font-bold text-bcs-blue">Objective:</strong> {esc(obj)}</p>'
        f'<h6 class="text-[11px] font-bold uppercase tracking-wider text-bcs-gold mb-2">Key activities</h6>'
        f'<ul class="space-y-1.5">{act_li}</ul>'
        f'</div>'
        f'<div class="lg:w-5/12 lg:border-l lg:border-slate-200 lg:pl-6 pt-4 lg:pt-0 border-t lg:border-t-0 border-slate-100">'
        f'<h6 class="text-[11px] font-bold uppercase tracking-wider text-bcs-gold mb-2.5">Gate exit deliverables</h6>'
        f'<div class="flex flex-wrap gap-2">{del_chips}</div>'
        f'</div>'
        f'</div>'
        f'</div>'
        f'</article>'
    )

ALL_NAV = [
    ("s1", "1. Overview"),
    ("s2", "2. Value Proposition"),
    ("s3", "3. Why Choose BCS"),
    ("s4", "4. Enterprise ERP"),
    ("s5", "5. Odoo ERP"),
    ("s6", "6. Oracle ERP"),
    ("s7", "7. Project Approach"),
    ("s8", "8. Five-Phase Methodology"),
    ("s9", "9. Banking & Payments"),
    ("s10", "10. Global Partners"),
    ("s11", "11. Track Record"),
    ("contact", "12. Contact BCS"),
]

TOP_NAV = [
    ("s1", "Overview"),
    ("s5", "Odoo ERP"),
    ("s6", "Oracle ERP"),
    ("s7", "Approach"),
    ("s9", "Banking"),
    ("s11", "Track Record"),
    ("contact", "Contact"),
]

title = blocks[0][2]
meta = blocks[1][1]
tagline = blocks[2][1]
body, toc_items, secn, sec_open = [], [], 0, False
cur_h3 = ""
n = len(blocks)
i = 3
phases_open = False

while i < n:
    b = blocks[i]
    if b[0] == "h":
        lvl, t = b[1], b[2]
        if lvl == 2:
            if phases_open:
                body.append("</div>"); phases_open = False
            if sec_open:
                body.append("</div></section>")
            secn += 1
            heading = re.sub(r"^\d+\. ", "", t)
            toc_items.append((f"s{secn}", secn, heading))
            is_odoo = heading.startswith("Odoo")
            if is_odoo:
                sec_cls = "py-14 sm:py-20 bg-gradient-to-b from-bcs-cream/70 via-white to-white border-t-4 border-bcs-yellow"
                badge = '<span class="inline-block mb-5 rounded-full bg-bcs-navy text-bcs-yellow text-xs font-bold uppercase tracking-widest px-3.5 py-1">Lead Enterprise ERP</span>'
            elif secn % 2 == 0:
                sec_cls = "py-14 sm:py-20 bg-bcs-bg border-t border-slate-200/70"
                badge = ""
            else:
                sec_cls = "py-14 sm:py-20 bg-white border-t border-slate-200/70"
                badge = ""

            body.append(
                f'<section class="{sec_cls}" id="s{secn}" data-sec>'
                f'<div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">'
                f'<div class="flex items-center gap-4 pb-4 mb-6 border-b border-slate-200">'
                f'<span class="w-11 h-11 sm:w-12 sm:h-12 rounded-xl bg-bcs-blue text-bcs-yellow font-extrabold text-lg sm:text-xl grid place-items-center shrink-0 shadow-sm">{secn:02d}</span>'
                f'<h2 class="text-2xl sm:text-3xl font-extrabold text-bcs-navy tracking-tight leading-tight">{esc(heading)}</h2>'
                f'</div>'
                f'{badge}'
            )
            cur_h3 = ""
            sec_open = True
        elif lvl == 3 and re.search(r"Phase \d:", t):
            if not phases_open:
                body.append('<div class="relative space-y-6 mt-6 before:content-[\'\'] before:absolute before:left-4 sm:before:left-5 before:top-6 before:bottom-6 before:w-0.5 before:bg-gradient-to-b before:from-bcs-yellow before:to-bcs-blue">')
                phases_open = True
            inner = []
            i += 1
            while i < n and blocks[i][0] != "h":
                inner.append(blocks[i]); i += 1
            body.append(render_phase(t, inner)); continue
        elif lvl == 3:
            if phases_open:
                body.append("</div>"); phases_open = False
            cur_h3 = t
            body.append(
                f'<h3 class="mt-10 mb-4 pl-3.5 border-l-4 border-bcs-yellow text-lg sm:text-xl font-bold text-bcs-blue tracking-tight">{esc(t)}</h3>'
            )
        else:
            body.append(
                f'<h4 class="flex items-center gap-3 mt-8 mb-3 text-base sm:text-lg font-bold text-bcs-navy">'
                f'<span class="w-9 h-9 rounded-lg bg-bcs-blue text-bcs-yellow grid place-items-center shrink-0 shadow-xs">{svg(icon_for(t))}</span>'
                f'<span>{esc(t)}</span></h4>'
            )
    elif b[0] == "table":
        body.append(render_table(b[1], b[2], cur_h3))
    elif b[0] == "ul":
        body.append(render_ul(b[1]))
    else:
        t = b[1]
        if t.startswith("**") and t.endswith("**") and t.count("**") == 2:
            body.append(
                f'<div class="mt-8 rounded-xl bg-gradient-to-r from-bcs-navy to-bcs-blue text-white border-l-4 border-bcs-yellow px-6 py-5 sm:px-8 sm:py-6 text-base sm:text-lg shadow-sm">{esc_dark(t)}</div>'
            )
        elif cur_h3 == "3.1 Our Values":
            body.append(
                f'<div class="rounded-r-xl border-l-4 border-bcs-yellow bg-slate-50 px-5 py-4 text-slate-700 leading-relaxed max-w-4xl">{esc(t)}</div>'
            )
        else:
            body.append(f'<p class="text-[0.98rem] text-slate-700 leading-relaxed max-w-4xl my-3.5">{esc(t)}</p>')
    i += 1

if phases_open:
    body.append("</div>")
body.append("</div></section>")

toc_items.append(("contact", 12, "Contact BCS"))
toc_cards_html = "".join(
    f'<a href="#{sid}" class="group flex items-center gap-3.5 rounded-xl border border-slate-200 bg-bcs-bg/60 px-4 py-3.5 hover:bg-white hover:border-bcs-yellow hover:shadow-sm transition-all">'
    f'<span class="w-9 h-9 rounded-lg bg-bcs-blue text-bcs-yellow font-extrabold text-xs grid place-items-center shrink-0 group-hover:bg-bcs-yellow group-hover:text-bcs-navy transition-colors">{num:02d}</span>'
    f'<span class="flex-1 text-sm font-semibold text-bcs-navy leading-snug group-hover:text-bcs-blue">{esc(lbl)}</span>'
    f'<svg class="w-4 h-4 text-slate-400 group-hover:text-bcs-blue group-hover:translate-x-0.5 transition-all shrink-0" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path fill-rule="evenodd" d="M7.21 14.77a.75.75 0 01.02-1.06L11.168 10 7.23 6.29a.75.75 0 111.04-1.08l4.5 4.25a.75.75 0 010 1.08l-4.5 4.25a.75.75 0 01-1.06-.02z" clip-rule="evenodd"/></svg>'
    f'</a>'
    for sid, num, lbl in toc_items
)

top_nav_html = "".join(
    f'<a href="#{s}" class="nav-link px-2.5 xl:px-3 py-1.5 rounded-full text-[13px] font-medium text-slate-200 hover:text-white hover:bg-white/10 transition-colors whitespace-nowrap shrink-0">{esc(t)}</a>'
    for s, t in TOP_NAV
)
outline_nav_html = "".join(
    f'<a href="#{s}" class="outline-link block rounded-lg border border-transparent px-3 py-2 text-sm font-medium text-bcs-navy hover:bg-bcs-bg hover:border-slate-200 transition-colors">{esc(t)}</a>'
    for s, t in ALL_NAV
)
mobile_nav_html = "".join(
    f'<a href="#{s}" class="block rounded-lg px-3.5 py-2.5 text-sm font-medium text-slate-100 hover:bg-white/10 hover:text-bcs-yellow transition-colors">{esc(t)}</a>'
    for s, t in ALL_NAV
)

stats = [
    ("100", "Odoo core applications"),
    ("16,000+", "Odoo community modules"),
    ("2", "World-leading ERP partners: Odoo and Oracle"),
]
stats_html = "".join(
    f'<div class="rounded-xl bg-white border border-slate-200 border-b-4 border-b-bcs-yellow px-5 py-4 shadow-sm">'
    f'<b class="block text-2xl sm:text-3xl font-extrabold text-bcs-navy tracking-tight">{a}</b>'
    f'<span class="block text-xs sm:text-[13px] text-slate-600 mt-0.5">{b}</span>'
    f'</div>'
    for a, b in stats
)

title_parts = [p.strip() for p in title.split(":", 1)]
title_main = title_parts[0]
title_sub = title_parts[1] if len(title_parts) > 1 else ""

page = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(plain(title))}</title>
  <meta name="description" content="{html.escape(tagline[:155])}">
  <link rel="icon" href="assets/img/logo.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="assets/css/styles.css">
</head>
<body class="antialiased selection:bg-bcs-yellow selection:text-bcs-navy">

<header class="site-header sticky top-0 z-50 bg-[rgb(28,72,97)] border-b-2 border-bcs-yellow shadow-sm no-print">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="flex items-center justify-between h-16 gap-4">
      <a href="#top" class="shrink-0 flex items-center">
        <img src="assets/img/logo.png" alt="BCS | Banking and Corporate Services" class="h-10 sm:h-11 w-auto rounded">
      </a>

      <nav class="hidden lg:flex items-center gap-1" aria-label="Primary navigation">
        {top_nav_html}
        <div class="relative ml-2 pl-2 border-l border-white/15">
          <button id="outline-menu-btn" type="button" aria-expanded="false" aria-controls="outline-panel"
            class="inline-flex items-center gap-1.5 rounded-full border border-bcs-yellow/60 bg-white/5 px-3 xl:px-3.5 py-1.5 text-xs font-semibold text-bcs-yellow hover:bg-bcs-yellow hover:text-bcs-navy transition-colors cursor-pointer whitespace-nowrap shrink-0">
            <span>All Sections</span>
            <svg class="w-3.5 h-3.5" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clip-rule="evenodd"/></svg>
          </button>
          <div id="outline-panel" class="hidden absolute right-0 mt-3 w-[440px] rounded-xl bg-white border border-slate-200 shadow-xl p-4 z-50">
            <p class="text-[11px] font-bold uppercase tracking-wider text-bcs-gold px-2 mb-2">Document Contents (12 Sections)</p>
            <div class="grid grid-cols-2 gap-1">{outline_nav_html}</div>
          </div>
        </div>
      </nav>

      <button id="mobile-menu-btn" type="button" aria-label="Open navigation menu" aria-expanded="false" aria-controls="mobile-drawer"
        class="lg:hidden inline-flex items-center justify-center rounded-lg p-2 text-bcs-yellow hover:bg-white/10 focus:outline-none cursor-pointer">
        <svg class="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/>
        </svg>
      </button>
    </div>

    <div id="mobile-drawer" class="hidden lg:hidden border-t border-white/15 py-3 pb-4">
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-1">{mobile_nav_html}</div>
    </div>
  </div>
</header>

<main id="top">
  <section class="hero-bg relative text-white overflow-hidden">
    <div class="hero-grid-pattern absolute inset-0 pointer-events-none"></div>
    <div class="relative max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 pt-14 pb-12 sm:pt-20 sm:pb-16">
      <p class="inline-flex items-center gap-2 rounded-full bg-white/10 border border-white/15 px-3.5 py-1 text-xs font-semibold uppercase tracking-widest text-bcs-yellow mb-5">
        Company Profile - Enterprise ERP Solutions &middot; Ethiopia &amp; Africa
      </p>
      <h1 class="tracking-tight leading-[1.15] max-w-4xl">
        <span class="block text-3xl sm:text-5xl lg:text-[3.25rem] font-extrabold text-white">{esc(title_main)}</span>
        {f'<span class="block text-2xl sm:text-3xl lg:text-[2.25rem] font-bold text-bcs-yellow mt-2.5">{esc(title_sub)}</span>' if title_sub else ''}
      </h1>
      <div class="w-20 h-1.5 rounded-full bg-bcs-yellow my-6"></div>
      <p class="text-base sm:text-xl text-slate-100/95 leading-relaxed max-w-3xl">{esc(tagline)}</p>
      <p class="text-sm text-slate-300 mt-4">{esc(meta)}</p>

      <div class="flex flex-wrap gap-3 mt-8">
        <a href="#s5" class="inline-flex items-center justify-center rounded-full bg-bcs-yellow px-6 py-3 text-sm sm:text-base font-bold text-bcs-navy shadow-md hover:bg-amber-300 transition-colors">Enterprise Odoo ERP</a>
        <a href="#s6" class="inline-flex items-center justify-center rounded-full border border-white/35 bg-white/5 px-6 py-3 text-sm sm:text-base font-semibold text-white hover:border-bcs-yellow hover:text-bcs-yellow transition-colors">Oracle ERP</a>
        <a href="#s9" class="inline-flex items-center justify-center rounded-full border border-white/35 bg-white/5 px-6 py-3 text-sm sm:text-base font-semibold text-white hover:border-bcs-yellow hover:text-bcs-yellow transition-colors">Banking and Payments</a>
      </div>
    </div>

    <div class="relative bg-bcs-bg/95 border-t border-bcs-yellow/40 py-6">
      <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          {stats_html}
        </div>
      </div>
    </div>
  </section>

  <section class="py-12 sm:py-16 bg-white" id="toc" aria-label="Table of Contents">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-2 pb-4 mb-6 border-b border-slate-200">
        <div>
          <p class="text-[11px] font-bold uppercase tracking-widest text-bcs-gold mb-1">Document Index</p>
          <h2 class="text-2xl sm:text-3xl font-extrabold text-bcs-navy tracking-tight">Table of Contents</h2>
        </div>
        <p class="text-sm text-slate-500">12 Sections &middot; Select any section to jump directly</p>
      </div>
      <nav aria-label="Table of contents" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3.5">
        {toc_cards_html}
      </nav>
    </div>
  </section>

  {chr(10).join(body)}

  <section class="py-14 sm:py-20 bg-bcs-bg border-t border-slate-200" id="contact" data-sec>
    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center gap-4 pb-4 mb-8 border-b border-slate-200">
        <span class="w-11 h-11 sm:w-12 sm:h-12 rounded-xl bg-bcs-blue text-bcs-yellow font-extrabold text-lg sm:text-xl grid place-items-center shrink-0 shadow-sm">12</span>
        <h2 class="text-2xl sm:text-3xl font-extrabold text-bcs-navy tracking-tight">Contact BCS</h2>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <article class="card h-full rounded-xl border border-slate-200 bg-white p-6 shadow-xs relative overflow-hidden">
          <div class="absolute top-0 inset-x-0 h-1 bg-bcs-yellow"></div>
          <h5 class="font-bold text-bcs-navy text-lg mb-1">Contact Person</h5>
          <p class="text-xs font-bold uppercase tracking-wider text-bcs-gold mb-4">For ERP Enquiries</p>
          <p class="text-base text-slate-800 mb-4"><strong class="font-bold text-bcs-navy">Mesay Alemayehu</strong>, Account Manager</p>
          <dl class="space-y-3 text-sm sm:text-[0.95rem]">
            <div>
              <dt class="text-[11px] font-bold uppercase tracking-wider text-bcs-gold">Phone</dt>
              <dd class="mt-0.5"><a href="tel:+251921001155" class="font-semibold text-bcs-blue hover:underline">+251 921 001155</a></dd>
            </div>
            <div>
              <dt class="text-[11px] font-bold uppercase tracking-wider text-bcs-gold">Email</dt>
              <dd class="mt-0.5"><a href="mailto:mesay.alemayehu@followbcs.com" class="font-semibold text-bcs-blue hover:underline break-all">mesay.alemayehu@followbcs.com</a></dd>
            </div>
          </dl>
        </article>

        <article class="card h-full rounded-xl border border-slate-200 bg-white p-6 shadow-xs relative overflow-hidden">
          <div class="absolute top-0 inset-x-0 h-1 bg-bcs-blue"></div>
          <h5 class="font-bold text-bcs-navy text-lg mb-4">Company Contact</h5>
          <dl class="space-y-3 text-sm sm:text-[0.95rem]">
            <div>
              <dt class="text-[11px] font-bold uppercase tracking-wider text-bcs-gold">Email</dt>
              <dd class="mt-0.5"><a href="mailto:info@followbcs.com" class="font-semibold text-bcs-blue hover:underline">info@followbcs.com</a></dd>
            </div>
            <div>
              <dt class="text-[11px] font-bold uppercase tracking-wider text-bcs-gold">Ethiopia</dt>
              <dd class="mt-0.5"><a href="tel:+251928592222" class="font-semibold text-bcs-blue hover:underline">+251928592222</a></dd>
            </div>
            <div>
              <dt class="text-[11px] font-bold uppercase tracking-wider text-bcs-gold">Dubai</dt>
              <dd class="mt-0.5"><a href="tel:+971567245699" class="font-semibold text-bcs-blue hover:underline">+971567245699</a></dd>
            </div>
            <div>
              <dt class="text-[11px] font-bold uppercase tracking-wider text-bcs-gold">Website</dt>
              <dd class="mt-0.5"><a href="https://followbcs.com/" target="_blank" rel="noopener noreferrer" class="font-semibold text-bcs-blue hover:underline">https://followbcs.com/</a></dd>
            </div>
          </dl>
        </article>
      </div>

      <div class="mt-6 rounded-xl bg-gradient-to-r from-bcs-navy to-bcs-blue text-white border-l-4 border-bcs-yellow px-6 py-5 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 shadow-sm">
        <p class="text-sm sm:text-base text-slate-100">
          For more details and other solutions, visit our website:
          <a href="https://followbcs.com/" target="_blank" rel="noopener noreferrer" class="font-bold text-bcs-yellow underline underline-offset-4 hover:text-amber-300 ml-1">https://followbcs.com/</a>
        </p>
        <a href="https://followbcs.com/" target="_blank" rel="noopener noreferrer" class="shrink-0 inline-flex items-center justify-center rounded-full bg-bcs-yellow px-5 py-2.5 text-xs sm:text-sm font-bold text-bcs-navy hover:bg-amber-300 transition-colors">Visit Website</a>
      </div>
    </div>
  </section>
</main>

<footer class="bg-[rgb(28,72,97)] text-white border-t-4 border-bcs-yellow py-10">
  <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-center sm:text-left">
    <img src="assets/img/logo.png" alt="BCS | Banking and Corporate Services" class="h-12 w-auto rounded">
    <p class="text-sm text-slate-300">&copy; BCS Services PLC &middot; BCS | Banking and Corporate Services</p>
  </div>
</footer>

<script src="assets/js/main.js"></script>
</body>
</html>'''

(root / "index.html").write_text(page, encoding="utf-8")
print("ok", len(page))
