import asyncio
from playwright.async_api import async_playwright
W,H=1380,1100
nodes={}
def box(k,x,y,w,h,num,title,lines,dash=False,tone='#e9eef7'):
    nodes[k]=(x,y,w,h)
    s=f'<rect x={x} y={y} width={w} height={h} rx=16 fill="{tone}" stroke="#c4cddb" stroke-width=2 {"stroke-dasharray=\"8 6\"" if dash else ""}/>'
    s+=f'<text x={x+22} y={y+38} font-size=17 font-weight=600 fill="#6b7790">{num}</text>'
    s+=f'<text x={x+22} y={y+68} font-size=26 font-weight=600 fill="#16233b">{title}</text>'
    for i,l in enumerate(lines): s+=f'<text x={x+22} y={y+102+i*27} font-size=18.5 fill="#4a5568">{l}</text>'
    return s
out=[]
bw,bh=400,160
out.append(box('1',40,100,bw,bh,'①','로그인·회원가입',['ID·비밀번호 입력, 로그인·회원가입','비밀번호 초기화, 필수·선택 권한 받기']))
out.append(box('2',480,100,bw,bh,'②','메인화면',['공지(맨 위)·날짜·현재 시간·오늘 일정','시간·날씨에 따라 바뀌는 배경']))
out.append(box('3',920,100,bw,bh,'③','캘린더',['월 캘린더, 이번 주 확대 강조, 눈동자 버튼','일정 추가, 일정 종류별 색 표시']))
bw2,bh2=400,160
out.append(box('4',40,360,bw2,bh2,'④','소모임',['가입한 소모임 목록, 순서 설정','다른 소모임 둘러보기 (가입 전에는 숨김)']))
out.append(box('5',480,360,bw2,bh2,'⑤','설정',['권한, 소모임 설정(알림·일정 표시)','일정 표시 순서, 개인 설정']))
out.append(box('6',920,360,bw2,bh2,'⑥','임원 설정',['사용자 정보·개인정보 조회, 계정 삭제','동아리 공지 쓰기·수정·삭제 (임원 전용)'],dash=True))
cy=[570,742,914]
out.append(box('40',100,cy[0],bw2+240,152,'④-n-0','미가입 소모임',['소개글 확인, 가입 신청 (신청 전 한 번 더 확인)']))
out.append(box('41',100,cy[1],bw2+240,152,'④-n-1','가입자',['글·공지·일정 확인, 글쓰기·일정 등록','내가 쓴 글 수정·삭제']))
out.append(box('42',100,cy[2],bw2+240,152,'④-n-2','소모임장',['가입자 기능 전부, 소모임 설정, 공지·대표 공지','모든 게시글 수정·삭제 (작성자에게 알림)'],tone='#e2ebfa'))
def arrow(x1,y1,x2,y2): return f'<path d="M{x1} {y1} L{x2} {y2}" stroke="#8d99ae" stroke-width=3 fill=none marker-end=url(#a) />'
a=[]
a.append(arrow(440,180,478,180)); a.append(arrow(880,180,918,180))
# 3 -> 4,5,6 bus
a.append('<path d="M1120 260 V310 H240 V358" stroke="#8d99ae" stroke-width=3 fill=none marker-end=url(#a) />')
a.append(arrow(680,310,680,358)); a.append(arrow(1120,310,1120,358))
# 4 -> children elbow
a.append('<path d="M60 510 V'+str(cy[2]+76)+'" stroke="#8d99ae" stroke-width=3 fill=none />')
for y in cy: a.append(arrow(60,y+76,98,y+76))
a.append('<path d="M60 510 V'+str(cy[0]+76)+'" stroke="#8d99ae" stroke-width=3 fill=none />')
svg=f'''<svg id=s xmlns="http://www.w3.org/2000/svg" width={W} height={H} viewBox="0 0 {W} {H}"><rect width={W} height={H} fill="#fff"/>
<defs><marker id=a viewBox="0 0 10 10" refX=8 refY=5 markerWidth=8 markerHeight=8 orient=auto-start-reverse><path d="M0 0L10 5L0 10z" fill="#8d99ae"/></marker></defs>
<text x=40 y=56 font-size=26 font-weight=600 fill="#16233b">화면 계층 구조</text>
<text x=40 y=84 font-size=16 fill="#6b7790">화살표는 들어가는 방향이다. 번호는 화면을 만든 순서이고, 층은 화살표로만 정한다. 점선은 현시연 임원에게만 보인다.</text>
{"".join(a)}{"".join(out)}
<text x=820 y=660 font-size=19 fill="#6b7790">n은 소모임을 만든 순서이다</text>
<text x=820 y=692 font-size=19 fill="#6b7790">-0 미가입 · -1 가입자 · -2 소모임장</text>
</svg>'''
html='<!doctype html><meta charset=utf-8><style>@font-face{font-family:P;src:url(file:///home/claude/fontsrc/Paperlogy/Paperlogy-4Regular.ttf);font-weight:400}@font-face{font-family:P;src:url(file:///home/claude/fontsrc/Paperlogy/Paperlogy-6SemiBold.ttf);font-weight:600}body{margin:0}svg text{font-family:P}</style>'+svg
open('hier.html','w').write(html)
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await b.new_page(viewport={'width':W,'height':H},device_scale_factor=2)
        await pg.goto('file:///home/claude/build/hier.html'); await pg.wait_for_timeout(400)
        await pg.locator('#s').screenshot(path='/home/claude/build/hier.png'); await b.close()
asyncio.run(main())
