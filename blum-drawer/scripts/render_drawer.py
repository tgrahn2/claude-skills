#!/usr/bin/env python3
"""
Generate a self-contained HTML plan sheet for Blum drawer boxes:
  - interactive 3D box (three.js, explode slider, per-drawer selector, dim sprites)
  - dimensioned SVG shop drawings per drawer (FRONT elevation, SIDE section,
    EXPLODED parts layout) with every measurement spelled out in fractions
  - a cut-list table

Reads the SAME JSON config as drawer_calc.py. Matches the host project's
plans/ style (three.js 0.160 importmap, dark cards, red dimension lines).

Usage:
    python3 -I render_drawer.py config.json out.html
    python3 -I render_drawer.py config.json -        # HTML to stdout
"""
import json
import os
import sys
from fractions import Fraction

# -I drops the script's own dir from sys.path; re-add it so the sibling import
# works. This only trusts the skill's own directory, not the (possibly
# untrusted) directory the config file came from.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from drawer_calc import compute, to_frac, parse_len  # sibling module


# ---------- tiny SVG dimensioned-drawing helpers ----------
class SVG:
    def __init__(self, w, h, scale):
        self.w, self.h, self.scale = w, h, scale
        self.parts = []

    def rect(self, x, y, w, h, cls):
        self.parts.append(f'<rect class="{cls}" x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}"/>')

    def line(self, x1, y1, x2, y2, cls):
        self.parts.append(f'<line class="{cls}" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"/>')

    def text(self, x, y, s, cls, anchor="middle", rot=None):
        tr = f' transform="rotate({rot} {x:.1f},{y:.1f})"' if rot is not None else ""
        self.parts.append(f'<text class="{cls}" x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}"{tr}>{s}</text>')

    def hdim(self, x1, x2, y, label, below=False):
        """Horizontal dimension between x1,x2 drawn at height y."""
        o = 14 if below else -14
        self.line(x1, y, x1, y + (o if below else o), "ext")
        self.line(x2, y, x2, y + (o if below else o), "ext")
        yd = y + o
        self.line(x1, yd, x2, yd, "dim")
        self.text((x1 + x2) / 2, yd + (14 if below else -5), label, "dimt")

    def vdim(self, y1, y2, x, label, right=True):
        o = 14 if right else -14
        self.line(x, y1, x + o, y1, "ext")
        self.line(x, y2, x + o, y2, "ext")
        xd = x + o
        self.line(xd, y1, xd, y2, "dim")
        self.text(xd + (12 if right else -12), (y1 + y2) / 2, label,
                  "dimt", anchor="middle", rot=90)

    def render(self):
        style = ("<style>.dim{stroke:#c0392b;stroke-width:1}.dimt{fill:#c0392b;font-size:12px}"
                 ".ext{stroke:#c0392b;stroke-width:.5;stroke-dasharray:3 2}"
                 ".part{fill:#e9dcc0;stroke:#6b5a37;stroke-width:1.5}"
                 ".bot{fill:#d8c187;stroke:#6b5a37;stroke-width:1.3}"
                 ".groove{stroke:#2d6cdf;stroke-width:1;stroke-dasharray:4 2}"
                 ".lbl{fill:#333;font-size:12px}.note{fill:#2d6cdf;font-size:11px}</style>")
        body = "\n    ".join(self.parts)
        return (f'<svg viewBox="0 0 {self.w} {self.h}" '
                f'font-family="-apple-system,Segoe UI,sans-serif">{style}\n    {body}\n  </svg>')


F = lambda x, d=32: to_frac(x, d)


def front_elevation(d, t, denom):
    """Looking at the drawer front: exterior width x box height."""
    s = 16  # px/in
    W = d["exterior_width"]; H = d["box_height"]; iw = d["inside_width"]
    m = 70
    svg = SVG(int(W * s + 2 * m + 60), int(H * s + 2 * m + 20), s)
    x0, y0 = m, m
    svg.rect(x0, y0, W * s, H * s, "part")
    # inside-width ticks (where the sides' inner faces are)
    svg.line(x0 + t * s, y0, x0 + t * s, y0 + H * s, "groove")
    svg.line(x0 + (W - t) * s, y0, x0 + (W - t) * s, y0 + H * s, "groove")
    svg.text(x0 + W * s / 2, y0 + H * s / 2, "FRONT", "lbl")
    svg.hdim(x0, x0 + W * s, y0, f'exterior {F(W,denom)}')
    svg.hdim(x0 + t * s, x0 + (W - t) * s, y0 + H * s, f'inside {F(iw,denom)}', below=True)
    svg.vdim(y0, y0 + H * s, x0 + W * s, f'height {F(H,denom)}')
    return svg.render()


