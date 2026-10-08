// Paste into the browser console on the open-slide viewer (/s/<slide-id>), after the deck
// has finished loading. Walks every page with the arrow keys (stopping when ArrowRight no longer
// advances), records each <table>'s geometry, merges, fills, borders, padding and text runs, then
// downloads tables.json for scripts/pptx-native-tables.py.
(async () => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const mainCanvas = () => {
    const c = [...document.querySelectorAll('div')].filter((e) => e.offsetWidth === 1920 && e.offsetHeight === 1080);
    c.sort((a, b) => b.getBoundingClientRect().width - a.getBoundingClientRect().width);
    return c[0];
  };
  const rgba = (s) => {
    const m = s.match(/rgba?\(([^)]+)\)/);
    if (!m) return null;
    const p = m[1].split(',').map((x) => parseFloat(x));
    const a = p.length > 3 ? p[3] : 1;
    if (a === 0) return null;
    const hex = p.slice(0, 3).map((v) => Math.round(v).toString(16).padStart(2, '0')).join('').toUpperCase();
    return { hex, a: Math.round(a * 1000) / 1000 };
  };
  const underlined = (el, stop) => {
    for (let e = el; e && e !== stop.parentElement; e = e.parentElement) {
      if (getComputedStyle(e).textDecorationLine.includes('underline')) return true;
    }
    return false;
  };
  const isBlock = (el) => ['block', 'flex', 'grid', 'list-item', 'table'].includes(getComputedStyle(el).display);
  const lh = (el) => {
    const cs = getComputedStyle(el);
    const v = parseFloat(cs.lineHeight);
    return isNaN(v) ? parseFloat(cs.fontSize) * 1.2 : v;
  };

  const paragraphs = (cell) => {
    const out = [];
    let cur = null;
    const start = (blockEl, extra = {}) => {
      cur = { runs: [], align: getComputedStyle(blockEl).textAlign, lineH: lh(blockEl), ...extra };
      out.push(cur);
    };
    const addRun = (text, el) => {
      const cs = getComputedStyle(el);
      const r = {
        t: text,
        size: parseFloat(cs.fontSize),
        bold: parseInt(cs.fontWeight, 10) >= 600,
        u: underlined(el, cell),
        color: rgba(cs.color),
        mono: /consolas|monospace/i.test(cs.fontFamily),
      };
      const last = cur.runs[cur.runs.length - 1];
      if (last && !last.br && last.size === r.size && last.bold === r.bold && last.u === r.u && last.mono === r.mono &&
          JSON.stringify(last.color) === JSON.stringify(r.color)) last.t += text;
      else cur.runs.push(r);
    };
    const walk = (node, blockEl) => {
      for (const ch of node.childNodes) {
        if (ch.nodeType === 3) {
          const t = ch.textContent.replace(/\s+/g, ' ');
          if (!t.trim() && (!cur || cur.runs.length === 0)) continue;
          if (!cur) start(blockEl);
          addRun(t, ch.parentElement);
        } else if (ch.nodeType === 1) {
          if (ch.tagName === 'BR') {
            if (cur) cur.runs.push({ br: true });
            continue;
          }
          if (isBlock(ch)) {
            const cs = getComputedStyle(ch);
            const kids = ch.children;
            if (cs.display === 'flex' && kids.length === 2 && kids[0].tagName === 'SPAN' && kids[0].textContent.trim().length <= 2) {
              start(ch, {
                bullet: { char: kids[0].textContent.trim(), color: rgba(getComputedStyle(kids[0]).color), gap: parseFloat(cs.columnGap) || 8,
                  markW: kids[0].getBoundingClientRect().width / scale },
                indent: parseFloat(cs.paddingLeft) || 0,
              });
              walk(kids[1], ch);
              cur = null;
              continue;
            }
            cur = null;
            walk(ch, ch);
            cur = null;
          } else walk(ch, blockEl);
        }
      }
    };
    walk(cell, cell);
    for (const p of out) {
      const rs = p.runs;
      while (rs.length && rs[0].br) rs.shift();
      while (rs.length && rs[rs.length - 1].br) rs.pop();
      if (rs.length) rs[0].t = rs[0].t.replace(/^\s+/, '');
      if (rs.length) rs[rs.length - 1].t = rs[rs.length - 1].t.replace(/\s+$/, '');
      for (let i = 0; i < rs.length; i++) {
        if (rs[i].br && rs[i + 1] && !rs[i + 1].br) rs[i + 1].t = rs[i + 1].t.replace(/^\s+/, '');
        if (rs[i].br && rs[i - 1] && !rs[i - 1].br) rs[i - 1].t = rs[i - 1].t.replace(/\s+$/, '');
      }
    }
    return out.filter((p) => p.runs.some((r) => !r.br && r.t.length));
  };

  let scale = 1;
  const edges = (vals) => {
    const s = [...vals].sort((a, b) => a - b);
    const out = [];
    for (const v of s) if (!out.length || v - out[out.length - 1] > 1.5) out.push(v);
    return out;
  };
  const nearest = (arr, v) => {
    let bi = 0;
    for (let i = 1; i < arr.length; i++) if (Math.abs(arr[i] - v) < Math.abs(arr[bi] - v)) bi = i;
    return bi;
  };
  const border = (cs, side) => {
    const w = parseFloat(cs[`border${side}Width`]);
    const st = cs[`border${side}Style`];
    if (!w || st === 'none' || st === 'hidden') return null;
    return { w, color: rgba(cs[`border${side}Color`]), style: st };
  };

  const extract = () => {
    const canvas = mainCanvas();
    const cr = canvas.getBoundingClientRect();
    scale = cr.width / 1920;
    const rel = (r) => ({ x: (r.left - cr.left) / scale, y: (r.top - cr.top) / scale, w: r.width / scale, h: r.height / scale });
    const tables = [];
    for (const tbl of canvas.querySelectorAll('table')) {
      const tr = rel(tbl.getBoundingClientRect());
      const cells = [...tbl.querySelectorAll('td,th')].map((c) => ({ el: c, r: rel(c.getBoundingClientRect()) }));
      const xs = edges(cells.flatMap((c) => [c.r.x, c.r.x + c.r.w]));
      const ys = edges(cells.flatMap((c) => [c.r.y, c.r.y + c.r.h]));
      const out = cells.map(({ el, r }) => {
        const cs = getComputedStyle(el);
        const c0 = nearest(xs, r.x), c1 = nearest(xs, r.x + r.w);
        const r0 = nearest(ys, r.y), r1 = nearest(ys, r.y + r.h);
        let bg = rgba(cs.backgroundColor);
        if (!bg) bg = rgba(getComputedStyle(el.parentElement).backgroundColor);
        return {
          r: r0, c: c0, rs: Math.max(1, r1 - r0), cs: Math.max(1, c1 - c0),
          bg,
          bd: { t: border(cs, 'Top'), r: border(cs, 'Right'), b: border(cs, 'Bottom'), l: border(cs, 'Left') },
          pad: ['Top', 'Right', 'Bottom', 'Left'].map((s) => parseFloat(cs[`padding${s}`]) || 0),
          va: cs.verticalAlign,
          nw: cs.whiteSpace === 'nowrap',
          paras: paragraphs(el),
        };
      });
      tables.push({
        x: xs[0], y: ys[0], w: xs[xs.length - 1] - xs[0], h: ys[ys.length - 1] - ys[0],
        bbox: tr,
        colW: xs.slice(1).map((v, i) => v - xs[i]),
        rowH: ys.slice(1).map((v, i) => v - ys[i]),
        cells: out,
      });
    }
    return tables;
  };

  const pageNo = () => parseInt(new URLSearchParams(location.search).get('p') || '1', 10);
  const result = {};
  let guard = 0;
  while (pageNo() > 1 && guard++ < 100) {
    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowLeft', bubbles: true }));
    await sleep(250);
  }
  for (let i = 0; i < 500; i++) {
    await sleep(800);
    const p = pageNo();
    if (p in result) break; // ArrowRight did not advance: last page reached
    result[p] = extract();
    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowRight', bubbles: true }));
  }
  window.__osTables = result;
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([JSON.stringify(result)], { type: 'application/json' }));
  a.download = 'tables.json';
  a.click();
  return Object.fromEntries(Object.entries(result).map(([k, v]) => [k, v.length]));
})();
