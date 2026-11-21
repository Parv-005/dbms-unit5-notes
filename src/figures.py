"""Hand-designed figures (inline SVG, theme-aware via CSS classes)."""
import math
from svglib import markers, uid, esc, digraph


class Fig:
    def __init__(self, w, h, label='figure', maxw=None):
        self.mid = uid()
        self.w, self.h = w, h
        self.label = label
        self.maxw = maxw or w
        self.p = []

    def box(self, x, y, w, h, text='', cls='', rx=10, tcls='t', fs=None):
        self.p.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" class="bx {cls}"/>')
        if text:
            self.text(x + w / 2, y + h / 2, text, tcls, fs=fs)

    def text(self, x, y, s, cls='t', anchor='middle', fs=None, lh=16):
        lines = s.split('\n')
        st = f' style="font-size:{fs}px"' if fs else ''
        for k, ln in enumerate(lines):
            dy = (k - (len(lines) - 1) / 2) * lh
            self.p.append(f'<text x="{x:.1f}" y="{y + dy:.1f}" class="{cls}" text-anchor="{anchor}" '
                          f'dominant-baseline="central"{st}>{esc(ln)}</text>')

    def line(self, x1, y1, x2, y2, cls='ln'):
        self.p.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="{cls}"/>')

    def poly(self, pts, cls='ln'):
        d = ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts)
        self.p.append(f'<polyline points="{d}" class="{cls}" fill="none"/>')

    def arrow(self, x1, y1, x2, y2, c='ink', dash=False, curve=0, both=False, w=None):
        d = ' dashed' if dash else ''
        sw = f' style="stroke-width:{w}"' if w else ''
        ms = f' marker-start="url(#{self.mid}-{c})"' if both else ''
        if curve:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            dx, dy = x2 - x1, y2 - y1
            L = math.hypot(dx, dy) or 1
            cx, cy = mx - dy / L * curve, my + dx / L * curve
            self.p.append(f'<path d="M{x1},{y1} Q{cx:.1f},{cy:.1f} {x2},{y2}" class="edge e-{c}{d}"{sw} '
                          f'marker-end="url(#{self.mid}-{c})"{ms}/>')
        else:
            self.p.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="edge e-{c}{d}"{sw} '
                          f'marker-end="url(#{self.mid}-{c})"{ms}/>')

    def raw(self, s):
        self.p.append(s)

    def render(self, caption=''):
        svg = (f'<svg class="fig-svg" viewBox="0 0 {self.w} {self.h}" style="max-width:{self.maxw}px" role="img" '
               f'aria-label="{esc(self.label)}">' + markers(self.mid) + ''.join(self.p) + '</svg>')
        cap = f'<figcaption>{caption}</figcaption>' if caption else ''
        return f'<figure class="fig">{svg}{cap}</figure>'


# ------------------------------------------------------------------ roadmap
def roadmap():
    f = Fig(860, 330, 'Unit 5 roadmap')
    f.box(330, 12, 200, 50, 'TRANSACTION\n(logical unit of work)', 'bx-acc', tcls='t tb')
    f.text(545, 37, 'must satisfy ACID — but has two enemies ↓', 't ts', anchor='start')
    f.box(40, 105, 330, 46, 'Enemy 1: CONCURRENCY\n(many transactions at once)', 'bx-warn', tcls='t tb')
    f.box(490, 105, 330, 46, 'Enemy 2: FAILURES\n(crash, disk failure, errors)', 'bx-bad', tcls='t tb')
    f.arrow(400, 62, 230, 103)
    f.arrow(460, 62, 650, 103)
    f.box(40, 175, 330, 40, 'Concurrency problems: lost update, dirty read,\nunrepeatable read, phantom', '', tcls='t ts')
    f.box(40, 228, 330, 40, 'Theory: schedules · serializability ·\nrecoverability', '', tcls='t ts')
    f.box(40, 281, 330, 40, 'Solution: concurrency control — locks, 2PL family,\ndeadlock handling, timestamps', 'bx-good', tcls='t ts')
    f.box(490, 175, 330, 40, 'Failure types · storage types ·\nwhat must be undone / redone', '', tcls='t ts')
    f.box(490, 228, 330, 40, 'Solution: log-based recovery (deferred /\nimmediate), checkpoints, shadow paging', 'bx-good', tcls='t ts')
    f.box(490, 281, 330, 40, 'Plus: DATABASE SECURITY — protecting data\nfrom unauthorised access (not failures)', 'bx-pur', tcls='t ts')
    for y in (151, 215, 268):
        f.arrow(205, y, 205, y + 10 if y == 151 else y + 13)
    for y in (151, 215):
        f.arrow(655, y, 655, y + 10 if y == 151 else y + 13)
    f.text(205, 165 - 2, '', 't')
    return f.render('The whole unit on one page: a transaction must stay correct despite <b>concurrency</b> (Isolation) and despite <b>failures</b> (Atomicity &amp; Durability).')