def side_section(d, t, bt, gd, denom):
    """Section through depth: slide length x box height, bottom in its groove."""
    s = 16
    D = d["slide_length"]; H = d["box_height"]
    m = 70
    svg = SVG(int(D * s + 2 * m + 60), int(H * s + 2 * m + 40), s)
    x0, y0 = m, m
    svg.rect(x0, y0, D * s, H * s, "part")
    svg.text(x0 + 6, y0 - 6, "FRONT", "lbl", anchor="start")
    svg.text(x0 + D * s - 6, y0 - 6, "BACK", "lbl", anchor="end")
    # bottom panel sitting in a groove ~ gd up from the bottom edge
    gy = y0 + H * s - int((gd + bt) * s) - 6
    svg.rect(x0, gy, D * s, bt * s, "bot")
    svg.text(x0 + D * s / 2, gy - 4, f'{F(bt,denom)} bottom in {F(gd,denom)}-deep groove', "note")
    svg.hdim(x0, x0 + D * s, y0, f'slide length (nominal) {F(D,denom)}')
    svg.vdim(y0, y0 + H * s, x0 + D * s, f'height {F(H,denom)}')
    svg.text(x0 + D * s / 2, y0 + H * s + 34,
             f'rear notch in BACK: {d["notch"]}" wide (use the jig)', "note")
    return svg.render()


def exploded_parts(d, t, bt, denom):
    """Flat 'cut these pieces' layout, each piece labeled with its cut size."""
    s = 11
    sideL = d["slide_length"]; fbL = d["parts"]["frontback"]["length"]; H = d["box_height"]
    bw = d["parts"]["bottom"]["width"]; bd = d["parts"]["bottom"]["depth"]
    cons = d["construction"]
    m, gap = 40, 26
    col = max(sideL, fbL, bw) * s
    rows = [H, H, bd]  # side, front/back, bottom heights in the layout
    total_h = (H + H + bd) * s + 3 * gap + 2 * m
    svg = SVG(int(col + 2 * m + 120), int(total_h), s)
    y = m

    def piece(y, w, h, label, cls="part"):
        svg.rect(m, y, w * s, h * s, cls)
        svg.text(m + w * s / 2, y + h * s / 2, label, "lbl")
        svg.hdim(m, m + w * s, y, F(w, denom))
        svg.vdim(y, y + h * s, m + w * s, F(h, denom))
        return y + h * s + gap

    y = piece(y, sideL, H, f'SIDE  x{d["parts"]["sides"]["qty"]}  ({t:g}")')
    fb_note = "full width (box joint)" if cons == "boxjoint" else "between sides"
    y = piece(y, fbL, H, f'FRONT/BACK  x{d["parts"]["frontback"]["qty"]}  {fb_note}  ({t:g}")')
    y = piece(y, bw, bd, f'BOTTOM  x{d["parts"]["bottom"]["qty"]}  ({bt:g}")', cls="bot")
    return svg.render()


