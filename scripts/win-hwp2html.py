#!/usr/bin/env python3
"""old-com 저장소의 WIN.HWP(한글 3.00) 를 원본의 쪽·줄 배치 그대로
19951114-windows-era/index.html 로 옮긴다. 문서에 들어 있는 그림(BMP)은 PNG 로 뽑는다.

사용법: scripts/win-hwp2html.py [old-com 경로, 기본 ../old-com]

문단마다 저장된 줄 정보(줄 시작 글자 위치, 쪽 안의 y, 그림을 피해 밀린 x)와
그림·표 상자의 쪽 안 위치를 써서 글자와 그림을 원래 자리에 놓는다.
길이 단위는 hunit(1/1800 인치). 글자 코드표와 문서 구조 읽기는 old-com 의 hwp2html.py 를 빌려 쓴다.
"""
import html
import io
import struct
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OLD_COM = Path(sys.argv[1] if len(sys.argv) > 1 else ROOT.parent / "old-com").resolve()
SRC = OLD_COM / "c-drive/HWP21/WIN.HWP"
OUT = ROOT / "19951114-windows-era"

sys.path.insert(0, str(OLD_COM))
import hwp2html as H  # noqa: E402

F = H.FMT30


def load():
    d = SRC.read_bytes()
    di = d[30:158]
    paper = struct.unpack_from("<HH6H", di, 6)  # 길이, 너비, 위, 아래, 왼쪽, 오른쪽, 머리말, 꼬리말
    info_len = di[126] | di[127] << 8
    body = zlib.decompressobj(-15).decompress(d[30 + 128 + 1008 + info_len:])
    return paper, body


def extract_pictures(body, end):
    """본문 뒤 추가 정보 블록: (종류 u32, 길이 u32, 파일 이름 32바이트, 그림 자료)."""
    from PIL import Image
    p = end
    while p + 8 <= len(body):
        kind, size = struct.unpack_from("<II", body, p)
        if kind == 0 and size == 0:
            break
        if kind == 1:
            name = body[p + 8:p + 40].split(b"\0")[0].decode("ascii")
            data = body[p + 40:p + 8 + size]
            n = int(name[3:8])
            Image.open(io.BytesIO(data)).save(OUT / f"win-{n}.png", optimize=True)
            print(f"  {name} → win-{n}.png")
        p += 8 + size


def read_paralist(r):
    paras = []
    while True:
        reuse, nch, nline, has_cs = r.u8(), r.u16(), r.u16(), r.u8()
        r.p += 1 + 4 + 1 + F.cshape
        if nch == 0:
            return paras
        if not reuse:
            r.p += F.pshape
        lines = []
        for _ in range(nline):
            st, adj, h, y, x1, x2, w = struct.unpack("<HhHHHHH", r.take(14))
            lines.append(dict(st=st, y=y, x=x1, w=w))
        if has_cs:
            for _ in range(nch):
                if r.u8() != 1:
                    r.p += F.cshape
        paras.append(dict(lines=lines, items=read_chars(r, nch)))


def read_chars(r, nch):
    """[(글자 단위 위치, 항목)] 항목: str | ('pic', dict) | ('box', dict)"""
    items, i = [], 0
    while i < nch:
        c = r.u16()
        if c == 13:
            break
        if c > 31:
            s, _ = H.char_hwp(c)
            items.append((i, s))
            i += 1
        elif c == 9:
            r.p += 6
            items.append((i, "\t"))
            i += 4
        elif c == 10:
            r.p += 6
            info = r.take(84)
            i += 4
            cells = []
            for _ in range(struct.unpack_from("<H", info, 80)[0]):
                ci = r.take(27)
                cells.append(dict(zip("xywh", struct.unpack_from("<4H", ci, 4))))
            for cell in cells:
                cell["paras"] = read_paralist(r)
            read_paralist(r)
            items.append((i - 4, ("box", dict(box(info), cells=cells))))
        elif c == 11:
            r.u32()
            r.p += 2
            i += 4
            base = r.p
            info = r.b[base:base + F.pic]
            name = info[83:83 + 256].split(b"\0")[0].decode("ascii")
            H.read_picture(r, F, 0)
            items.append((i - 4, ("pic", dict(box(info), name=name))))
        else:
            raise ValueError(f"이 문서에서 예상하지 못한 특수 문자 {c}")
    return items