# ------------------------------------------------------------------ section 1
def buffer():
    f = Fig(820, 250, 'read and write through the buffer')
    f.box(20, 60, 200, 130, '', 'bx-mut')
    f.text(120, 80, 'Transaction T1', 't tb')
    f.text(120, 105, '(program / work area)', 't ts')
    f.box(45, 125, 150, 44, 'local variable\nx = 4000 → 3500', 'bx-acc', tcls='t ts')
    f.box(310, 60, 200, 130, '', 'bx-mut')
    f.text(410, 80, 'Main memory', 't tb')
    f.text(410, 105, '(volatile)', 't ts')
    f.box(335, 125, 150, 44, 'buffer block\ncontaining X', 'bx-warn', tcls='t ts')
    f.box(600, 60, 200, 130, '', 'bx-mut')
    f.text(700, 80, 'Disk (database)', 't tb')
    f.text(700, 105, '(non-volatile)', 't ts')
    f.box(625, 125, 150, 44, 'block on disk\nX = 4000', 'bx-good', tcls='t ts')
    f.arrow(335, 138, 197, 138, 'acc')
    f.text(266, 124, 'read(X)', 't tb ts')
    f.arrow(197, 158, 335, 158, 'bad')
    f.text(266, 176, 'write(X)', 't tb ts')
    f.arrow(625, 138, 487, 138, 'acc')
    f.text(556, 124, 'input(B)', 't ts')
    f.arrow(487, 158, 625, 158, 'bad')
    f.text(556, 176, 'output(B)', 't ts')
    f.text(410, 222, 'read/write move data between the transaction and the BUFFER;  input/output move whole blocks between buffer and DISK.', 't ts')
    f.text(410, 240, 'write(X) does NOT guarantee X is on disk yet — that is why we need recovery (logs).', 't ts tw')
    return f.render('How <code>read(X)</code> and <code>write(X)</code> really work.')


def acid():
    f = Fig(860, 250, 'ACID properties and who enforces them')
    data = [('A', 'Atomicity', 'all or nothing', 'Recovery manager\n(undo using log)', 'bx-acc'),
            ('C', 'Consistency', 'valid state → valid state', 'Programmer +\nintegrity constraints', 'bx-good'),
            ('I', 'Isolation', 'as if running alone', 'Concurrency-control\nsubsystem (locks)', 'bx-warn'),
            ('D', 'Durability', 'committed = permanent', 'Recovery manager\n(redo using log)', 'bx-pur')]
    for k, (L, name, one, who, c) in enumerate(data):
        x = 20 + k * 210
        f.box(x, 20, 190, 100, '', c)
        f.text(x + 95, 45, L, 't tbig')
        f.text(x + 95, 78, name, 't tb')
        f.text(x + 95, 100, one, 't ts')
        f.arrow(x + 95, 122, x + 95, 160, 'mut')
        f.text(x + 125, 141, 'ensured by', 't tx', anchor='start')
        f.box(x, 162, 190, 60, who, '', tcls='t ts')
    f.text(430, 240, 'Atomicity + Durability → RECOVERY system      ·      Isolation → CONCURRENCY CONTROL      ·      Consistency → application + DBMS checks', 't tx')
    return f.render('The four ACID properties and the DBMS component responsible for each.')


def states():
    nodes = [('B', 40, 170, 'Begin'), ('A', 170, 170, 'Active'), ('P', 390, 60, 'Partially\\nCommitted'),
             ('C', 640, 60, 'Committed'), ('F', 390, 280, 'Failed'), ('Ab', 640, 280, 'Aborted'),
             ('E', 820, 170, 'Terminated\\n(End)')]
    edges = [dict(u='B', v='A', label=''),
             dict(u='A', v='P', label='last operation\nexecuted', cls='good'),
             dict(u='P', v='C', label='commit (log written)', cls='good'),
             dict(u='A', v='F', label='error / failure', cls='bad'),
             dict(u='P', v='F', label='failure before commit', cls='bad'),
             dict(u='F', v='Ab', label='rollback', cls='bad'),
             dict(u='C', v='E', label=''),
             dict(u='Ab', v='E', label='restart or kill')]
    for e in edges:
        e['label'] = e['label'].replace('\n', ' ')
    g = digraph(nodes, edges, caption='', shape='box', nw=120, nh=50, pad=20,
                node_cls={'B': 'n-mut', 'E': 'n-mut', 'A': 'n-acc', 'P': 'n-warn', 'C': 'n-good', 'F': 'n-bad', 'Ab': 'n-bad'})
    return g.replace('</figure>', '<figcaption>Transaction state diagram. Green path = success, red path = failure. '
                     'Once a transaction is <b>Committed</b> it can no longer be rolled back.</figcaption></figure>')


