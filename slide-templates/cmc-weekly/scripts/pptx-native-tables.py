#!/usr/bin/env python3
"""Replace open-slide's per-cell shapes with native PowerPoint tables.

open-slide's PPTX export (@open-slide/core 2.x) has no table node: every <td>
becomes a Rectangle plus a text box. This post-processor rebuilds each HTML
<table> as a real <a:tbl> graphic frame.

Inputs
  export.pptx   the file produced by open-slide's "Export as PPTX"
  tables.json   table geometry/content captured from the running viewer with
                scripts/extract-tables.js ({page: [table, ...]})

Usage
  python3 scripts/pptx-native-tables.py export.pptx tables.json out.pptx

Only the Python standard library is used.
"""
import json
import re
import sys
import zipfile
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape

EMU = 6350  # 1 canvas px (1920-wide canvas on a 13.333in slide)
NS = {
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
}
A = '{%s}' % NS['a']
P = '{%s}' % NS['p']
FONT = 'Malgun Gothic'
MONO = 'Consolas'
SYMBOL_FONT = 'Segoe UI Symbol'


def emu(px):
    return int(round(px * EMU))


def color_xml(c):
    if not c:
        return '<a:noFill/>'
    alpha = '' if c['a'] >= 0.999 else '<a:alpha val="%d"/>' % round(c['a'] * 100000)
    return '<a:solidFill><a:srgbClr val="%s">%s</a:srgbClr></a:solidFill>' % (c['hex'], alpha)


def line_xml(tag, b):
    if not b or not b.get('color'):
        return '<a:%s w="0"><a:noFill/></a:%s>' % (tag, tag)
    dash = {'dashed': 'dash', 'dotted': 'sysDot'}.get(b['style'], 'solid')
    return ('<a:%s w="%d" cap="flat" cmpd="sng" algn="ctr">%s<a:prstDash val="%s"/>'
            '<a:round/></a:%s>') % (tag, emu(b['w']), color_xml(b['color']), dash, tag)


def run_xml(r):
    if r.get('br'):
        return '<a:br><a:rPr lang="ko-KR" sz="%d" dirty="0"/></a:br>' % sz(r.get('size', 20))
    latin = MONO if r.get('mono') else FONT
    attrs = 'lang="ko-KR" altLang="en-US" sz="%d"' % sz(r['size'])
    if r.get('bold'):
        attrs += ' b="1"'
    if r.get('u'):
        attrs += ' u="sng"'
    return ('<a:r><a:rPr %s dirty="0">%s<a:latin typeface="%s"/><a:ea typeface="%s"/>'
            '<a:cs typeface="%s"/></a:rPr><a:t>%s</a:t></a:r>') % (
        attrs, color_xml(r.get('color')), latin, FONT, latin, escape(r['t']))


def sz(px):
    return max(100, int(round(px * 50)))  # px → 1/100 pt (1pt = 2px)


ALIGN = {'start': 'l', 'left': 'l', 'center': 'ctr', 'right': 'r', 'end': 'r', 'justify': 'just'}


def para_xml(p):
    algn = ALIGN.get(p.get('align'), 'l')
    spc = '<a:lnSpc><a:spcPts val="%d"/></a:lnSpc><a:spcBef><a:spcPts val="0"/></a:spcBef>' \
          '<a:spcAft><a:spcPts val="0"/></a:spcAft>' % max(100, int(round(p['lineH'] * 50)))
    b = p.get('bullet')
    if b:
        hang = b['markW'] + b['gap']
        font = 'Arial' if b['char'] in '•·-' else SYMBOL_FONT
        clr = '<a:buClr><a:srgbClr val="%s"/></a:buClr>' % b['color']['hex'] if b.get('color') else ''
        ppr = ('<a:pPr marL="%d" indent="%d" algn="%s">%s%s<a:buSzPct val="100000"/>'
               '<a:buFont typeface="%s"/><a:buChar char="%s"/></a:pPr>') % (
            emu(p.get('indent', 0) + hang), -emu(hang), algn, spc, clr, font, escape(b['char']))
    else:
        ppr = '<a:pPr marL="0" indent="0" algn="%s">%s<a:buNone/></a:pPr>' % (algn, spc)
    first = next((r for r in p['runs'] if not r.get('br')), {'size': 20})
    return '<a:p>%s%s<a:endParaRPr lang="ko-KR" sz="%d" dirty="0"/></a:p>' % (
        ppr, ''.join(run_xml(r) for r in p['runs']), sz(first['size']))


def empty_para(size_px=14):
    return '<a:p><a:pPr><a:lnSpc><a:spcPts val="%d"/></a:lnSpc></a:pPr>' \
           '<a:endParaRPr lang="ko-KR" sz="%d" dirty="0"/></a:p>' % (sz(size_px * 1.2), sz(size_px))


