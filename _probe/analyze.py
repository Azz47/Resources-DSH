# -*- coding: utf-8 -*-
"""课件/文档语料批量分析器 —— 从任意 .pptx / .pdf 中程序化提取「内容排版、页面布局、
配图、叙述逻辑」四类可量化特征，输出 JSONL + 汇总，供沉淀课件设计规范。

用法:
    python analyze.py <out-dir> <file-or-dir> [<file-or-dir> ...]

pptx 走 python-pptx；(pdf 走 LibreOffice kit 渲染后统计页面像素分布，另行处理)
"""
import json
import os
import sys
from collections import Counter

from pptx import Presentation
from pptx.util import Emu

EMU_PER_IN = 914400


def walk_inputs(paths):
    out = []
    for p in paths:
        if os.path.isdir(p):
            for root, _dirs, files in os.walk(p):
                for f in files:
                    if f.lower().endswith(('.pptx', '.ppt')):
                        out.append(os.path.join(root, f))
        elif p.lower().endswith(('.pptx', '.ppt')):
            out.append(p)
    return out


def shape_text(shape):
    try:
        if shape.has_text_frame:
            return shape.text_frame.text or ''
    except Exception:
        pass
    return ''


def analyze_pptx(path):
    prs = Presentation(path)
    sw = prs.slide_width / EMU_PER_IN
    sh = prs.slide_height / EMU_PER_IN
    rec = {
        'path': path,
        'name': os.path.basename(path),
        'slide_w_in': round(sw, 3),
        'slide_h_in': round(sh, 3),
        'aspect': round(sw / sh, 4) if sh else None,
        'slides': 0,
        'slides_detail': [],
        'font_sizes': Counter(),
        'fonts': Counter(),
        'colors': Counter(),
        'shape_types': Counter(),
    }

    for idx, slide in enumerate(prs.slides, 1):
        texts, pics, tables, charts = [], 0, 0, 0
        for shape in slide.shapes:
            rec['shape_types'][str(shape.shape_type)] += 1
            t = shape_text(shape)
            if t.strip():
                texts.append(t.strip())
            try:
                if shape.shape_type == 13 or shape.__class__.__name__ == 'Picture':
                    pics += 1
            except Exception:
                pass
            if getattr(shape, 'has_table', False) and shape.has_table:
                tables += 1
            if getattr(shape, 'has_chart', False) and shape.has_chart:
                charts += 1
            try:
                if shape.has_text_frame:
                    for para in shape.text_frame.paragraphs:
                        for run in para.runs:
                            if run.font.size:
                                rec['font_sizes'][round(run.font.size.pt, 1)] += 1
                            if run.font.name:
                                rec['fonts'][run.font.name] += 1
                            try:
                                if run.font.color and run.font.color.rgb:
                                    rec['colors'][str(run.font.color.rgb)] += 1
                            except Exception:
                                pass
            except Exception:
                pass

        joined = '\n'.join(texts)
        # 标题取最上面那个有文字的框（近似）
        top_text = ''
        best_top = None
        for shape in slide.shapes:
            t = shape_text(shape)
            if not t.strip():
                continue
            try:
                top = shape.top
            except Exception:
                top = None
            if top is not None and (best_top is None or top < best_top):
                best_top, top_text = top, t.strip().split('\n')[0]
        rec['slides_detail'].append({
            'n': idx,
            'title_like': top_text[:60],
            'text_blocks': len(texts),
            'chars': len(joined),
            'pics': pics,
            'tables': tables,
            'charts': charts,
        })
        rec['slides'] = idx

    s = rec['slides'] or 1
    d = rec['slides_detail']
    rec['avg_chars_per_slide'] = round(sum(x['chars'] for x in d) / s, 1)
    rec['avg_blocks_per_slide'] = round(sum(x['text_blocks'] for x in d) / s, 1)
    rec['pics_total'] = sum(x['pics'] for x in d)
    rec['slides_with_image'] = sum(1 for x in d if x['pics'] > 0)
    rec['image_ratio'] = round(rec['slides_with_image'] / s, 3)
    rec['tables_total'] = sum(x['tables'] for x in d)
    rec['charts_total'] = sum(x['charts'] for x in d)
    rec['font_sizes'] = dict(rec['font_sizes'].most_common(12))
    rec['fonts'] = dict(rec['fonts'].most_common(8))
    rec['colors'] = dict(rec['colors'].most_common(10))
    rec['shape_types'] = {k: v for k, v in rec['shape_types'].most_common(10)}
    return rec


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(2)
    out_dir, inputs = sys.argv[1], sys.argv[2:]
    os.makedirs(out_dir, exist_ok=True)
    files = walk_inputs(inputs)
    print(f'found {len(files)} pptx file(s)')
    ok, failed = 0, []
    with open(os.path.join(out_dir, 'corpus.jsonl'), 'w', encoding='utf-8') as fh:
        for f in files:
            try:
                rec = analyze_pptx(f)
                fh.write(json.dumps(rec, ensure_ascii=False) + '\n')
                ok += 1
                print(f"  OK  {rec['slides']:>3}p  {rec['avg_chars_per_slide']:>6}字/页  img{rec['image_ratio']:.0%}  {rec['name'][:60]}")
            except Exception as e:
                failed.append((f, repr(e)[:120]))
                print(f'  FAIL {os.path.basename(f)}: {e!r}'[:160])
    print(f'\ndone: {ok} ok, {len(failed)} failed -> {out_dir}/corpus.jsonl')
    for f, e in failed:
        print('   ', e)


if __name__ == '__main__':
    main()