# ------------------------------------------------------------------ section 4
def exec_timeline():
    f = Fig(860, 300, 'serial, concurrent and parallel execution')
    x0, unit = 150, 55

    def bar(lane_y, start, length, label, c):
        f.box(x0 + start * unit, lane_y, length * unit - 3, 26, label, c, rx=5, tcls='t ts')
    f.text(20, 40, 'Serial', 't tb', anchor='start')
    f.text(20, 58, '(1 CPU)', 't tx', anchor='start')
    for i in range(3):
        bar(36, i, 1, f'T1·{i + 1}', 'bx-acc')
    for i in range(3):
        bar(36, 3 + i, 1, f'T2·{i + 1}', 'bx-warn')
    f.text(20, 120, 'Concurrent', 't tb', anchor='start')
    f.text(20, 138, '(1 CPU, interleaved)', 't tx', anchor='start')
    seq = ['T1', 'T2', 'T1', 'T2', 'T1', 'T2']
    cnt = {'T1': 0, 'T2': 0}
    for i, t in enumerate(seq):
        cnt[t] += 1
        bar(116, i, 1, f'{t}·{cnt[t]}', 'bx-acc' if t == 'T1' else 'bx-warn')
    f.text(20, 205, 'Parallel', 't tb', anchor='start')
    f.text(20, 223, '(2 CPUs, truly', 't tx', anchor='start')
    f.text(20, 237, 'simultaneous)', 't tx', anchor='start')
    for i in range(3):
        bar(186, i, 1, f'T1·{i + 1}', 'bx-acc')
        bar(218, i, 1, f'T2·{i + 1}', 'bx-warn')
    f.text(x0 - 8, 199, 'CPU1', 't tx', anchor='end')
    f.text(x0 - 8, 231, 'CPU2', 't tx', anchor='end')
    f.arrow(x0, 268, x0 + 6 * unit + 20, 268, 'mut')
    f.text(x0 + 3 * unit, 285, 'time →', 't tx')
    f.text(x0 + 6 * unit + 40, 49, 'finishes at t = 6', 't ts', anchor='start')
    f.text(x0 + 6 * unit + 40, 129, 'also t = 6 on paper, but while one', 't ts', anchor='start')
    f.text(x0 + 6 * unit + 40, 145, 'waits for disk I/O the other uses CPU', 't ts', anchor='start')
    f.text(x0 + 6 * unit + 40, 214, 'finishes at t = 3', 't ts', anchor='start')
    return f.render('Serial vs concurrent (interleaved) vs parallel execution of two transactions (each box = one step).')


# ------------------------------------------------------------------ section 6/7 Venns
def venn_serial():
    f = Fig(700, 330, 'classes of schedules by serializability')
    f.box(10, 10, 680, 310, '', 'bx-mut', rx=22)
    f.text(30, 34, 'All schedules (includes non-serializable ones)', 't tb', anchor='start')
    f.box(50, 55, 600, 245, '', 'bx-pur', rx=20)
    f.text(70, 78, 'View-serializable', 't tb', anchor='start')
    f.text(470, 78, 'VS but not CS ⇒ has blind writes', 't tx', anchor='start')
    f.box(95, 100, 510, 180, '', 'bx-acc', rx=18)
    f.text(115, 123, 'Conflict-serializable  (tested with a precedence graph)', 't tb', anchor='start')
    f.box(160, 150, 380, 110, '', 'bx-good', rx=16)
    f.text(350, 190, 'Serial schedules', 't tb')
    f.text(350, 215, 'n transactions → n! serial orders', 't ts')
    return f.render('Serial ⊂ Conflict-serializable ⊂ View-serializable ⊂ All schedules.')


def venn_recov():
    f = Fig(700, 330, 'classes of schedules by recoverability')
    f.box(10, 10, 680, 310, '', 'bx-mut', rx=22)
    f.text(30, 34, 'All schedules (includes non-recoverable ones ✗)', 't tb', anchor='start')
    f.box(50, 55, 600, 245, '', 'bx-warn', rx=20)
    f.text(70, 78, 'Recoverable — reader commits after the writer it read from', 't tb', anchor='start')
    f.box(95, 100, 510, 180, '', 'bx-acc', rx=18)
    f.text(115, 123, 'Cascadeless (ACA) — read only committed data', 't tb', anchor='start')
    f.box(140, 145, 420, 120, '', 'bx-pur', rx=16)
    f.text(160, 168, 'Strict — no read OR write of uncommitted data', 't tb', anchor='start')
    f.box(220, 190, 260, 60, 'Serial schedules', 'bx-good', rx=14, tcls='t tb')
    return f.render('Serial ⊂ Strict ⊂ Cascadeless ⊂ Recoverable ⊂ All schedules. '
                    '(This classification is independent of serializability.)')


