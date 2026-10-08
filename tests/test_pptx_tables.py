import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from contextlib import redirect_stdout
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    'pptx_tables', ROOT / 'slide-templates/cmc-weekly/scripts/pptx-native-tables.py')
pptx = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pptx)

NS = ('xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
      'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
      'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"')


def shape(shape_id, name, x, y, w, h):
    e = pptx.EMU
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{shape_id}" name="{name}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{x * e}" y="{y * e}"/><a:ext cx="{w * e}" cy="{h * e}"/></a:xfrm></p:spPr></p:sp>')


SLIDE = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><p:sld {NS}><p:cSld><p:spTree>'
         '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/>'
         + shape(2, 'title', 40, 20, 600, 60)       # outside the table: must survive
         + shape(3, 'cell-a', 100, 200, 100, 40)    # two per-cell shapes the export drew
         + shape(4, 'cell-b', 200, 200, 100, 40)
         + '</p:spTree></p:cSld></p:sld>')

LINE = {'w': 2, 'color': {'hex': '000000', 'a': 1}, 'style': 'solid'}


def cell(r, c, text, rs=1, cs=1, bg=None):
    return {'r': r, 'c': c, 'rs': rs, 'cs': cs, 'bg': bg, 'pad': [2, 6, 2, 6], 'va': 'middle', 'nw': False,
            'bd': {'t': LINE, 'r': LINE, 'b': LINE, 'l': LINE},
            'paras': [{'align': 'center', 'lineH': 24,
                       'runs': [{'t': text, 'size': 20, 'bold': False, 'u': False, 'mono': False,
                                 'color': {'hex': '000000', 'a': 1}}]}]}


TABLE = {'x': 100, 'y': 200, 'w': 200, 'h': 80, 'colW': [100, 100], 'rowH': [40, 40],
         'cells': [cell(0, 0, '항목 & 값', cs=2, bg={'hex': 'F2F2F2', 'a': 1}),
                   cell(1, 0, 'A'), cell(1, 1, 'B')]}


class PptxNativeTablesTests(unittest.TestCase):
    def convert(self, tables):
        holder = tempfile.TemporaryDirectory()
        self.addCleanup(holder.cleanup)
        temp = Path(holder.name)
        src, spec_path, dst = temp / 'in.pptx', temp / 'tables.json', temp / 'out.pptx'
        with zipfile.ZipFile(src, 'w') as z:
            z.writestr('ppt/slides/slide1.xml', SLIDE)
            z.writestr('ppt/slides/slide2.xml', SLIDE)
        spec_path.write_text(json.dumps(tables, ensure_ascii=False))
        with redirect_stdout(io.StringIO()):
            pptx.main(str(src), str(spec_path), str(dst))
        with zipfile.ZipFile(dst) as z:
            return {name: z.read(name).decode() for name in z.namelist()}

    def test_cell_shapes_become_one_native_table(self):
        out = self.convert({'1': [TABLE]})
        slide = out['ppt/slides/slide1.xml']
        self.assertEqual(slide.count('<a:tbl>'), 1)
        self.assertNotIn('cell-a', slide)
        self.assertNotIn('cell-b', slide)
        self.assertIn('name="title"', slide)
        self.assertIn('gridSpan="2"', slide)
        self.assertIn('hMerge="1"', slide)
        self.assertIn('항목 &amp; 값', slide)
        self.assertIn('val="F2F2F2"', slide)
        self.assertEqual(slide.count('<a:gridCol w="%d"' % (100 * pptx.EMU)), 2)
        self.assertIn('<a:lnL w="%d"' % (2 * pptx.EMU), slide)  # 2px canvas line = 1pt

    def test_pages_without_tables_are_untouched(self):
        out = self.convert({'1': [TABLE]})
        self.assertEqual(out['ppt/slides/slide2.xml'], SLIDE)


if __name__ == '__main__':
    unittest.main()
