"""Tiny SVG helpers. All colours come from CSS classes so light/dark themes work."""
import math, html

_uid = [0]


def uid():
    _uid[0] += 1
    return f'm{_uid[0]}'


def esc(s):
    return html.escape(str(s), quote=True)


def markers(mid):
    out = ['<defs>']
    for c in ('ink', 'bad', 'acc', 'good', 'mut'):
        out.append(f'<marker id="{mid}-{c}" viewBox="0 0 10 10" refX="9.5" refY="5" markerWidth="7" markerHeight="7" '
                   f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" class="ah ah-{c}"/></marker>')
    out.append('</defs>')
    return ''.join(out)


def circle_layout(T, cx=None, cy=None):
    n = len(T)
    if n == 1:
        return [(T[0], 160, 70, T[0])]
    if n == 2:
        return [(T[0], 70, 70, T[0]), (T[1], 250, 70, T[1])]
    if n == 3:
        return [(T[0], 160, 45, T[0]), (T[1], 60, 180, T[1]), (T[2], 260, 180, T[2])]
    if n == 4:
        return [(T[0], 70, 60, T[0]), (T[1], 260, 60, T[1]), (T[2], 260, 220, T[2]), (T[3], 70, 220, T[3])]
    R = 150
    cx = cx or 200
    cy = cy or 190
    res = []
    for i, t in enumerate(T):
        a = -math.pi / 2 + 2 * math.pi * i / n
        res.append((t, cx + R * math.cos(a), cy + R * math.sin(a), t))
    return res


def _trim(px, py, qx, qy, shape, r, w, h):
    """point on boundary of node centred at (px,py) in direction of (qx,qy)"""
    dx, dy = qx - px, qy - py
    L = math.hypot(dx, dy) or 1
    if shape == 'circle':
        return px + dx / L * r, py + dy / L * r
    hw, hh = w / 2 + 2, h / 2 + 2
    s = min(hw / abs(dx) if dx else 1e9, hh / abs(dy) if dy else 1e9)
    return px + dx * s, py + dy * s


def digraph(nodes, edges, caption='', r=24, shape='circle', nw=110, nh=40, big=False, pad=30,
            width=None, height=None, node_cls=None):
    """nodes: [(id,x,y,label)] ; edges: [dict(u,v,label,cls,bend,lpos)]"""
    mid = uid()
    pos = {n[0]: (n[1], n[2]) for n in nodes}
    lab = {n[0]: n[3] for n in nodes}
    node_cls = node_cls or {}
    xs = [p[0] for p in pos.values()]
    ys = [p[1] for p in pos.values()]
    ext = r if shape == 'circle' else max(nw, nh) / 2
    minx, maxx = min(xs) - ext - pad, max(xs) + ext + pad
    miny, maxy = min(ys) - ext - pad, max(ys) + ext + pad
    W = width or (maxx - minx)
    H = height or (maxy - miny)
    pairs = {(e['u'], e['v']) for e in edges}
    out = [f'<svg class="fig-svg graph" viewBox="{minx:.0f} {miny:.0f} {W:.0f} {H:.0f}" '
           f'style="max-width:{W * (1.35 if not big else 1.25):.0f}px" role="img" aria-label="{esc(caption or "graph")}">',
           markers(mid)]
    labels = []
    for e in edges:
        u, v = e['u'], e['v']
        (x1, y1), (x2, y2) = pos[u], pos[v]
        cls = e.get('cls', '') or 'ink'
        ccls = {'cyc': 'bad', 'bad': 'bad', 'acc': 'acc', 'good': 'good', 'mut': 'mut'}.get(cls, 'ink')
        bend = e.get('bend')
        if bend is None:
            bend = 28 if (v, u) in pairs else 0
        dash = ' dashed' if e.get('dash') else ''
        if bend == 0:
            sx, sy = _trim(x1, y1, x2, y2, shape, r, nw, nh)
            ex, ey = _trim(x2, y2, x1, y1, shape, r + 1, nw, nh)
            out.append(f'<line x1="{sx:.1f}" y1="{sy:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" class="edge e-{ccls}{dash}" '
                       f'marker-end="url(#{mid}-{ccls})"/>')
            lx, ly = (sx + ex) / 2, (sy + ey) / 2
            dx, dy = ex - sx, ey - sy
            L = math.hypot(dx, dy) or 1
            lx += -dy / L * 11
            ly += dx / L * 11
        else:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            dx, dy = x2 - x1, y2 - y1
            L = math.hypot(dx, dy) or 1
            px, py = -dy / L, dx / L
            cx, cy = mx + px * bend * 2, my + py * bend * 2
            sx, sy = _trim(x1, y1, cx, cy, shape, r, nw, nh)
            ex, ey = _trim(x2, y2, cx, cy, shape, r + 1, nw, nh)
            out.append(f'<path d="M{sx:.1f},{sy:.1f} Q{cx:.1f},{cy:.1f} {ex:.1f},{ey:.1f}" class="edge e-{ccls}{dash}" '
                       f'marker-end="url(#{mid}-{ccls})"/>')
            lx = 0.25 * sx + 0.5 * cx + 0.25 * ex + px * 10
            ly = 0.25 * sy + 0.5 * cy + 0.25 * ey + py * 10
        if e.get('lpos'):
            lx, ly = e['lpos']
        if e.get('label'):
            labels.append(f'<text x="{lx:.1f}" y="{ly:.1f}" class="elabel e-{ccls}-t" text-anchor="middle" '
                          f'dominant-baseline="middle">{esc(e["label"])}</text>')
    for (nid, x, y, l) in nodes:
        nc = node_cls.get(nid, '')
        if shape == 'circle':
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" class="node {nc}"/>')
        else:
            out.append(f'<rect x="{x - nw / 2:.1f}" y="{y - nh / 2:.1f}" width="{nw}" height="{nh}" rx="8" class="node {nc}"/>')
        parts = str(l).split('\\n')
        for k, p in enumerate(parts):
            dy = (k - (len(parts) - 1) / 2) * 15
            out.append(f'<text x="{x:.1f}" y="{y + dy:.1f}" class="nlabel" text-anchor="middle" dominant-baseline="central">{esc(p)}</text>')
    out.extend(labels)
    out.append('</svg>')
    fig = ''.join(out)
    cap = f'<figcaption>{caption}</figcaption>' if caption else ''
    return f'<figure class="fig">{fig}{cap}</figure>'