# ---------- three.js block ----------
THREE_TEMPLATE = r"""
<script type="importmap">
{ "imports": {
  "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
  "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"
}}
</script>
<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const DRAWERS = __DRAWERS_JSON__;
const T = __T__, BT = __BT__, GD = __GD__;

const host = document.getElementById('viewer');
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x1b1d21);
const camera = new THREE.PerspectiveCamera(42, host.clientWidth/host.clientHeight, 0.5, 2000);
const DEFAULT_CAM = new THREE.Vector3(26, 22, 40);
camera.position.copy(DEFAULT_CAM);
const renderer = new THREE.WebGLRenderer({ antialias:true });
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.setSize(host.clientWidth, host.clientHeight);
host.appendChild(renderer.domElement);
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;

scene.add(new THREE.AmbientLight(0xffffff, 0.6));
const key = new THREE.DirectionalLight(0xffffff, 1.0); key.position.set(30,50,40); scene.add(key);
const fill = new THREE.DirectionalLight(0xffffff, 0.45); fill.position.set(-40,20,-30); scene.add(fill);

let parts = [], labels = [];
const edgeMat = new THREE.LineBasicMaterial({ color:0x2a2c30 });
const BOX = 0xcaa96f, BOT = 0xd8c187;

function clear(){
  for (const p of parts) scene.remove(p.mesh);
  for (const l of labels) scene.remove(l);
  parts = []; labels = [];
}
function addPart(cx,cy,cz,w,h,d,color,dir){
  const geo = new THREE.BoxGeometry(w,h,d);
  const mesh = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({color, roughness:0.72}));
  mesh.position.set(cx,cy,cz);
  mesh.add(new THREE.LineSegments(new THREE.EdgesGeometry(geo), edgeMat));
  scene.add(mesh);
  parts.push({mesh, home:mesh.position.clone(), dir:new THREE.Vector3(...dir)});
}
function roundRect(g,x,y,w,h,r){g.beginPath();g.moveTo(x+r,y);g.arcTo(x+w,y,x+w,y+h,r);g.arcTo(x+w,y+h,x,y+h,r);g.arcTo(x,y+h,x,y,r);g.arcTo(x,y,x+w,y,r);g.closePath();}
function makeLabel(text,x,y,z){
  const pad=10,fs=42,cvs=document.createElement('canvas'),g=cvs.getContext('2d');
  g.font=`bold ${fs}px sans-serif`; const w=g.measureText(text).width;
  cvs.width=w+pad*2; cvs.height=fs+pad*2; g.font=`bold ${fs}px sans-serif`;
  g.fillStyle='rgba(20,22,26,.88)'; roundRect(g,0,0,cvs.width,cvs.height,12); g.fill();
  g.fillStyle='#ffd18a'; g.textBaseline='middle'; g.fillText(text,pad,cvs.height/2);
  const spr=new THREE.Sprite(new THREE.SpriteMaterial({map:new THREE.CanvasTexture(cvs),depthTest:false,transparent:true}));
  spr.scale.set(cvs.width*0.02, cvs.height*0.02, 1); spr.position.set(x,y,z);
  scene.add(spr); labels.push(spr);
}

function build(i){
  clear();
  const d = DRAWERS[i];
  const W = d.exterior_width, H = d.box_height, D = d.slide_length;
  const fb = d.frontback_length;
  // center the box on origin: x[-W/2..W/2], y[-H/2..H/2], z[-D/2..D/2]
  // sides (full depth, full height)
  addPart(-W/2+T/2, 0, 0, T, H, D, BOX, [-14,0,0]);
  addPart( W/2-T/2, 0, 0, T, H, D, BOX, [ 14,0,0]);
  // front/back (height full; length fb; standard=between sides, boxjoint=full W)
  addPart(0, 0,  D/2-T/2, fb, H, T, BOX, [0,0, 14]);
  addPart(0, 0, -D/2+T/2, fb, H, T, BOX, [0,0,-14]);
  // bottom (floats in groove, near the bottom edge)
  const by = -H/2 + GD + BT/2;
  addPart(0, by, 0, W-2*T+2*GD, BT, D-2*T+2*GD, BOT, [0,-16,0]);

  makeLabel(d.label+'  —  exterior '+d.ext_txt, 0, H/2+3, D/2);
  makeLabel('width '+d.ext_txt, 0, -H/2-3, D/2);
  makeLabel('height '+d.h_txt, W/2+2, 0, D/2);
  makeLabel('depth / slide '+d.d_txt, W/2+2, -H/2-3, 0);
  controls.target.set(0,0,0);
}

// UI
const sel = document.getElementById('sel');
DRAWERS.forEach((d,i)=>{ const o=document.createElement('option'); o.value=i; o.textContent=d.label; sel.appendChild(o); });
sel.addEventListener('change', ()=>{ build(+sel.value); });
const ex = document.getElementById('explode'); let exVal=0, exTgt=0;
ex.addEventListener('input', ()=>{ exTgt=parseFloat(ex.value); });
document.getElementById('reset').addEventListener('click', ()=>{ camera.position.copy(DEFAULT_CAM); controls.target.set(0,0,0); ex.value=0; exTgt=0; });
let lblOn=true; document.getElementById('lbl').addEventListener('click', e=>{ lblOn=!lblOn; e.target.classList.toggle('on',lblOn); labels.forEach(l=>l.visible=lblOn); });
let spin=false; document.getElementById('spin').addEventListener('click', e=>{ spin=!spin; e.target.classList.toggle('on',spin); });
window.addEventListener('resize', ()=>{ camera.aspect=host.clientWidth/host.clientHeight; camera.updateProjectionMatrix(); renderer.setSize(host.clientWidth, host.clientHeight); });

build(0);
const tmp = new THREE.Vector3();
(function animate(){
  requestAnimationFrame(animate);
  exVal += (exTgt-exVal)*0.12;
  for (const p of parts){ tmp.copy(p.dir).multiplyScalar(exVal); p.mesh.position.copy(p.home).add(tmp); }
  if (spin) scene.rotation.y += 0.004;
  controls.update(); renderer.render(scene, camera);
})();
</script>
"""


