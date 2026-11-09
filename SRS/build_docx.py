import re
from docx import Document
from docx.shared import Pt, Cm, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

REG='Paperlogy 4 Regular'; MED='Paperlogy 5 Medium'; SEMI='Paperlogy 6 SemiBold'; BOLD='Paperlogy 7 Bold'; XB='Paperlogy 8 ExtraBold'
INK=RGBColor(0x1f,0x23,0x28); QUIET=RGBColor(0x5f,0x66,0x6e); ACC=RGBColor(0x1d,0x5f,0xc4)

def setfont(run_or_style, name):
    el = run_or_style.element if hasattr(run_or_style,'element') else run_or_style
    rpr = el.get_or_add_rPr() if hasattr(el,'get_or_add_rPr') else el.rPr
    rf = rpr.find(qn('w:rFonts'))
    if rf is None:
        rf = OxmlElement('w:rFonts'); rpr.insert(0, rf)
    for a in ('ascii','hAnsi','eastAsia','cs'):
        rf.set(qn('w:'+a), name)
    for a in ('asciiTheme','hAnsiTheme','eastAsiaTheme','cstheme'):
        k=qn('w:'+a)
        if k in rf.attrib: del rf.attrib[k]

doc = Document()
sec = doc.sections[0]
sec.page_width=Cm(21); sec.page_height=Cm(29.7)
for s in ('left_margin','right_margin'): setattr(sec,s,Cm(2.2))
sec.top_margin=Cm(2.2); sec.bottom_margin=Cm(2.2)
CONTENT_W = 21-4.4

def style(name, font, size, color=INK, before=0, after=0, keep=False, line=None):
    st = doc.styles[name]
    st.font.size=Pt(size); st.font.bold=False; st.font.italic=False; st.font.color.rgb=color
    setfont(st.element.get_or_add_rPr().getparent() if False else st, font) if False else None
    rpr = st.element.get_or_add_rPr()
    rf = rpr.find(qn('w:rFonts'))
    if rf is None:
        rf = OxmlElement('w:rFonts'); rpr.insert(0, rf)
    for a in ('ascii','hAnsi','eastAsia','cs'): rf.set(qn('w:'+a), font)
    for a in ('asciiTheme','hAnsiTheme','eastAsiaTheme','cstheme'):
        k=qn('w:'+a)
        if k in rf.attrib: del rf.attrib[k]
    pf = st.paragraph_format
    pf.space_before=Pt(before); pf.space_after=Pt(after); pf.keep_with_next=keep
    if line: pf.line_spacing=line
    return st

style('Normal', REG, 10, INK, 0, 6, False, 1.45)
style('Title', XB, 22, INK, 0, 4, False, 1.2)
style('Heading 1', XB, 20, INK, 0, 6, True)
style('Heading 2', BOLD, 15, INK, 22, 8, True, 1.25)
style('Heading 3', SEMI, 12, INK, 14, 5, True, 1.25)
style('Heading 4', SEMI, 12, INK, 16, 5, True, 1.25)
style('Heading 5', SEMI, 10.5, ACC, 10, 4, True, 1.25)
style('List Bullet', REG, 10, INK, 0, 3, False, 1.45)
style('List Number', REG, 10, INK, 0, 3, False, 1.45)
for n in ('Title',):
    pPr = doc.styles[n].element.get_or_add_pPr()
    b = pPr.find(qn('w:pBdr'))
    if b is not None: pPr.remove(b)
# H2 bottom rule
pPr = doc.styles['Heading 2'].element.get_or_add_pPr()
bd = OxmlElement('w:pBdr'); bt = OxmlElement('w:bottom')
for k,v in (('val','single'),('sz','6'),('space','4'),('color','C9CED4')): bt.set(qn('w:'+k),v)
bd.append(bt); pPr.append(bd)

def unesc(t):
    t=t.replace('&#91;','[').replace('&#93;',']')
    t=re.sub(r'\\([\\`*_{}\[\]()#+\-.!~|<>])', r'\1', t)
    return t.replace('✕','×')

