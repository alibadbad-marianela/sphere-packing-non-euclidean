import os
import pdfplumber,sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # folder that contains code/ and out/
with pdfplumber.open(os.path.join(ROOT, 'out', 'Research_Paper.pdf')) as pdf:
    for i,p in enumerate(pdf.pages):
        if i<5: continue
        ws=[w for w in p.extract_words() if w['top']>72]
        low=max(w['bottom'] for w in ws)
        if p.images: low=max(low,max(im['bottom'] for im in p.images))
        lines=(p.extract_text() or '').split('\n')
        fr=round((720-low)/72,2)
        print(i+1, fr, '*' if fr>1.5 else ' ', '|', lines[1][:55] if len(lines)>1 else '', '|', lines[-1][:40])
