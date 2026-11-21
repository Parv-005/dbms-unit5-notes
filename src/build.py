#!/usr/bin/env python3
"""Builds Unit5_Transactions_Notes.html from parts/*.html + helpers.

Placeholders inside parts:
  {{sched:ID}}         schedule table
  {{pgraph:ID}}        precedence graph (auto-computed)   {{pgraph:ID|nolabel}}
  {{conf:ID}}          table of every conflicting pair
  {{edges:ID}}         per-data-item edge table (compact)
  {{verdict:ID}}       auto verdict (cycle / serial orders)
  {{recov:ID}}         reads-from / recoverability analysis
  {{svg:NAME}}         custom figure from figures.py
"""
import re, os, html, math, sys

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
from schedules import SCHED
import figures
from svglib import digraph, circle_layout

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(BASE, 'out.html')

# ------------------------------------------------------------------ parsing
COMPACT = re.compile(r'([rwcaRWCA])\s*(\d+)\s*(?:\(\s*([A-Za-z]\w*)\s*\))?')
OPRE = re.compile(r'^\s*(read|write|r|w)(?:_item)?\s*\(\s*([A-Za-z]\w*)\s*\)\s*;?\s*$', re.I)


def parse(spec):
    """Return list of rows: dict(t=txn, op=str, note=str, mark='' | '!' | '*')"""
    spec = spec.strip()
    rows = []
    if spec.startswith('@'):           # compact form  @r1(X); w2(Y); c1
        for m in COMPACT.finditer(spec[1:]):
            k, n, item = m.group(1).lower(), m.group(2), m.group(3)
            t = 'T' + n
            op = {'r': f'R({item})', 'w': f'W({item})', 'c': 'Commit', 'a': 'Abort'}[k]
            rows.append(dict(t=t, op=op, note='', mark=''))
        return rows
    for line in spec.splitlines():
        line = line.strip()
        if not line:
            continue
        note = ''
        if '#' in line:
            line, note = line.split('#', 1)
            line, note = line.strip(), note.strip()
        t, op = line.split(':', 1)
        op = op.strip()
        mark = ''
        if op[:1] in '!*':
            mark, op = op[0], op[1:].strip()
        rows.append(dict(t=t.strip(), op=op, note=note, mark=mark))
    return rows


def txns_of(rows):
    seen = []
    for r in rows:
        if r['t'] not in seen and r['t'] != '-':
            seen.append(r['t'])
    return sorted(seen, key=lambda s: (len(s), s))


def rw(rows):
    out = []
    for i, r in enumerate(rows, 1):
        m = OPRE.match(r['op'])
        if m:
            out.append((i, r['t'], m.group(1)[0].upper(), m.group(2)))
    return out


def commit_step(rows):
    c = {}
    for i, r in enumerate(rows, 1):
        o = r['op'].strip().lower()
        if o.startswith('commit'):
            c[r['t']] = i
        if o.startswith('abort') or o.startswith('failure') or o.startswith('rollback'):
            c[r['t']] = -i
    return c


def conflicts(rows):
    ops = rw(rows)
    res = []
    for a in range(len(ops)):
        for b in range(a + 1, len(ops)):
            i, ti, oi, xi = ops[a]
            j, tj, oj, xj = ops[b]
            if ti != tj and xi == xj and 'W' in (oi, oj):
                res.append((i, j, ti, tj, oi, oj, xi))
    return res


def edge_map(rows):
    em = {}
    for (i, j, ti, tj, oi, oj, x) in conflicts(rows):
        em.setdefault((ti, tj), []).append((i, j, oi, oj, x))
    return em


def reach(adj, s):
    seen, st = set(), [s]
    while st:
        u = st.pop()
        for v in adj.get(u, ()):
            if v not in seen:
                seen.add(v)
                st.append(v)
    return seen


def analyse(rows):
    T = txns_of([r for r in rows if OPRE.match(r['op'])] or rows)
    em = edge_map(rows)
    adj = {}
    for (u, v) in em:
        adj.setdefault(u, set()).add(v)
    cyc_edges = {(u, v) for (u, v) in em if u in reach(adj, v)}
    orders = []

    def topo(done, left):
        if len(orders) > 60:
            return
        if not left:
            orders.append(list(done))
            return
        for n in sorted(left, key=lambda s: (len(s), s)):
            if all((p, n) not in em for p in left if p != n):
                topo(done + [n], left - {n})
    if not cyc_edges:
        topo([], set(T))
    # one explicit cycle
    cycle = None
    if cyc_edges:
        u, v = sorted(cyc_edges)[0]
        # path v -> u
        prev = {v: None}
        st = [v]
        while st:
            a = st.pop(0)
            if a == u:
                break
            for b in sorted(adj.get(a, ())):
                if b not in prev:
                    prev[b] = a
                    st.append(b)
        path = [u]
        while path[-1] != v:
            path.append(prev[path[-1]])
        path.reverse()            # v ... u
        cycle = [u] + path         # u -> v -> ... -> u
    return dict(T=T, em=em, cyc=cyc_edges, orders=orders, cycle=cycle)