TOK = re.compile(r'(\*\*.+?\*\*|`.+?`|\[[^\]]+\]\(https?://[^)]+\))')
def add_inline(p, text, base=REG, size=None, color=None):
    for part in TOK.split(text):
        if not part: continue
        if part.startswith('**') and part.endswith('**'):
            r=p.add_run(unesc(part[2:-2])); setfont(r,SEMI)
        elif re.match(r'^\[[^\]]+\]\(https?://[^)]+\)$',part):
            mm=re.match(r'^\[([^\]]+)\]\((https?://[^)]+)\)$',part)
            rid=p.part.relate_to(mm.group(2),'http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink',is_external=True)
            h=OxmlElement('w:hyperlink'); h.set(qn('r:id'),rid)
            r=p.add_run(unesc(mm.group(1))); setfont(r,base); r.font.color.rgb=ACC; r.font.underline=True
            if size: r.font.size=Pt(size)
            h.append(r._r); p._p.append(h); continue
        elif part.startswith('`') and part.endswith('`'):
            r=p.add_run(unesc(part[1:-1])); setfont(r,MED)
            rpr=r._r.get_or_add_rPr(); sh=OxmlElement('w:shd')
            sh.set(qn('w:val'),'clear'); sh.set(qn('w:color'),'auto'); sh.set(qn('w:fill'),'EEF0F2'); rpr.append(sh)
        else:
            r=p.add_run(unesc(part)); setfont(r,base)
        if size: r.font.size=Pt(size)
        if color is not None: r.font.color.rgb=color

def shade(cell, fill):
    tcPr=cell._tc.get_or_add_tcPr(); sh=OxmlElement('w:shd')
    sh.set(qn('w:val'),'clear'); sh.set(qn('w:color'),'auto'); sh.set(qn('w:fill'),fill); tcPr.append(sh)

def cell_margins(tbl, top=60, bottom=60, left=90, right=90):
    tblPr=tbl._tbl.tblPr; m=OxmlElement('w:tblCellMar')
    for k,v in (('top',top),('left',left),('bottom',bottom),('right',right)):
        e=OxmlElement('w:'+k); e.set(qn('w:w'),str(v)); e.set(qn('w:type'),'dxa'); m.append(e)
    tblPr.append(m)

def borders(tbl):
    tblPr=tbl._tbl.tblPr; b=OxmlElement('w:tblBorders')
    for k in ('top','left','bottom','right','insideH','insideV'):
        e=OxmlElement('w:'+k); e.set(qn('w:val'),'single'); e.set(qn('w:sz'),'4'); e.set(qn('w:space'),'0'); e.set(qn('w:color'),'C9CED4'); b.append(e)
    tblPr.append(b)

def widths_for(header, rows):
    n=len(header)
    if header[0]=='ID' and n==3: w=[2.0,12.9,1.7]
    elif header[0]=='ID' and n==4: w=[2.0,11.2,1.7,1.7]
    elif header[0]=='ID' and n==5: w=[1.9,1.6,9.6,1.7,1.8]
    else:
        import math
        L=[max([len(header[i])]+[len(r[i]) for r in rows if i<len(r)]) for i in range(n)]
        avg=[sum(len(r[i]) for r in rows if i<len(r))/max(1,len(rows)) for i in range(n)]
        raw=[max(1.6,math.sqrt(max(a,4))) for a in avg]
        s=sum(raw); w=[x/s*CONTENT_W for x in raw]
    k=CONTENT_W/sum(w); return [x*k for x in w]

def add_table(lines):
    def cells(l): 
        l=l.strip()
        parts=re.split(r'(?<!\\)\|', l)
        return [c.strip() for c in parts[1:-1]]
    header=cells(lines[0]); rows=[cells(l) for l in lines[2:]]
    w=widths_for(header, rows)
    t=doc.add_table(rows=1+len(rows), cols=len(header))
    t.alignment=WD_TABLE_ALIGNMENT.CENTER; t.autofit=False
    tblPr=t._tbl.tblPr
    lay=OxmlElement('w:tblLayout'); lay.set(qn('w:type'),'fixed'); tblPr.append(lay)
    borders(t); cell_margins(t)
    # grid
    grid=t._tbl.tblGrid
    for i,gc in enumerate(grid.findall(qn('w:gridCol'))): gc.set(qn('w:w'), str(int(w[i]/2.54*1440)))
    for ri,row in enumerate([header]+rows):
        tr=t.rows[ri]
        trPr=tr._tr.get_or_add_trPr(); cs=OxmlElement('w:cantSplit'); trPr.append(cs)
        if ri==0:
            th=OxmlElement('w:tblHeader'); trPr.append(th)
        for ci in range(len(header)):
            c=tr.cells[ci]; c.width=Cm(w[ci])
            txt=row[ci] if ci<len(row) else ''
            p=c.paragraphs[0]; p.paragraph_format.space_after=Pt(0); p.paragraph_format.line_spacing=1.3
            if ri==0:
                shade(c,'EEF0F2'); add_inline(p,txt,base=SEMI,size=9)
            else:
                add_inline(p,txt,base=REG,size=9)
                if txt in ('○','×','✕','—') or re.match(r'^(○|×|✕|—)',txt): pass
            if ri>0 and header[ci] in ('우선순위','상태','순서','기본 표시','번호'): p.alignment=WD_ALIGN_PARAGRAPH.CENTER
            if ri==0 and header[ci] in ('우선순위','상태','순서'): p.alignment=WD_ALIGN_PARAGRAPH.CENTER
            if ri>0 and header[0]=='기능' and '일반 회원' in header and ci>0 : p.alignment=WD_ALIGN_PARAGRAPH.CENTER
            if ri==0 and header[0]=='기능' and '일반 회원' in header and ci>0 : p.alignment=WD_ALIGN_PARAGRAPH.CENTER
            if ri>0 and header[0]=='ID' and ci==0: 
                for r in p.runs: setfont(r,MED); r.font.size=Pt(8.5); r.font.color.rgb=QUIET
            if ri>0 and txt=='추천': 
                for r in p.runs: r.font.color.rgb=QUIET
    sp=doc.add_paragraph(); sp.paragraph_format.space_after=Pt(4); sp.paragraph_format.line_spacing=0.6
    return t