# ------------------------------------------------------------------ section 8 locking
def lockmgr():
    f = Fig(820, 210, 'lock table')
    f.box(20, 20, 140, 170, '', 'bx-mut')
    f.text(90, 40, 'Lock table', 't tb')
    rows = [('A', [('T1', 'S', 1), ('T3', 'S', 1), ('T2', 'X', 0)]),
            ('B', [('T2', 'X', 1), ('T4', 'S', 0)]),
            ('C', [('T5', 'S', 1)])]
    for k, (item, reqs) in enumerate(rows):
        y = 62 + k * 44
        f.box(45, y, 90, 32, f'item {item}', 'bx-acc', tcls='t ts')
        px = 135
        for j, (t, m, g) in enumerate(reqs):
            x = 200 + j * 150
            f.arrow(px, y + 16, x, y + 16, 'mut')
            f.box(x, y, 120, 32, f'{t} : {m}  {"granted" if g else "waiting"}', 'bx-good' if g else 'bx-bad', tcls='t ts')
            px = x + 120
    f.text(660, 74, '← queue per data item', 't tx', anchor='start')
    f.text(660, 92, '(FIFO order)', 't tx', anchor='start')
    f.text(660, 118, 'T2 waits on A because', 't tx', anchor='start')
    f.text(660, 134, 'X is incompatible with', 't tx', anchor='start')
    f.text(660, 150, 'the S-locks already granted.', 't tx', anchor='start')
    return f.render('The lock manager keeps a <b>lock table</b>: for every locked item, a queue of granted and waiting requests.')


def _staircase(f, x0, y0, w, h, ups, downs, commit=None, lp=None, title='', cls='ln-acc', note=''):
    """ups/downs: list of x-fractions where #locks +1 / -1 (or -k with tuple)"""
    f.box(x0, y0, w, h, '', 'bx-plain', rx=8)
    f.text(x0 + w / 2, y0 + 16, title, 't tb')
    bx, by = x0 + 30, y0 + h - 46
    W, H = w - 50, h - 84
    f.arrow(bx, by, bx + W + 8, by, 'mut')
    f.arrow(bx, by, bx, by - H - 8, 'mut')
    f.text(bx + W, by + 14, 'time', 't tx', anchor='end')
    f.text(bx, by - H - 16, '#locks', 't tx')
    ev = sorted([(u, 1) for u in ups] + [(d[0], -d[1]) if isinstance(d, tuple) else (d, -1) for d in downs])
    n = 0
    mx = max(1, len(ups))
    pts = [(bx, by)]
    for (t, dn) in ev:
        x = bx + t * W
        pts.append((x, by - n / mx * H))
        n += dn
        pts.append((x, by - n / mx * H))
    pts.append((bx + W, by - n / mx * H))
    f.poly(pts, cls)
    if lp is not None:
        x = bx + lp * W
        f.line(x, by, x, by - H - 4, 'ln-dash')
        f.text(x, by + 14, 'lock point', 't tx')
    if commit is not None:
        x = bx + commit * W
        f.line(x, by, x, by - H - 4, 'ln-bad')
        f.text(x, by - H - 10, 'commit', 't tx tbad')
    if note:
        f.text(x0 + w / 2, y0 + h - 10, note, 't tx tb')


def twopl():
    f = Fig(760, 300, '2PL growing and shrinking phases')
    bx, by, W, H = 70, 240, 600, 170
    f.arrow(bx, by, bx + W + 20, by, 'mut')
    f.arrow(bx, by, bx, by - H - 20, 'mut')
    f.text(bx + W + 10, by + 18, 'time', 't ts', anchor='end')
    f.text(bx + 6, by - H - 20, 'number of locks held', 't ts', anchor='start')
    steps = [(0.06, 1), (0.16, 2), (0.27, 3), (0.38, 4)]
    pts = [(bx, by)]
    n = 0
    for t, k in steps:
        x = bx + t * W
        pts.append((x, by - n * 38))
        n = k
        pts.append((x, by - n * 38))
    lpx = bx + 0.45 * W
    pts.append((lpx, by - n * 38))
    for t in (0.55, 0.66, 0.78, 0.9):
        x = bx + t * W
        pts.append((x, by - n * 38))
        n -= 1
        pts.append((x, by - n * 38))
    f.poly(pts, 'ln-acc thick')
    f.line(lpx, by, lpx, by - H - 10, 'ln-dash')
    f.text(lpx, by - H - 14, 'LOCK POINT', 't tb')
    f.text(bx + 0.22 * W, by + 22, '◀ GROWING phase ▶', 't tb tgood')
    f.text(bx + 0.22 * W, by + 40, 'may acquire locks / upgrade S→X; cannot release', 't tx')
    f.text(bx + 0.70 * W, by + 22, '◀ SHRINKING phase ▶', 't tb tbad')
    f.text(bx + 0.70 * W, by + 40, 'may release locks / downgrade X→S; cannot acquire', 't tx')
    f.text(bx + 0.06 * W + 30, by - 20, 'lock-S(A)', 't tx')
    f.text(bx + 0.27 * W + 18, by - 96, 'lock-X(C)', 't tx')
    f.text(bx + 0.62 * W + 22, by - 130, 'unlock(A)', 't tx')
    return f.render('Two-Phase Locking: the number of locks held only rises (growing) and then only falls (shrinking). '
                    'The moment the last lock is obtained is the <b>lock point</b>.')


