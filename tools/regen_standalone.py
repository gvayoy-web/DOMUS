"""Regenera visualizaciones/sistema-domus.html desde el fragmento v2."""
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
frag = (ROOT / "visualizaciones" / "sistema-domus-fragment.html").read_text(encoding="utf-8")
theme = """<style>
:root{color-scheme:light dark;--background:light-dark(#fff,#181818);--foreground:light-dark(#1a1c1f,#fff);--card:light-dark(#f2f2f2,#2c2c2c);--border:light-dark(#ccc,#555);--muted-foreground:light-dark(#555,#bbb);--viz-series-1:#0e9db5;--viz-series-2:#e0574b;--viz-series-4:#8a63d2;--destructive:#c81e1e;--font-size-base:16px}
body{font-family:system-ui,sans-serif;background:var(--background);color:var(--foreground);margin:0;padding:16px}
h1{font-size:1.4rem;margin:.2em 0}.text-muted{color:var(--muted-foreground)}.text-small{font-size:.8rem}
.viz-badge{display:inline-block;padding:6px 10px;border:1px solid var(--border);border-radius:6px;font-size:.8rem}
.card{border:1px solid var(--border);border-radius:8px;padding:10px;background:var(--card)}
.viz-stat-value{font-weight:700}.form-label{font-size:.8rem;font-weight:600}
.form-select{font-size:.9rem;padding:6px;margin:4px 0 8px;max-width:100%}
.table-responsive{overflow:auto}table{border-collapse:collapse;width:100%;font-size:.9rem}
th,td{border:1px solid var(--border);padding:6px 8px;text-align:left}
</style>"""
doc = (
    "<!doctype html><html lang='es'><head><meta charset='utf-8'>"
    "<meta name='viewport' content='width=device-width,initial-scale=1'>"
    + theme
    + "</head><body>"
    + frag
    + "</body></html>"
)
head = """<!doctype html>
<html lang="en" data-visualize-standalone>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="referrer" content="no-referrer">
<title>Sistema Domus v2</title>
<style>:root{color-scheme:light dark;background:light-dark(rgb(255 255 255), rgb(24 24 24))}html,body{margin:0}body{box-sizing:border-box;padding:1rem;background:inherit}iframe{display:block;width:100%;height:calc(100vh - 2rem);margin:0 auto;border:0}</style>
</head>
<body>
<iframe sandbox="allow-scripts" referrerpolicy="no-referrer" title="Sistema Domus v2" srcdoc="
"""
tail = """">
</iframe>
</body>
</html>
"""
out = ROOT / "visualizaciones" / "sistema-domus.html"
out.write_text(head + html.escape(doc, quote=True) + tail, encoding="utf-8")
print("standalone OK", out.stat().st_size)