def add_image(path, caption):
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.keep_with_next=True; p.paragraph_format.space_before=Pt(4)
    p.add_run().add_picture(path, width=Cm(CONTENT_W))
    c=doc.add_paragraph(); c.alignment=WD_ALIGN_PARAGRAPH.CENTER
    add_inline(c, caption, base=REG, size=8.5, color=QUIET)

md=open('srs.md',encoding='utf-8').read().split('\n')
imgs=[('nav.png',None),('er.png',None)]; img_i=0
i=0
first=True
while i<len(md):
    l=md[i]
    if not l.strip(): i+=1; continue
    if l.startswith('# '):
        doc.add_paragraph(unesc(l[2:]), style='Title'); i+=1; continue
    m=re.match(r'^(#{2,5}) (.*)',l)
    if m:
        lvl=len(m.group(1)); h=doc.add_paragraph(style=f'Heading {lvl}'); add_inline(h,m.group(2),base={2:BOLD,3:SEMI,4:SEMI,5:SEMI}[lvl]); 
        if lvl==2 and not first_h2_done if 'first_h2_done' in globals() else False: pass
        globals()['first_h2_done']=True
        i+=1; continue
    if l.startswith('|'):
        blk=[]
        while i<len(md) and md[i].startswith('|'): blk.append(md[i]); i+=1
        add_table(blk); continue
    if l.startswith('&#91;embedded content:'):
        cap=re.sub(r'^&#91;embedded content: ?','',l).rstrip('\\]').rstrip(']')
        path=imgs[img_i][0]; img_i+=1
        add_image(path,'그림. '+unesc(cap)); i+=1; continue
    if re.match(r'^- ',l):
        while i<len(md) and re.match(r'^- ',md[i]):
            p=doc.add_paragraph(style='List Bullet'); add_inline(p,md[i][2:]); i+=1
        continue
    if re.match(r'^\d+\. ',l):
        while i<len(md) and re.match(r'^\d+\. ',md[i]):
            p=doc.add_paragraph(style='List Number'); add_inline(p,re.sub(r'^\d+\. ','',md[i])); i+=1
        continue
    if re.match(r'^Nov 9, 2026',l) or re.match(r'^[A-Z][a-z]{2} \d+, 20\d\d',l):
        p=doc.add_paragraph(); add_inline(p,'2026-11-09 · Kim',base=REG,size=9.5,color=QUIET); p.paragraph_format.space_after=Pt(14); i+=1; continue
    # bold lead-in line or plain paragraph
    p=doc.add_paragraph()
    if re.match(r'^\*\*.+\*\*$',l):
        p.paragraph_format.keep_with_next=True; p.paragraph_format.space_before=Pt(8); p.paragraph_format.space_after=Pt(3)
    add_inline(p,l); i+=1

# footer page number
f=sec.footer.paragraphs[0]; f.alignment=WD_ALIGN_PARAGRAPH.CENTER
r=f.add_run('플리 시연 SRS · '); setfont(r,REG); r.font.size=Pt(8.5); r.font.color.rgb=QUIET
r2=f.add_run(); setfont(r2,REG); r2.font.size=Pt(8.5); r2.font.color.rgb=QUIET
for t,txt in (('begin',None),(None,'PAGE'),('end',None)):
    if t:
        fc=OxmlElement('w:fldChar'); fc.set(qn('w:fldCharType'),t); r2._r.append(fc)
    else:
        it=OxmlElement('w:instrText'); it.set(qn('xml:space'),'preserve'); it.text=txt; r2._r.append(it)
doc.core_properties.title='플리 시연 — 소프트웨어 요구사항 명세서(SRS)'
doc.core_properties.author='Kim'
doc.save('플리시연_SRS.docx')
print('saved')