# ------------------------------------------------------------------ renderers
def esc(s):
    return html.escape(s, quote=False)


def fmt_op(op):
    o = esc(op)
    low = op.lower()
    cls = 'op'
    if low.startswith('commit'):
        cls += ' op-c'
    elif low.startswith(('abort', 'failure', 'rollback', 'fail')):
        cls += ' op-a'
    elif 'lock' in low:
        cls += ' op-l'
    return f'<span class="{cls}">{o}</span>'


def r_sched(sid):
    d = SCHED[sid]
    rows = parse(d['s'])
    T = d.get('txns') or txns_of(rows)
    has_note = any(r['note'] for r in rows)
    cap = d.get('cap', '')
    h = ['<div class="sched-wrap"><table class="sched">']
    if cap:
        h.append(f'<caption>{cap}</caption>')
    h.append('<thead><tr><th class="st">Step</th>')
    for i, t in enumerate(T):
        h.append(f'<th class="tx tx{i % 6}">{esc(t)}</th>')
    if has_note:
        h.append(f'<th class="nt">{esc(d.get("notehead", "Remarks / values"))}</th>')
    h.append('</tr></thead><tbody>')
    for k, r in enumerate(rows, 1):
        rc = {'!': ' class="hl-bad"', '*': ' class="hl-key"'}.get(r['mark'], '')
        h.append(f'<tr{rc}><td class="st">{k}</td>')
        for t in T:
            h.append(f'<td>{fmt_op(r["op"]) if r["t"] == t else ""}</td>')
        if has_note:
            h.append(f'<td class="nt">{r["note"]}</td>')
        h.append('</tr>')
    h.append('</tbody></table></div>')
    return ''.join(h)


def r_pgraph(sid, opts=''):
    rows = parse(SCHED[sid]['s'])
    A = analyse(rows)
    T = A['T']
    nodes = circle_layout(T)
    edges = []
    for (u, v), lst in sorted(A['em'].items()):
        items = sorted({x for (_, _, _, _, x) in lst})
        edges.append(dict(u=u, v=v, label='' if 'nolabel' in opts else ','.join(items),
                          cls='cyc' if (u, v) in A['cyc'] else ''))
    cap = SCHED[sid].get('gcap', f'Precedence graph')
    return digraph(nodes, edges, caption=cap, big=len(T) > 4)


def r_conf(sid):
    rows = parse(SCHED[sid]['s'])
    cs = conflicts(rows)
    h = ['<div class="tbl-wrap"><table class="tbl small"><thead><tr><th>#</th><th>Earlier operation (step)</th>'
         '<th>Later operation (step)</th><th>Item</th><th>Type</th><th>Edge</th></tr></thead><tbody>']
    for n, (i, j, ti, tj, oi, oj, x) in enumerate(cs, 1):
        h.append(f'<tr><td>{n}</td><td><code>{oi}<sub>{ti[1:]}</sub>({x})</code> &nbsp;({i})</td>'
                 f'<td><code>{oj}<sub>{tj[1:]}</sub>({x})</code> &nbsp;({j})</td><td>{x}</td>'
                 f'<td>{oi}–{oj}</td><td><b>{ti} → {tj}</b></td></tr>')
    if not cs:
        h.append('<tr><td colspan="6">No conflicting pairs.</td></tr>')
    h.append('</tbody></table></div>')
    return ''.join(h)