def build_html(cfg):
    g, drawers, warnings, denom = compute(cfg)
    t = parse_len(g["material_thickness"]); bt = parse_len(g["bottom_thickness"])
    gd = parse_len(g["groove_depth"])

    # data for three.js (one entry per drawer definition, not per qty)
    three_data = []
    sections = []
    for d in drawers:
        three_data.append({
            "label": f'{d["label"]} (x{d["qty"]})',
            "exterior_width": d["exterior_width"], "inside_width": d["inside_width"],
            "box_height": d["box_height"], "slide_length": d["slide_length"],
            "frontback_length": d["parts"]["frontback"]["length"],
            "ext_txt": F(d["exterior_width"], denom), "h_txt": F(d["box_height"], denom),
            "d_txt": F(d["slide_length"], denom),
        })
        sections.append(f"""
  <h2>{d['label']} &nbsp;<span class="tag">x{d['qty']} · {d['construction']} · {d['slide_length']:g}" slides</span></h2>
  <div class="grid">
    <div class="card"><div class="cap">Front elevation</div>{front_elevation(d, t, denom)}</div>
    <div class="card"><div class="cap">Side section</div>{side_section(d, t, bt, gd, denom)}</div>
    <div class="card wide"><div class="cap">Cut these pieces</div>{exploded_parts(d, t, bt, denom)}</div>
  </div>""")

    three = (THREE_TEMPLATE
             .replace("__DRAWERS_JSON__", json.dumps(three_data))
             .replace("__T__", repr(t)).replace("__BT__", repr(bt)).replace("__GD__", repr(gd)))

    warn_html = ""
    if warnings:
        items = "".join(f"<li>{w}</li>" for w in warnings)
        warn_html = f'<div class="warn"><strong>Check:</strong><ul>{items}</ul></div>'

    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Blum Drawer Plans</title>
<style>
  body{{margin:0;background:#15171a;color:#e8e6e1;font-family:-apple-system,Segoe UI,Roboto,sans-serif;}}
  .wrap{{max-width:1040px;margin:0 auto;padding:22px 20px 70px;}}
  h1{{font-size:20px;margin:0 0 4px;}} h2{{font-size:15px;margin:30px 0 8px;color:#ffd18a;}}
  .sub{{color:#9aa0a6;font-size:12px;margin:0 0 16px;}}
  .tag{{color:#9aa0a6;font-size:11px;font-weight:400;}}
  .card{{background:#1e2125;border:1px solid #33373d;border-radius:12px;padding:14px;margin:10px 0;}}
  .cap{{font-size:11px;text-transform:uppercase;letter-spacing:.04em;color:#9aa0a6;margin-bottom:8px;}}
  .grid{{display:grid;grid-template-columns:1fr 1fr;gap:12px;}} .wide{{grid-column:1/3;}}
  svg{{width:100%;height:auto;background:#fbfaf7;border-radius:8px;}}
  #viewer{{height:440px;background:#1b1d21;border-radius:12px;border:1px solid #33373d;position:relative;}}
  .ctl{{margin:10px 0;display:flex;gap:8px;align-items:center;flex-wrap:wrap;font-size:12px;}}
  button,select{{background:#2f333a;color:#e8e6e1;border:1px solid #474b53;border-radius:7px;padding:6px 10px;font-size:12px;cursor:pointer;}}
  button.on{{background:#4a6b8a;border-color:#6b93b8;}} input[type=range]{{width:160px;}}
  .warn{{background:#3a2a16;border:1px solid #6b4e23;color:#ffd9a0;border-radius:10px;padding:10px 14px;font-size:13px;}}
  table{{border-collapse:collapse;width:100%;font-size:13px;margin-top:6px;}}
  th,td{{border-bottom:1px solid #30333a;padding:6px 8px;text-align:left;}} td:not(:first-child){{text-align:right;}}
  th{{color:#9aa0a6;font-size:11px;text-transform:uppercase;}}
  @media print{{body{{background:#fff;color:#000}}.card{{border:1px solid #ccc}}#viewer{{display:none}}h2{{color:#8a5a00}}}}
</style></head>
<body><div class="wrap">
  <h1>Blum Undermount Drawer — Plans</h1>
  <p class="sub">Interactive 3D + dimensioned shop drawings. Drag to rotate, scroll to zoom. Dims in inches.</p>
  {warn_html}
  <div id="viewer"></div>
  <div class="ctl">
    <label>Drawer</label><select id="sel"></select>
    <label>Explode</label><input id="explode" type="range" min="0" max="1" step="0.01" value="0"/>
    <button id="reset">Reset</button><button id="lbl" class="on">Labels</button><button id="spin">Spin</button>
  </div>
  {''.join(sections)}
</div>
{three}
</body></html>"""


def main():
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(1)
    cfg = json.loads(sys.stdin.read() if sys.argv[1] == "-" else open(sys.argv[1]).read())
    html = build_html(cfg)
    if sys.argv[2] == "-":
        sys.stdout.write(html)
    else:
        open(sys.argv[2], "w").write(html)
        print(f"wrote {sys.argv[2]}")


if __name__ == "__main__":
    main()