def twopl_variants():
    f = Fig(880, 500, 'comparison of 2PL variants')
    _staircase(f, 10, 10, 425, 235, [0.08, 0.2, 0.32], [0.5, 0.65, 0.8], commit=0.92, lp=0.32,
               title='Basic 2PL', note='locks released gradually, even before commit')
    _staircase(f, 445, 10, 425, 235, [0.08, 0.2, 0.32], [0.5, (0.92, 2)], commit=0.92, lp=0.32,
               title='Strict 2PL', note='S-locks may go early; all X-locks held till commit')
    _staircase(f, 10, 255, 425, 235, [0.08, 0.2, 0.32], [(0.92, 3)], commit=0.92, lp=0.32,
               title='Rigorous 2PL', note='ALL locks (S and X) held till commit/abort')
    _staircase(f, 445, 255, 425, 235, [0.04, 0.045, 0.05], [0.5, 0.65, 0.8], commit=0.92, lp=0.05,
               title='Conservative (static) 2PL', note='all locks taken before the first operation')
    return f.render('How the four 2PL variants differ in <i>when</i> locks are acquired and released '
                    '(red line = commit, dashed = lock point).')


def hierarchy2pl():
    f = Fig(760, 300, 'relationship of 2PL variants')
    f.box(10, 10, 740, 280, '', 'bx-mut', rx=22)
    f.text(30, 34, 'Schedules allowed by Basic 2PL  (all conflict-serializable)', 't tb', anchor='start')
    f.box(40, 55, 420, 220, '', 'bx-acc', rx=18)
    f.text(60, 78, 'Strict 2PL  (also cascadeless & recoverable)', 't tb', anchor='start')
    f.box(70, 105, 300, 150, '', 'bx-pur', rx=16)
    f.text(220, 150, 'Rigorous 2PL', 't tb')
    f.text(220, 175, 'order of serialization', 't ts')
    f.text(220, 193, '= order of commit', 't ts')
    f.box(330, 120, 400, 140, '', 'bx-warn op70', rx=16)
    f.text(600, 150, 'Conservative 2PL', 't tb')
    f.text(600, 175, 'deadlock-free; may or may', 't ts')
    f.text(600, 193, 'not be strict / rigorous', 't ts')
    f.text(400, 240, 'Conservative +', 't tx')
    f.text(400, 254, 'Rigorous', 't tx')
    return f.render('Rigorous ⊂ Strict ⊂ Basic 2PL. Conservative 2PL is also a subset of basic 2PL but overlaps the others '
                    '(it can be combined with strict/rigorous).')


# ------------------------------------------------------------------ deadlock
def deadlock_rag():
    nodes = [('T1', 120, 50, 'T1'), ('T2', 520, 50, 'T2'), ('S', 120, 220, 'Student'), ('G', 520, 220, 'Grade')]
    edges = [dict(u='S', v='T1', label='held by', cls='good'), dict(u='G', v='T2', label='held by', cls='good'),
             dict(u='T1', v='G', label='requests', cls='bad', dash=True, lpos=(250, 110)),
             dict(u='T2', v='S', label='requests', cls='bad', dash=True, lpos=(390, 110))]
    g = digraph(nodes, edges, shape='box', nw=130, nh=44, node_cls={'T1': 'n-acc', 'T2': 'n-acc', 'S': 'n-warn', 'G': 'n-warn'})
    return g.replace('</figure>', '<figcaption>T1 holds Student and wants Grade; T2 holds Grade and wants Student — '
                     'a cycle of waiting = <b>deadlock</b>.</figcaption></figure>')


def waitfor():
    nodes = [('T1', 90, 60, 'T1'), ('T2', 300, 60, 'T2'), ('T3', 300, 220, 'T3'), ('T4', 90, 220, 'T4'), ('T5', 480, 140, 'T5')]
    edges = [dict(u='T1', v='T2', label='waits for', cls='bad'), dict(u='T2', v='T3', label='', cls='bad'),
             dict(u='T3', v='T4', label='', cls='bad'), dict(u='T4', v='T1', label='', cls='bad'),
             dict(u='T5', v='T2', label='waits for')]
    g = digraph(nodes, edges)
    return g.replace('</figure>', '<figcaption>Wait-for graph: edge Ti → Tj means “Ti is waiting for a lock held by Tj”. '
                     'Cycle T1 → T2 → T3 → T4 → T1 ⇒ deadlock. T5 is waiting but is not part of the deadlock.</figcaption></figure>')


