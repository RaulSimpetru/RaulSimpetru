"""Turn poster.html into ../assets/poster.svg, the image the profile README shows.

Needs Google Chrome and pdftocairo (poppler: `brew install poppler`). Run from anywhere:

    python3 poster/build.py

Chrome prints poster.html to a one-page PDF at its own size, pdftocairo turns that into a plain vector SVG
(text as outlines, pictures embedded), and the dashed ring around the drawn hand is added on top as an
animated SVG circle that stops for people who turn off animations.
"""
import json, os, re, subprocess, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "assets", "poster.svg")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
INK = "#2A2522"

# Reports the page size and where the drawing sits, once the fonts have loaded.
MEASURE = ("<script>document.fonts.ready.then(()=>{const b=document.body.getBoundingClientRect(),"
           "d=document.getElementById('drawing').getBoundingClientRect();document.title='M'+JSON.stringify("
           "{w:Math.ceil(b.width),h:Math.ceil(b.height),d:{x:d.left,y:d.top,w:d.width,h:d.height}})+'M'})</script>")


def chrome(*args):
    cmd = [CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--virtual-time-budget=8000", *args]
    return subprocess.run(cmd, capture_output=True, text=True).stdout


html = open(os.path.join(HERE, "poster.html"), encoding="utf-8").read()
with tempfile.TemporaryDirectory() as tmp:
    # The temporary pages live next to poster.html so img/ resolves.
    m, p, pdf = (os.path.join(HERE, "_measure.html"), os.path.join(HERE, "_print.html"), os.path.join(tmp, "poster.pdf"))
    try:
        open(m, "w", encoding="utf-8").write(html.replace("</body>", MEASURE + "</body>"))
        info = json.loads(re.search(r"<title>M(.*?)M</title>", chrome("--window-size=900,2400", "--dump-dom", f"file://{m}")).group(1))
        page = f"@page{{size:{info['w']}px {info['h']}px;margin:0}}"
        open(p, "w", encoding="utf-8").write(html.replace("</style>", page + "</style>"))
        chrome(f"--print-to-pdf={pdf}", f"file://{p}")
        subprocess.run(["pdftocairo", "-svg", pdf, OUT], check=True)
    finally:
        for f in (m, p):
            if os.path.exists(f):
                os.remove(f)

# The ring: (310, 400) with radius 26 in the drawing's own 1134 x 638 frame, plus a short line to the close-up.
d = info["d"]
X = lambda v: d["x"] + v * d["w"] / 1134
Y = lambda v: d["y"] + v * d["h"] / 638
ring = (f'<circle class="march" cx="{X(310):.1f}" cy="{Y(400):.1f}" r="{26 * d["w"] / 1134:.1f}" fill="none" stroke="{INK}" '
        f'stroke-width="2" stroke-dasharray="5 4"/><path d="M{X(286):.1f} {Y(390):.1f} L{X(245):.1f} {Y(373):.1f}" stroke="{INK}" stroke-width="1.6"/>')
style = ("<style>@keyframes march{to{stroke-dashoffset:-18}}.march{animation:march 1.4s linear infinite}"
         "@media (prefers-reduced-motion:reduce){.march{animation:none}}</style>")
svg = open(OUT, encoding="utf-8").read()
# pdftocairo works in points (0.75 of a CSS pixel): give the SVG its pixel size and draw the ring in pixels.
svg = re.sub(r'width="[\d.]+(pt)?" height="[\d.]+(pt)?"', f'width="{info["w"]}" height="{info["h"]}"', svg, count=1)
svg = svg.replace("</svg>", f'{style}<g transform="scale(0.75)">{ring}</g></svg>')
open(OUT, "w", encoding="utf-8").write(svg)
print(f"assets/poster.svg: {info['w']} x {info['h']} px, {os.path.getsize(OUT) // 1024} KB")