def box(info):
    """그림·표 상자 공통 정보: 쪽 안 위치(62, 64), 바깥 여백(18~), 안 여백(34~), 크기(42, 44)."""
    x, y = struct.unpack_from("<HH", info, 62)
    w, h = struct.unpack_from("<HH", info, 42)
    margin, pad_left, pad_top = (struct.unpack_from("<H", info, o)[0] for o in (18, 34, 38))
    return dict(x=x, y=y, w=w, h=h, m=margin, px=pad_left, py=pad_top)


def esc_line(s):
    s = html.escape(s)
    # 연속된 공백과 줄 앞 공백을 살린다
    out, prev_space = [], True
    for ch in s:
        if ch == " ":
            out.append("&nbsp;" if prev_space else " ")
            prev_space = True
        else:
            out.append(ch)
            prev_space = False
    return "".join(out)


def line_texts(para):
    """문단을 원래 줄 단위로 나눈다. (줄 정보, 글, 그 줄의 상자들)"""
    lines = para["lines"]
    out = []
    for k, ln in enumerate(lines):
        end = lines[k + 1]["st"] if k + 1 < len(lines) else 1 << 30
        text, objs = "", []
        for pos, it in para["items"]:
            if ln["st"] <= pos < end:
                if isinstance(it, str):
                    text += "    " if it == "\t" else it
                else:
                    objs.append(it)
        out.append((ln, text, objs, k == len(lines) - 1))
    return out


def u(v):
    return f"calc({v} * var(--u))"


def render():
    paper, body = load()
    plen, pwid, top, bottom, left, right, head, foot = paper
    r = H.Reader(body)
    for _ in range(F.fonts):
        n = r.u16()
        r.p += 40 * n
    n = r.u16()
    r.p += (20 + F.cshape + F.pshape) * n
    paras = read_paralist(r)
    extract_pictures(body, r.p)

    pages = [[]]
    prev_y = -1
    pending = []  # 앞 쪽에서 자리가 모자라 다음 쪽 맨 위로 넘어간 그림

    objs_by_page = [[]]
    for para in paras:
        for ln, text, objs, last in line_texts(para):
            if ln["y"] < prev_y:
                pages.append([])
                objs_by_page.append([])
                objs_by_page[-1].extend(pending)
                pending = []
            prev_y = ln["y"]
            pages[-1].append((ln, text, last))
            for kind, o in objs:
                # 쪽 아래로 넘치는 그림은 한글이 다음 쪽 맨 위에 놓았다 (y 가 0 으로 저장됨)
                if kind == "pic" and o["y"] < ln["y"]:
                    pending.append((kind, o))
                else:
                    objs_by_page[-1].append((kind, o))

    body_top = top + head
    out = []
    for n, (lines, objs) in enumerate(zip(pages, objs_by_page), 1):
        out.append(f'<section class="page" aria-label="{n}쪽">')
        for ln, text, last in lines:
            if not text.strip():
                continue
            cls = "ln last" if last else "ln"
            out.append(
                f'<div class="{cls}" style="left:{u(left + ln["x"])};top:{u(body_top + ln["y"])};'
                f'width:{u(ln["w"] - ln["x"])}"><span>{esc_line(text)}</span></div>')
        for kind, o in objs:
            ix, iy = left + o["x"] + o["m"], body_top + o["y"] + o["m"]
            pos = f'left:{u(ix)};top:{u(iy)};width:{u(o["w"])};height:{u(o["h"])}'
            if kind == "pic":
                if o["name"].startswith("E$$"):
                    out.append(f'<img class="pic" src="win-{int(o["name"][3:8])}.png" alt="" style="{pos}">')
                else:
                    out.append(f'<div class="pic missing" style="{pos}" title="원본 파일이 남아 있지 않음">'
                               f'<span>{html.escape(o["name"])}</span></div>')
            else:
                out.append(f'<div class="box" style="{pos}">')
                for cell in o["cells"]:
                    for para in cell["paras"]:
                        for ln, text, objs2, last in line_texts(para):
                            if not text.strip():
                                continue
                            out.append(
                                f'<div class="ln{" last" if last else ""}" style="left:{u(o["px"] + ln["x"])};'
                                f'top:{u(o["py"] + ln["y"])};width:{u(cell["w"] - 2 * o["px"] - ln["x"])}"><span>{esc_line(text)}</span></div>')
                out.append("</div>")
        out.append("</section>")
    return pwid, plen, "\n".join(out)