def waitdie():
    f = Fig(820, 250, 'wait-die and wound-wait')
    f.p.append('')
    f.text(205, 10, 'WAIT–DIE  (non-preemptive)', 't tb')
    f.text(615, 10, 'WOUND–WAIT  (preemptive)', 't tb')
    for k, base in enumerate((0, 410)):
        f.box(base + 20, 40, 120, 40, 'Older Ti\n(TS = 5)', 'bx-acc', tcls='t ts')
        f.box(base + 250, 40, 120, 40, 'Younger Tj\n(TS = 10)', 'bx-warn', tcls='t ts')
        f.box(base + 20, 150, 120, 40, 'Younger Tj\n(TS = 10)', 'bx-warn', tcls='t ts')
        f.box(base + 250, 150, 120, 40, 'Older Ti\n(TS = 5)', 'bx-acc', tcls='t ts')
        f.arrow(base + 142, 60, base + 248, 60, 'mut')
        f.text(base + 195, 32, 'requests lock held by', 't tx')
        f.arrow(base + 142, 170, base + 248, 170, 'mut')
        f.text(base + 195, 142, 'requests lock held by', 't tx')
    f.text(205, 105, 'Older requester → WAITS', 't tb tgood')
    f.text(205, 215, 'Younger requester → DIES (rolled back,', 't tb tbad')
    f.text(205, 233, 'restarts later with the SAME timestamp)', 't tx')
    f.text(615, 105, 'Older requester → WOUNDS younger (Tj rolled back)', 't tb tbad')
    f.text(615, 215, 'Younger requester → WAITS', 't tb tgood')
    return f.render('Rule of thumb: in both schemes only the <b>younger</b> transaction is ever rolled back, so the oldest '
                    'transaction always survives ⇒ no deadlock and no starvation.')


# ------------------------------------------------------------------ recovery
def storage():
    f = Fig(820, 190, 'storage types')
    data = [('Volatile storage', 'main memory, cache', 'contents LOST on\nsystem crash / power cut', 'bx-bad'),
            ('Non-volatile storage', 'disk, SSD, tape', 'survives crash, but can\nbe lost on disk failure', 'bx-warn'),
            ('Stable storage', 'several non-volatile copies\non independent devices/sites', 'information is\n(practically) NEVER lost', 'bx-good')]
    for k, (a, b, c, cls) in enumerate(data):
        x = 20 + k * 270
        f.box(x, 20, 250, 150, '', cls)
        f.text(x + 125, 45, a, 't tb')
        f.text(x + 125, 82, b, 't ts')
        f.line(x + 20, 112, x + 230, 112, 'ln-mut')
        f.text(x + 125, 140, c, 't ts')
    return f.render('Storage types. The <b>log</b> is kept on <b>stable storage</b> (in practice: mirrored disks / remote copies).')


def wal():
    f = Fig(820, 250, 'write-ahead logging')
    f.box(20, 30, 360, 120, '', 'bx-mut')
    f.text(200, 48, 'MAIN MEMORY (volatile)', 't tb')
    f.box(40, 70, 150, 60, 'log buffer\n<T1, A, 600, 500>', 'bx-pur', tcls='t ts')
    f.box(210, 70, 150, 60, 'database buffer\nblock with A = 500', 'bx-warn', tcls='t ts')
    f.box(440, 30, 360, 120, '', 'bx-mut')
    f.text(620, 48, 'DISK', 't tb')
    f.box(460, 70, 150, 60, 'log file\n(stable storage)', 'bx-pur', tcls='t ts')
    f.box(630, 70, 150, 60, 'database file', 'bx-good', tcls='t ts')
    f.arrow(115, 132, 115, 195, 'acc', curve=0)
    f.arrow(115, 195, 535, 195, 'acc')
    f.arrow(535, 195, 535, 132, 'acc')
    f.text(320, 212, '① FIRST: force the log record(s) to stable storage', 't tb tacc')
    f.arrow(285, 68, 705, 68, 'bad', curve=-30)
    f.text(495, 18, '② ONLY THEN may the data block be written to disk', 't tb tbad')
    f.text(410, 238, 'and <Ti commit> must reach stable storage before Ti is declared committed.', 't ts')
    return f.render('Write-Ahead Logging (WAL) rule: <b>log first, data later</b>. This guarantees the old value is always '
                    'available for UNDO and the new value for REDO.')


def checkpoint():
    f = Fig(860, 330, 'checkpoint recovery timeline')
    x0, x1 = 90, 820
    tc, tf = 380, 700
    f.arrow(x0, 290, x1, 290, 'mut')
    f.text(x1 - 10, 306, 'time', 't tx', anchor='end')
    f.line(tc, 20, tc, 290, 'ln-acc thick')
    f.text(tc, 14, 'checkpoint (tc)', 't tb tacc')
    f.line(tf, 20, tf, 290, 'ln-bad thick')
    f.text(tf, 14, 'system crash (tf)', 't tb tbad')
    bars = [('T1', 110, 290, True, 'ignore — committed before checkpoint (already on disk)', 'mut'),
            ('T2', 250, 560, True, 'REDO — committed after checkpoint', 'good'),
            ('T3', 430, 600, True, 'REDO — started & committed after checkpoint', 'good'),
            ('T4', 300, 760, False, 'UNDO — active at crash, no commit', 'bad'),
            ('T5', 520, 760, False, 'UNDO — active at crash, no commit', 'bad')]
    for k, (t, s, e, com, lab, c) in enumerate(bars):
        y = 50 + k * 47
        f.text(x0 - 30, y + 9, t, 't tb')
        ee = min(e, tf) if not com else e
        f.box(s, y, ee - s, 18, '', f'bx-{"mut" if c == "mut" else ("good" if c == "good" else "bad")}', rx=4)
        if com:
            f.text(e + 6, y + 9, '✔ commit', 't tx', anchor='start')
        else:
            f.text(tf + 8, y + 9, '✖ crash', 't tx tbad', anchor='start')
        f.text((s + ee) / 2, y + 30, lab, 't tx halo')
    return f.render('Using a checkpoint: only transactions active at or after the checkpoint need attention. '
                    'Committed ones are REDONE, uncommitted ones are UNDONE, older ones are ignored.')