def r_edges(sid):
    rows = parse(SCHED[sid]['s'])
    ops = rw(rows)
    items = []
    for (_, _, _, x) in ops:
        if x not in items:
            items.append(x)
    items.sort()
    em_all = set()
    h = ['<div class="tbl-wrap"><table class="tbl small"><thead><tr><th>Item</th>'
         '<th>Operations on the item, in schedule order (step)</th><th>Edges contributed</th></tr></thead><tbody>']
    for x in items:
        seq = [(i, t, o) for (i, t, o, y) in ops if y == x]
        seqtxt = ', '.join(f'{o.lower()}<sub>{t[1:]}</sub>({i})' for (i, t, o) in seq)
        es = []
        for a in range(len(seq)):
            for b in range(a + 1, len(seq)):
                i, ti, oi = seq[a]
                j, tj, oj = seq[b]
                if ti != tj and 'W' in (oi, oj) and (ti, tj) not in es:
                    es.append((ti, tj))
        es.sort(key=lambda e: (int(e[0][1:]), int(e[1][1:])))
        new = [e for e in es if e not in em_all]
        em_all.update(es)
        etxt = ', '.join(f'{a}→{b}' for a, b in es)
        h.append(f'<tr><td><b>{x}</b></td><td><code class="seq">{seqtxt}</code></td><td>{etxt}</td></tr>')
    h.append('</tbody></table></div>')
    return ''.join(h)


def r_verdict(sid):
    rows = parse(SCHED[sid]['s'])
    A = analyse(rows)
    E = sorted(A['em'])
    elist = ', '.join(f'{u}→{v}' for u, v in E) or 'none'
    if A['cycle']:
        cyc = ' → '.join(A['cycle'])
        return (f'<div class="verdict bad"><b>Edges:</b> {elist}<br><b>Cycle:</b> {cyc}<br>'
                f'⇒ The precedence graph has a cycle, so the schedule is <b>NOT conflict serializable</b>.</div>')
    ords = [' → '.join(o) for o in A['orders']]
    many = 'Equivalent serial schedules' if len(ords) > 1 else 'Equivalent serial schedule'
    return (f'<div class="verdict good"><b>Edges:</b> {elist}<br><b>No cycle</b> ⇒ the schedule is '
            f'<b>conflict serializable</b>.<br><b>{many} (topological order):</b> ' +
            ' &nbsp;|&nbsp; '.join(f'<b>{o}</b>' for o in ords) + '</div>')


def r_recov(sid):
    rows = parse(SCHED[sid]['s'])
    ops = rw(rows)
    cs = commit_step(rows)
    lastw = {}
    reads = []        # (step, reader, item, writer, writer_wstep)
    strict_viol = []
    for (i, t, o, x) in ops:
        prev = lastw.get(x)
        if prev and prev[0] != t:
            w, ws = prev
            wc = cs.get(w)
            done_before = wc is not None and abs(wc) < i
            if o == 'R':
                reads.append((i, t, x, w, ws, done_before))
            if not done_before:
                strict_viol.append((i, t, o, x, w))
        if o == 'W':
            lastw[x] = (t, i)
    h = ['<div class="tbl-wrap"><table class="tbl small"><thead><tr><th>Read (step)</th><th>Reads value written by</th>'
         '<th>Writer committed before this read?</th><th>Commit order</th><th>Recoverable for this pair?</th></tr></thead><tbody>']
    rec_ok = True
    casc_ok = True
    no_commits = not any(v > 0 for v in cs.values())

    def when(tx, v):
        if v is None:
            return f'{tx}: no commit shown'
        return f'{tx} commits at {v}' if v > 0 else f'{tx} ABORTS at {-v}'
    for (i, t, x, w, ws, done) in reads:
        rc, wc = cs.get(t), cs.get(w)
        ordtxt = when(w, wc) + ', ' + when(t, rc)
        if no_commits:
            ok = 'commit order not given'
        elif rc is None or rc < 0:
            ok = 'Yes (reader never commits)'
        elif wc is not None and wc > 0 and wc < rc:
            ok = 'Yes'
        else:
            ok = '<b>NO</b> — reader committed while writer was uncommitted'
            rec_ok = False
        if not done:
            casc_ok = False
        h.append(f'<tr><td><code>r<sub>{t[1:]}</sub>({x})</code> ({i})</td><td>{w} (w at step {ws})</td>'
                 f'<td>{"Yes" if done else "<b>No</b> (dirty read)"}</td><td>{ordtxt}</td><td>{ok}</td></tr>')
    if not reads:
        h.append('<tr><td colspan="5">No transaction reads a value written by another transaction.</td></tr>')
    h.append('</tbody></table></div>')
    strict = not strict_viol
    rtxt = ('cannot be decided (no commits given)' if no_commits else ('Yes' if rec_ok else 'No'))
    summ = (f'<div class="verdict {"good" if rec_ok else "bad"}">Recoverable: <b>{rtxt}</b> &nbsp;·&nbsp; '
            f'Cascadeless: <b>{"Yes" if casc_ok else "No"}</b> &nbsp;·&nbsp; Strict: <b>{"Yes" if strict else "No"}</b>')
    if strict_viol:
        summ += '<br><small>Strictness violated at: ' + ', '.join(
            f'{o.lower()}<sub>{t[1:]}</sub>({x}) touches {x} last written by uncommitted {w}' for (i, t, o, x, w) in strict_viol) + '</small>'
    summ += '</div>'
    return ''.join(h) + summ