def table_xml(t, shape_id, name):
    nrows, ncols = len(t['rowH']), len(t['colW'])
    origin = {}
    covered = {}
    for c in t['cells']:
        origin[(c['r'], c['c'])] = c
        for dr in range(c['rs']):
            for dc in range(c['cs']):
                if dr or dc:
                    covered[(c['r'] + dr, c['c'] + dc)] = (dr > 0, dc > 0)

    def owner(r, cc):
        for c in t['cells']:
            if c['r'] <= r < c['r'] + c['rs'] and c['c'] <= cc < c['c'] + c['cs']:
                return c
        return None

    def side(c, s):
        """Own border, else the neighbour's facing border (HTML border-collapse)."""
        if c['bd'].get(s):
            return c['bd'][s]
        r0, c0 = c['r'], c['c']
        nr, nc = {'t': (r0 - 1, c0), 'b': (r0 + c['rs'], c0), 'l': (r0, c0 - 1), 'r': (r0, c0 + c['cs'])}[s]
        n = owner(nr, nc)
        return n['bd'].get({'t': 'b', 'b': 't', 'l': 'r', 'r': 'l'}[s]) if n else None

    cols = [emu(w) for w in t['colW']]
    rows = [emu(h) for h in t['rowH']]
    out = ['<a:tbl><a:tblPr firstRow="0" bandRow="0"/><a:tblGrid>']
    out += ['<a:gridCol w="%d"/>' % w for w in cols]
    out.append('</a:tblGrid>')
    for ri in range(nrows):
        out.append('<a:tr h="%d">' % rows[ri])
        for ci in range(ncols):
            c = origin.get((ri, ci))
            if c is None:
                v, h = covered.get((ri, ci), (False, False))
                attrs = (' vMerge="1"' if v else '') + (' hMerge="1"' if h else '')
                out.append('<a:tc%s><a:txBody><a:bodyPr/><a:lstStyle/>%s</a:txBody><a:tcPr/></a:tc>' % (attrs, empty_para()))
                continue
            attrs = (' gridSpan="%d"' % c['cs'] if c['cs'] > 1 else '') + (' rowSpan="%d"' % c['rs'] if c['rs'] > 1 else '')
            body = ''.join(para_xml(p) for p in c['paras']) or empty_para()
            pt, pr, pb, pl = c['pad']
            if c.get('nw'):  # no-wrap cells: PowerPoint glyphs run wider than Chrome's, give them room
                pl, pr = min(pl, 4), min(pr, 4)
            anchor = {'top': 't', 'bottom': 'b'}.get(c['va'], 'ctr')
            tcpr = '<a:tcPr marL="%d" marR="%d" marT="%d" marB="%d" anchor="%s">%s%s%s%s%s</a:tcPr>' % (
                emu(pl), emu(pr), emu(pt), emu(pb), anchor,
                line_xml('lnL', side(c, 'l')), line_xml('lnR', side(c, 'r')),
                line_xml('lnT', side(c, 't')), line_xml('lnB', side(c, 'b')),
                color_xml(c['bg']))
            out.append('<a:tc%s><a:txBody><a:bodyPr/><a:lstStyle/>%s</a:txBody>%s</a:tc>' % (attrs, body, tcpr))
        out.append('</a:tr>')
    out.append('</a:tbl>')
    return ('<p:graphicFrame xmlns:a="{a}" xmlns:p="{p}"><p:nvGraphicFramePr><p:cNvPr id="{id}" name="{name}"/>'
            '<p:cNvGraphicFramePr><a:graphicFrameLocks noGrp="1"/></p:cNvGraphicFramePr><p:nvPr/></p:nvGraphicFramePr>'
            '<p:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{cx}" cy="{cy}"/></p:xfrm>'
            '<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/table">{tbl}'
            '</a:graphicData></a:graphic></p:graphicFrame>').format(
        a=NS['a'], p=NS['p'], id=shape_id, name=escape(name), x=emu(t['x']), y=emu(t['y']),
        cx=sum(cols), cy=sum(rows), tbl=''.join(out))


def bbox(el):
    xfrm = el.find('.//' + A + 'xfrm')
    if xfrm is None:
        return None
    off, ext = xfrm.find(A + 'off'), xfrm.find(A + 'ext')
    if off is None or ext is None:
        return None
    return (int(off.get('x')) / EMU, int(off.get('y')) / EMU, int(ext.get('cx')) / EMU, int(ext.get('cy')) / EMU)


def inside(b, t, tol=6):
    x, y, w, h = b
    cx, cy = x + w / 2, y + h / 2
    return (t['x'] - tol <= cx <= t['x'] + t['w'] + tol and t['y'] - tol <= cy <= t['y'] + t['h'] + tol
            and w <= t['w'] + 2 * tol and h <= t['h'] + 2 * tol)


def convert_slide(xml, tables):
    for prefix, uri in re.findall(r'xmlns:(\w+)="([^"]+)"', xml.decode('utf-8')):
        ET.register_namespace(prefix, uri)
    root = ET.fromstring(xml)
    tree = root.find('.//' + P + 'spTree')
    ids = [int(e.get('id')) for e in root.iter(P + 'cNvPr') if e.get('id', '').isdigit()]
    next_id = max(ids + [1]) + 1
    stats = []
    for n, t in enumerate(tables, 1):
        children = list(tree)
        hit = [i for i, el in enumerate(children)
               if el.tag in (P + 'sp', P + 'pic', P + 'cxnSp') and (b := bbox(el)) and inside(b, t)]
        if not hit:
            stats.append((n, 0))
            continue
        for i in reversed(hit):
            tree.remove(children[i])
        frame = ET.fromstring(table_xml(t, next_id, 'Table %d' % n))
        tree.insert(hit[0], frame)
        next_id += 1
        stats.append((n, len(hit)))
    xml_out = b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n' + ET.tostring(root, encoding='utf-8')
    return xml_out, stats


def main(src, spec, dst):
    pages = json.load(open(spec, encoding='utf-8'))
    zin = zipfile.ZipFile(src)
    with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            m = re.match(r'ppt/slides/slide(\d+)\.xml$', item.filename)
            if m and pages.get(m.group(1)):
                data, stats = convert_slide(data, pages[m.group(1)])
                print('slide %s: %s' % (m.group(1), ', '.join('T%d←%d shapes' % s for s in stats)))
            zout.writestr(item, data)


if __name__ == '__main__':
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])