def recov_phases():
    f = Fig(940, 200, 'redo and undo phases')
    f.box(20, 80, 900, 40, '', 'bx-mut', rx=4)
    labels = ['<T0 start>', '<checkpoint {T1,T2}>', '<T1 commit>', '<T3 start>', '<T2, B, 50, 70>', '<T3, C, 5, 9>', 'crash']
    for k, s in enumerate(labels):
        x = 26 + k * 128
        f.box(x, 85, 122, 30, s, 'bx-acc' if 'checkpoint' in s else ('bx-bad' if s == 'crash' else ''), rx=4, tcls='t tx')
    f.arrow(170, 60, 880, 60, 'good', w=2.2)
    f.text(500, 45, 'PHASE 1 — REDO: scan FORWARD from the last checkpoint, repeat every update; build the undo-list', 't tb tgood')
    f.arrow(880, 140, 170, 140, 'bad', w=2.2)
    f.text(500, 160, 'PHASE 2 — UNDO: scan BACKWARD, undo updates of transactions in the undo-list (T2, T3)', 't tb tbad')
    f.text(500, 182, 'write <Ti abort> for each of them when its <Ti start> is reached', 't tx')
    return f.render('Modern recovery algorithm (Korth): redo (“repeat history”) forwards, then undo incomplete transactions backwards.')


def shadow():
    f = Fig(860, 340, 'shadow paging')
    f.box(30, 40, 150, 260, '', 'bx-mut')
    f.text(105, 25, 'Shadow page table', 't tb')
    f.text(105, 318, '(on disk, never changed)', 't tx')
    f.box(680, 40, 150, 260, '', 'bx-mut')
    f.text(755, 25, 'Current page table', 't tb')
    f.text(755, 318, '(in memory, being updated)', 't tx')
    f.text(430, 25, 'Pages on disk', 't tb')
    pages = {1: 70, 2: 120, 3: 170, 4: 220, 5: 270}
    for i, y in pages.items():
        f.box(45, y - 18, 120, 34, f'entry {i}', '', rx=4, tcls='t ts')
        f.box(695, y - 18, 120, 34, f'entry {i}', 'bx-warn' if i in (2, 5) else '', rx=4, tcls='t ts')
    old = {1: 70, 2: 120, 3: 170, 4: 220, 5: 270}
    for i, y in old.items():
        f.box(330, y - 15, 110, 30, f'page {i}' + (' (old)' if i in (2, 5) else ''), 'bx-plain', rx=4, tcls='t tx')
    f.box(480, 105, 120, 30, 'page 2 (new)', 'bx-warn', rx=4, tcls='t tx')
    f.box(480, 255, 120, 30, 'page 5 (new)', 'bx-warn', rx=4, tcls='t tx')
    for i, y in old.items():
        f.arrow(165, y, 328, y, 'mut')
    for i, y in old.items():
        if i in (2, 5):
            f.arrow(695, y, 602, y, 'acc')
        else:
            f.arrow(695, y, 442, y, 'mut', curve=-8)
    f.text(430, 312, 'Commit = atomically switch the "current DB root" pointer from the shadow table to the current table.', 't tx tacc')
    f.text(430, 330, 'Crash before commit = just keep the shadow table → old consistent state, no undo/redo needed.', 't tx')
    return f.render('Shadow paging: updated pages are written to <b>new</b> locations; the shadow table still points to the old pages.')


# ------------------------------------------------------------------ security
def cia():
    f = Fig(760, 300, 'CIA triad')
    pts = [(380, 40), (150, 250), (610, 250)]
    f.raw(f'<polygon points="{" ".join(f"{x},{y}" for x, y in pts)}" class="bx bx-acc op50"/>')
    f.box(300, 15, 160, 50, 'CONFIDENTIALITY', 'bx-pur', tcls='t tb')
    f.box(40, 225, 220, 50, 'INTEGRITY', 'bx-good', tcls='t tb')
    f.box(500, 225, 220, 50, 'AVAILABILITY', 'bx-warn', tcls='t tb')
    f.text(380, 160, 'Database', 't tb')
    f.text(380, 180, 'security goals', 't ts')
    f.text(560, 40, 'only authorised users can SEE data', 't ts', anchor='start')
    f.text(560, 58, '(e.g. salaries, medical records)', 't tx', anchor='start')
    f.text(150, 292, 'data changed only by authorised, correct operations', 't tx')
    f.text(610, 292, 'data accessible to authorised users when needed', 't tx')
    return f.render('The three goals of database security: Confidentiality, Integrity, Availability.')