def r_matrix(sid):
    rows = parse(SCHED[sid]['s'])
    A = analyse(rows)
    T = A['T']
    h = ['<div class="tbl-wrap" style="max-width:560px;margin:14px auto"><table class="tbl center small"><tr><th>from \\ to</th>']
    h += [f'<th>{t}</th>' for t in T] + ['</tr>']
    for u in T:
        h.append(f'<tr><th>{u}</th>')
        for v in T:
            if u == v:
                h.append('<td class="muted">—</td>')
            else:
                h.append('<td class="n">✔</td>' if (u, v) in A['em'] else '<td></td>')
        h.append('</tr>')
    h.append('</table></div>')
    return ''.join(h)


def r_svg(name):
    return getattr(figures, name)()


HANDLERS = dict(sched=r_sched, pgraph=r_pgraph, conf=r_conf, edges=r_edges,
                verdict=r_verdict, recov=r_recov, svg=r_svg, matrix=r_matrix)


def expand(text):
    def rep(m):
        kind, arg = m.group(1), m.group(2)
        opts = ''
        if '|' in arg:
            arg, opts = arg.split('|', 1)
        f = HANDLERS[kind]
        return f(arg, opts) if kind == 'pgraph' else f(arg)
    return re.sub(r'\{\{(\w+):([^}]+)\}\}', rep, text)


# ------------------------------------------------------------------ assemble
def toc(body):
    items = re.findall(r'<h([23]) id="([^"]+)"[^>]*>(.*?)</h\1>', body, re.S)
    out = ['<ul class="toc">']
    open_sub = False
    for lvl, hid, txt in items:
        txt = re.sub(r'<span class="beyond-tag">.*?</span>', '', txt)
        txt = re.sub(r'<[^>]+>', '', txt.replace('</span>', ' </span>')).strip()
        if lvl == '2':
            if open_sub:
                out.append('</ul></li>')
                open_sub = False
            else:
                if len(out) > 1:
                    out.append('</li>')
            out.append(f'<li><a href="#{hid}" class="t2">{txt}</a>')
        else:
            if not open_sub:
                out.append('<ul>')
                open_sub = True
            out.append(f'<li><a href="#{hid}" class="t3">{txt}</a></li>')
    if open_sub:
        out.append('</ul></li>')
    else:
        out.append('</li>')
    out.append('</ul>')
    return ''.join(out)


def main():
    parts_dir = os.path.join(BASE, 'parts')
    body = ''
    for fn in sorted(os.listdir(parts_dir)):
        if fn.endswith('.html') and os.environ.get('PARTS','') in fn:
            body += open(os.path.join(parts_dir, fn), encoding='utf-8').read() + '\n'
    body = expand(body)
    css = open(os.path.join(BASE, 'style.css'), encoding='utf-8').read()
    js = open(os.path.join(BASE, 'app.js'), encoding='utf-8').read()
    page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>DBMS Unit 5 Notes</title>
<meta name="description" content="Complete notes for DBMS Unit 5: transactions, ACID, schedules, serializability, recoverability, locking (2PL family), deadlocks, database recovery and database security, with topic-wise solved PYQs.">
<style>{css}</style>
</head>
<body>
<button class="menu-btn" id="menuBtn" aria-label="Open contents">☰ Contents</button>
<aside class="sidebar" id="sidebar">
  <div class="side-head">
    <div class="side-title">DBMS · Unit 5</div>
    <div class="side-tools">
      <button id="themeBtn" title="Toggle light / dark">◐ Theme</button>
      <button id="expandBtn" title="Show / hide all PYQ answers">▾ Answers</button>
    </div>
  </div>
  <nav>{toc(body)}</nav>
</aside>
<main class="content" id="content">
{body}
</main>
<script>{js}</script>
</body>
</html>'''
    open(OUT, 'w', encoding='utf-8').write(page)
    left = re.findall(r'\{\{[^}]+\}\}', page)
    print('written', OUT, len(page) // 1024, 'KB', 'unresolved:', left[:5])


if __name__ == '__main__':
    main()
