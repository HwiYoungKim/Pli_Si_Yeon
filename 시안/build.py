import base64, io, sys
from fontTools import subset
from fontTools.ttLib import TTFont
src = open('proto_src.html', encoding='utf-8').read()
chars = set(src) | {chr(c) for c in range(0x20, 0x7f)} | set('·‹›←→↑↓…※–—~×')
text = ''.join(sorted(chars))
FD = '/home/claude/fontsrc/Paperlogy/'
faces = []
for w, f in [(300,'3Light'),(400,'4Regular'),(600,'6SemiBold'),(800,'8ExtraBold')]:
    font = TTFont(FD+f'Paperlogy-{f}.ttf')
    opts = subset.Options(); opts.flavor='woff2'; opts.layout_features=['*']; opts.notdef_outline=True
    s = subset.Subsetter(opts); s.populate(text=text); s.subset(font)
    buf = io.BytesIO(); font.flavor='woff2'; font.save(buf)
    b = base64.b64encode(buf.getvalue()).decode()
    print(w, len(buf.getvalue())//1024, 'KB')
    faces.append("@font-face{font-family:'Paperlogy';font-weight:%d;font-style:normal;font-display:swap;src:url(data:font/woff2;base64,%s) format('woff2')}" % (w, b))
out = src.replace('/*FONTS*/', '\n'.join(faces))
open('/home/claude/build/proto/플리시연_시안.html','w',encoding='utf-8').write(out)
print('html', len(out)//1024, 'KB')