PAGE = """<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>이제 윈도우 시대?</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Nanum+Myeongjo&display=swap">
<style>
  :root {{ --desk: #8a8f96; --ink: #000; --paper: #fff; --meta: #f1f1ee; --muted: #555; }}
  * {{ box-sizing: border-box; }}
  html {{ background: var(--desk); }}
  body {{ margin: 0; padding: 0 16px 48px; font-family: "Nanum Myeongjo", "Batang", "바탕", serif; color: var(--ink); }}
  header {{ max-width: 210mm; margin: 0 auto; padding: 20px 0 16px; color: #fff; font-size: 14px; line-height: 1.6; }}
  header h1 {{ font-size: 22px; margin: 0 0 4px; }}
  header p {{ margin: 0; }}
  header a {{ color: #fff; }}
  .page {{
    --u: calc(100cqw / {pwid});
    container-type: inline-size; position: relative; overflow: hidden;
    width: min(210mm, 100%); aspect-ratio: {pwid} / {plen};
    margin: 0 auto 16px; background: var(--paper); box-shadow: 2px 3px 8px rgba(0, 0, 0, .35);
  }}
  .ln {{
    position: absolute; height: calc(250 * var(--u));
    font-size: calc(250 * var(--u)); line-height: 1; white-space: nowrap;
    text-align: justify; text-align-last: justify;
  }}
  .ln.last {{ text-align-last: left; }}
  .pic {{ position: absolute; display: block; }}
  .missing {{ border: 1px dashed #999; display: flex; align-items: center; justify-content: center;
              font: calc(160 * var(--u)) monospace; color: #888; }}
  .box {{ position: absolute; border: 1px solid #000; }}
  @media print {{
    @page {{ size: A4; margin: 0; }}
    html {{ background: none; }}
    body {{ padding: 0; }}
    header {{ display: none; }}
    .page {{ width: 210mm; margin: 0; box-shadow: none; break-after: page; }}
  }}
</style>
</head>
<body>
<header>
  <h1>이제 윈도우 시대?</h1>
  <p>정상혁 · 1995년 11월, 학교 교지에 기고한 글</p>
  <p>아래아한글 3.0 문서(<code>WIN.HWP</code>)에 저장된 용지(A4)·여백·줄 나눔·그림 위치를 그대로 옮겼다.
     글은 고치지 않았다. 점선 상자는 문서에 연결만 되어 있던 그림 파일(<code>C:\\I\\DOWN\\DUMP0000.PCX</code>)이 남아 있지 않은 자리다.</p>
</header>
<main>
{pages}
</main>
<script>
  // 줄 나눔은 원본 그대로 두고, 웹 글꼴이 원래 글꼴보다 넓어 줄이 넘치면 자간만 좁힌다.
  function fit() {{
    for (const ln of document.querySelectorAll('.ln')) {{
      const span = ln.firstElementChild;
      span.style.letterSpacing = '';
      const over = span.getBoundingClientRect().width - ln.getBoundingClientRect().width;
      if (over > 0) span.style.letterSpacing = -(over / span.textContent.length) + 'px';
    }}
  }}
  document.fonts.ready.then(fit);
  addEventListener('load', fit);
  addEventListener('resize', fit);
</script>
</body>
</html>
"""


if __name__ == "__main__":
    pwid, plen, pages = render()
    (OUT / "index.html").write_text(PAGE.format(pwid=pwid, plen=plen, pages=pages))
    print(f"✓ {OUT / 'index.html'}")