def sec_layers():
    f = Fig(860, 170, 'layers of database security')
    steps = [('User / application', 'bx-mut'), ('Authentication\n(who are you?)', 'bx-acc'),
             ('Authorization /\naccess control', 'bx-pur'), ('Views, roles,\nrow-level security', 'bx-warn'),
             ('Encryption\n(at rest / in transit)', 'bx-good'), ('DATA', 'bx-bad')]
    for k, (s, c) in enumerate(steps):
        x = 10 + k * 142
        f.box(x, 40, 124, 60, s, c, tcls='t ts')
        if k:
            f.arrow(x - 16, 70, x - 2, 70, 'mut')
    f.box(150, 125, 700, 32, 'AUDITING (audit trail of who did what, when) watches every layer', 'bx-plain', tcls='t ts')
    f.text(430, 20, 'Defence in depth — a request must pass every layer to reach the data', 't tb')
    return f.render('Database security is layered (“defence in depth”).')


def authgraph():
    nodes = [('DBA', 70, 140, 'DBA'), ('U1', 250, 60, 'U1'), ('U2', 250, 220, 'U2'), ('U3', 440, 60, 'U3'),
             ('U4', 440, 220, 'U4'), ('U5', 620, 140, 'U5')]
    edges = [dict(u='DBA', v='U1', label='grant opt.'), dict(u='DBA', v='U2', label='grant opt.'),
             dict(u='U1', v='U3', label='grant opt.', cls='bad'), dict(u='U3', v='U5', label='', cls='bad'),
             dict(u='U2', v='U4', label=''), dict(u='U1', v='U4', label='', cls='bad', bend=0)]
    g = digraph(nodes, edges, node_cls={'DBA': 'n-acc'})
    return g.replace('</figure>', '<figcaption>Authorization (grant) graph for one privilege. If the DBA revokes from U1 '
                     '<b>CASCADE</b>, the red grants made through U1 disappear: U3 and U5 lose the privilege. '
                     'U4 keeps it, because U4 still has a path from the DBA through U2.</figcaption></figure>')


def blp():
    f = Fig(820, 300, 'Bell-LaPadula')
    lv = [('TOP SECRET (TS)', 'bx-bad'), ('SECRET (S)', 'bx-warn'), ('CONFIDENTIAL (C)', 'bx-acc'), ('UNCLASSIFIED (U)', 'bx-good')]
    for k, (s, c) in enumerate(lv):
        f.box(300, 20 + k * 68, 220, 50, s, c, tcls='t tb')
    f.box(40, 105, 160, 54, 'Subject\nclearance = SECRET', 'bx-pur', tcls='t ts')
    f.arrow(202, 125, 298, 50, 'bad', dash=True)
    f.text(225, 70, 'read ✖', 't tb tbad')
    f.arrow(202, 145, 298, 180, 'good')
    f.text(232, 178, 'read ✔', 't tb tgood')
    f.arrow(522, 40, 600, 40, 'good')
    f.arrow(522, 248, 600, 248, 'bad', dash=True)
    f.text(610, 40, 'write ✔ (write up allowed)', 't ts tgood', anchor='start')
    f.text(610, 248, 'write ✖ (no write down)', 't ts tbad', anchor='start')
    f.text(610, 120, 'S subject writing:', 't tb', anchor='start')
    f.text(610, 140, 'may write to S or TS objects,', 't ts', anchor='start')
    f.text(610, 158, 'never to C or U objects', 't ts', anchor='start')
    f.text(610, 176, '(prevents leaking secrets down)', 't tx', anchor='start')
    return f.render('Mandatory Access Control (Bell–LaPadula): <b>No read up</b> (simple security property) and '
                    '<b>No write down</b> (★-property).')


def mgl():
    nodes = [('DB', 330, 40, 'Database'), ('A1', 170, 130, 'Area A1'), ('A2', 490, 130, 'Area A2'),
             ('F1', 90, 220, 'File Fa'), ('F2', 250, 220, 'File Fb'), ('F3', 490, 220, 'File Fc'),
             ('r1', 40, 310, 'ra1'), ('r2', 140, 310, 'ra2'), ('r3', 250, 310, 'rb1'), ('r4', 440, 310, 'rc1'), ('r5', 540, 310, 'rc2')]
    edges = [dict(u='DB', v='A1'), dict(u='DB', v='A2'), dict(u='A1', v='F1'), dict(u='A1', v='F2'), dict(u='A2', v='F3'),
             dict(u='F1', v='r1'), dict(u='F1', v='r2'), dict(u='F2', v='r3'), dict(u='F3', v='r4'), dict(u='F3', v='r5')]
    for e in edges:
        e['label'] = ''
    g = digraph(nodes, edges, shape='box', nw=86, nh=34, node_cls={'DB': 'n-acc'})
    return g.replace('</figure>', '<figcaption>Granularity hierarchy. Locking a node implicitly locks all its descendants.</figcaption></figure>')
