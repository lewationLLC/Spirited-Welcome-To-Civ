#!/usr/bin/env python3
"""Generate design/world/overhead-layout.svg (the overhead world map).

Run:  python3 design/world/make_overhead_layout.py
Then render the PNG from the SVG (see README.md in this folder).

Everything is placed by hand in map coordinates (1600 x 1200, north up).
Mountains are scattered with a fixed seed so the output is reproducible.
"""
import math
import random
from pathlib import Path

W, H = 1600, 1200
rng = random.Random(7)
out = []


def add(s):
    out.append(s)


def bez(p0, p1, p2, p3, t):
    u = 1 - t
    return (
        u**3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t**3 * p3[0],
        u**3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t**3 * p3[1],
    )


def label(x, y, text, size=13, bold=False, italic=False, anchor="middle",
          rot=0, fill="#2b211a", halo="#f4ead6"):
    add(
        f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{"bold" if bold else "normal"}"'
        f'{" font-style=\"italic\"" if italic else ""} fill="{fill}" text-anchor="{anchor}"'
        f' transform="rotate({rot} {x} {y})" paint-order="stroke" stroke="{halo}"'
        f' stroke-width="5" stroke-linejoin="round">{text}</text>'
    )


def pts(points):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in points)


# ---------------------------------------------------------------- geometry
# Spine of the mountain range: runs from far off to the north-east (where it
# recedes into the distance) down to the south, bowing round the Arrowhead.
SPINE = [(1700, -80), (900, 150), (480, 470), (420, 1290)]
spine = [bez(*SPINE, i / 400) for i in range(401)]
HALF_W = 115  # half-width of the range

# The Arrowhead and the line of flight (south-east, 45 degrees).
AH = (370, 300)            # centre of the exposed blade
DIR = (math.sqrt(0.5), math.sqrt(0.5))
TIP = (AH[0] + 48 * DIR[0], AH[1] + 48 * DIR[1])


def spine_info(p):
    """Return (distance to spine, spine param t, side) side>0 = east/south."""
    best = (1e9, 0, 0)
    for i in range(len(spine) - 1):
        ax, ay = spine[i]
        bx, by = spine[i + 1]
        dx, dy = bx - ax, by - ay
        L2 = dx * dx + dy * dy
        s = max(0, min(1, ((p[0] - ax) * dx + (p[1] - ay) * dy) / L2))
        cx, cy = ax + s * dx, ay + s * dy
        d = math.hypot(p[0] - cx, p[1] - cy)
        if d < best[0]:
            cross = dx * (p[1] - ay) - dy * (p[0] - ax)
            best = (d, (i + s) / (len(spine) - 1), 1 if cross < 0 else -1)
    return best


def valley_dist(p):
    """Perpendicular distance from the line of flight through the tip."""
    vx, vy = p[0] - TIP[0], p[1] - TIP[1]
    return abs(vx * DIR[1] - vy * DIR[0])


# Valley mouth: where the line of flight leaves the range on the far side.
s = 0
while True:
    s += 2
    p = (TIP[0] + s * DIR[0], TIP[1] + s * DIR[1])
    d, t, side = spine_info(p)
    if side > 0 and d > HALF_W + 10:
        MOUTH = p
        break

# Wall and Great Gate.
WALL = [(1250, 520), (1070, 780), (1010, 960), (1010, 1260)]
GATE = bez(*WALL, 0.42)

INSET = (1290, 24, 1586, 452)  # Academy Arena detail panel


def in_box(p, box, pad=0):
    return box[0] - pad < p[0] < box[2] + pad and box[1] - pad < p[1] < box[3] + pad


# ---------------------------------------------------------------- svg start
add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" '
    f'height="{H}" font-family="DejaVu Serif, Georgia, serif">')
add("""<defs>
<linearGradient id="sea" x1="0" x2="1"><stop offset="0" stop-color="#1f4f86"/><stop offset="1" stop-color="#3b78b5"/></linearGradient>
<pattern id="wild" width="34" height="34" patternUnits="userSpaceOnUse"><circle cx="8" cy="9" r="4" fill="#5d6b3a" opacity=".55"/><circle cx="25" cy="24" r="5" fill="#4e5c30" opacity=".5"/><path d="M20 6 l3 -5 l3 5z" fill="#6b5a3a" opacity=".5"/></pattern>
<pattern id="farm" width="36" height="36" patternUnits="userSpaceOnUse" patternTransform="rotate(28)"><rect width="36" height="36" fill="#a9c26a"/><rect width="18" height="18" fill="#c9cf7a"/><rect x="18" y="18" width="18" height="18" fill="#8fae55"/><path d="M0 9h18M18 27h18" stroke="#7f9a4a" stroke-width=".8" opacity=".6"/></pattern>
<pattern id="grass" width="26" height="26" patternUnits="userSpaceOnUse"><rect width="26" height="26" fill="#cfd2a0"/><path d="M5 8l2-4 2 4M17 20l2-4 2 4" stroke="#8d9a5c" stroke-width="1" fill="none"/></pattern>
<radialGradient id="glow"><stop offset="0" stop-color="#5fd6e8" stop-opacity=".9"/><stop offset="1" stop-color="#5fd6e8" stop-opacity="0"/></radialGradient>
<filter id="soft"><feGaussianBlur stdDeviation="1.2"/></filter>
</defs>""")

# Base desert.
add(f'<rect width="{W}" height="{H}" fill="#e6d3ab"/>')

# Far side of the range (the Breach's country): grassland.
far = [p for p in spine] + [(W + 50, H + 50), (W + 50, -100)]
add(f'<polygon points="{pts(far)}" fill="url(#grass)"/>')

# The Wildlands of the West: west of the range, south of the city.
wild = [(0, 450), (140, 445), (250, 470), (330, 520)]
wild += [p for p in spine if p[1] > 520]
wild += [(0, H + 50)]
add(f'<polygon points="{pts(wild)}" fill="url(#wild)"/>')
add(f'<polygon points="{pts(wild)}" fill="#7f8a52" opacity=".22"/>')

# Cleared farmland (buffer zone): a fan from the valley mouth to the wall.
mx, my = MOUTH
farm = f"M{mx-30:.0f} {my-20:.0f} C{mx+60:.0f} {my-110:.0f} 1080 640 1150 650 " \
       f"L{WALL[1][0]:.0f} {WALL[1][1]:.0f} C1010 960 1010 960 1010 1210 " \
       f"L760 1210 C700 1050 {mx-90:.0f} {my+90:.0f} {mx-30:.0f} {my-20:.0f}Z"
add(f'<path d="{farm}" fill="url(#farm)" stroke="#6f8a3e" stroke-width="2" opacity=".95"/>')
for i in range(14):  # farmhouses
    x = rng.uniform(mx + 20, 990)
    y = rng.uniform(my + 10, 1180)
    if spine_info((x, y))[0] < HALF_W + 25:
        continue
    add(f'<rect x="{x:.0f}" y="{y:.0f}" width="9" height="7" fill="#b5603a" stroke="#5a3a28" stroke-width=".8"/>')

# River on the far side, out of the range and south past the farms.
add('<path d="M860 360 C900 460 930 560 905 640 C885 720 880 760 905 820 C930 930 860 1040 900 1210" '
    'stroke="#5fa3b5" stroke-width="9" fill="none" stroke-linecap="round"/>')

# ---------------------------------------------------------------- the sea
add('<ellipse cx="330" cy="270" rx="230" ry="165" fill="#e8b986" opacity=".55"/>')
add('<path d="M0 0 L150 0 C140 80 175 140 150 200 C120 250 200 300 175 330 '
    'C150 370 90 400 60 440 L0 455Z" fill="url(#sea)"/>')
add('<path d="M150 200 C215 205 245 250 230 285 C210 320 170 330 175 330 '
    'C200 300 120 250 150 200Z" fill="#2d5d9a"/>')
add('<ellipse cx="270" cy="372" rx="46" ry="25" fill="#3fb7c9"/>')

# ---------------------------------------------------------------- the city
# great rock pillar (overhead: cap with a shadow)
add('<ellipse cx="400" cy="178" rx="44" ry="32" fill="#8a3f24" opacity=".35" transform="translate(10 10)"/>')
add('<ellipse cx="400" cy="178" rx="44" ry="32" fill="#d9773f" stroke="#8a3f24" stroke-width="2"/>')
add('<ellipse cx="398" cy="176" rx="22" ry="15" fill="#b55a30" opacity=".7"/>')
# crater rim round the buried point
add(f'<circle cx="{TIP[0]-6:.0f}" cy="{TIP[1]-6:.0f}" r="38" fill="#c9a27a" opacity=".55" '
    f'stroke="#7a5a3a" stroke-width="2" stroke-dasharray="5 4"/>')
# buildings
for i in range(150):
    a = rng.uniform(0, 2 * math.pi)
    r = rng.uniform(30, 150)
    x = 320 + r * math.cos(a) * 1.25
    y = 290 + r * math.sin(a) * 0.95
    if math.hypot(x - 400, y - 178) < 50 or (x - 270) ** 2 / 50 ** 2 + (y - 372) ** 2 / 29 ** 2 < 1:
        continue
    if x < 175 or spine_info((x, y))[0] < HALF_W:
        continue
    sz = rng.uniform(5, 10)
    add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{sz:.1f}" height="{sz*0.8:.1f}" '
        f'fill="#c9a27a" stroke="#8a6a4a" stroke-width=".7"/>')
# domed palace
add('<circle cx="285" cy="300" r="15" fill="#e3c9a3" stroke="#8a6a4a" stroke-width="2"/>'
    '<circle cx="285" cy="300" r="6" fill="#c9a27a"/>')
add('<circle cx="312" cy="318" r="8" fill="#e3c9a3" stroke="#8a6a4a" stroke-width="1.5"/>')
# palms along the waterfront
for x, y in [(212, 330), (222, 342), (236, 349), (300, 360), (314, 352), (198, 318)]:
    add(f'<circle cx="{x}" cy="{y}" r="5" fill="#4c6b2e"/>')
# causeway between the two bays
add('<path d="M110 420 C160 400 210 360 252 318" stroke="#8c6a48" stroke-width="7" '
    'fill="none" stroke-linecap="round"/>')

# The Arrowhead itself (overhead), shadow first. Local +x = direction of point.
blade = "M58 0 L10 -20 L-18 -26 L-22 -11 L-46 -9 L-46 9 L-22 11 L-18 26 L10 20Z"
ang = 45
add(f'<path d="{blade}" fill="#000" opacity=".25" transform="translate({AH[0]-14} {AH[1]+6}) rotate({ang})"/>')
add(f'<path d="{blade}" fill="#22232e" stroke="#5a5f8c" stroke-width="2.2" '
    f'transform="translate({AH[0]} {AH[1]}) rotate({ang})"/>')
add(f'<path d="M50 0 L-40 0 M10 -16 L-10 6 M14 14 L-6 -6 M-14 -20 L-26 2" stroke="#5a5f8c" '
    f'stroke-width="1.2" opacity=".8" transform="translate({AH[0]} {AH[1]}) rotate({ang})"/>')

# ---------------------------------------------------------------- mountains
def mountain(x, y, s, fill, stroke, op):
    add(f'<g opacity="{op:.2f}"><path d="M{x-s:.1f} {y+s*0.45:.1f} L{x:.1f} {y-s:.1f} '
        f'L{x+s:.1f} {y+s*0.45:.1f}Z" fill="{fill}" stroke="{stroke}" stroke-width="1"/>'
        f'<path d="M{x:.1f} {y-s:.1f} L{x+s*0.3:.1f} {y-s*0.4:.1f} L{x:.1f} {y-s*0.25:.1f}Z" '
        f'fill="#f3efe6" opacity=".85"/></g>')


cands = []
for i in range(5000):
    t = rng.random()
    cx, cy = bez(*SPINE, t)
    # sample a point across the range at this t
    t2 = min(1, t + 0.002)
    nx, ny = bez(*SPINE, t2)
    dx, dy = nx - cx, ny - cy
    L = math.hypot(dx, dy) or 1
    off = rng.gauss(0, HALF_W * 0.5)
    if abs(off) > HALF_W:
        continue
    x, y = cx + (-dy / L) * off, cy + (dx / L) * off
    if not (-20 < x < W + 20 and -20 < y < H + 20):
        continue
    if in_box((x, y), INSET, 18):
        continue
    vd = valley_dist((x, y))
    along = (x - TIP[0]) * DIR[0] + (y - TIP[1]) * DIR[1]
    if vd < 26 and along > -10:
        continue
    if math.hypot(x - 330, y - 280) < 165:
        continue
    # recede: smaller and paler toward the north-east
    depth = max(0.0, min(1.0, (0.45 - t) / 0.45))
    size = (8 + 9 * (1 - abs(off) / HALF_W)) * (1 - 0.55 * depth)
    if vd < 45 and along > 0:
        size *= 1.25  # the sheer walls of the cut
    op = 1 - 0.6 * depth
    shade = rng.choice(["#8a6a4d", "#a88664", "#97765a"])
    cands.append((y, x, size, shade, op))
cands.sort()
placed = []
for y, x, size, shade, op in cands:
    if any(abs(x - px) < size * 0.9 and abs(y - py) < size * 0.6 for px, py in placed[-260:]):
        continue
    placed.append((x, y))
    mountain(x, y, size, shade, "#5a4636", op)

# Death Valley: the straight cut of the arrow's flight.
add(f'<line x1="{TIP[0]:.0f}" y1="{TIP[1]:.0f}" x2="{MOUTH[0]:.0f}" y2="{MOUTH[1]:.0f}" '
    f'stroke="#3f342b" stroke-width="22" stroke-linecap="butt"/>')
add(f'<line x1="{TIP[0]:.0f}" y1="{TIP[1]:.0f}" x2="{MOUTH[0]:.0f}" y2="{MOUTH[1]:.0f}" '
    f'stroke="#22232e" stroke-width="22" stroke-dasharray="3 16" opacity=".8"/>')
add(f'<line x1="{TIP[0]:.0f}" y1="{TIP[1]:.0f}" x2="{MOUTH[0]:.0f}" y2="{MOUTH[1]:.0f}" '
    f'stroke="#b9a27e" stroke-width="3" stroke-dasharray="6 6"/>')

# Road: valley mouth across the farms (bridge over the river) to the gate.
add(f'<path d="M{MOUTH[0]:.0f} {MOUTH[1]:.0f} C{MOUTH[0]+60:.0f} {MOUTH[1]+60:.0f} '
    f'{GATE[0]-80:.0f} {GATE[1]-30:.0f} {GATE[0]:.0f} {GATE[1]:.0f}" stroke="#b9a27e" '
    f'stroke-width="5" fill="none" stroke-dasharray="1 0"/>')
# cypress row along the road
for k in range(9):
    tt = k / 9
    x, y = bez(MOUTH, (MOUTH[0] + 60, MOUTH[1] + 60), (GATE[0] - 80, GATE[1] - 30), GATE, tt)
    add(f'<circle cx="{x+6:.0f}" cy="{y-9:.0f}" r="3.2" fill="#1e2a1a"/>')

# ---------------------------------------------------------------- the Breach
breach = f"M{WALL[0][0]} {WALL[0][1]} C{WALL[1][0]} {WALL[1][1]} {WALL[2][0]} {WALL[2][1]} " \
         f"{WALL[3][0]} {WALL[3][1]} L{W+20} {H+20} L{W+20} {WALL[0][1]-60}Z"
add(f'<path d="{breach}" fill="#e2d6bd"/>')
# Citadel hill
add('<ellipse cx="1300" cy="770" rx="95" ry="70" fill="#9fb06a" stroke="#6f7e45" stroke-width="2"/>')
add('<ellipse cx="1300" cy="770" rx="60" ry="42" fill="#b5c27d" opacity=".8"/>')
add('<polygon points="1272,748 1328,748 1336,770 1328,792 1272,792 1264,770" fill="#e8e2d2" stroke="#4a443d" stroke-width="2.5"/>')
for x, y in [(1272, 748), (1328, 748), (1328, 792), (1272, 792)]:
    add(f'<rect x="{x-5}" y="{y-5}" width="10" height="10" fill="#dcd8cc" stroke="#4a443d" stroke-width="1.5"/>')
add('<rect x="1291" y="760" width="18" height="18" fill="#7d7468"/>')
# streets and houses of the town
add(f'<path d="M{GATE[0]:.0f} {GATE[1]:.0f} L1150 905 L1235 830 L1270 792" stroke="#b9a27e" stroke-width="6" fill="none"/>')
add('<path d="M1150 905 L1180 1010 M1150 905 L1350 930 L1480 900 M1180 1010 L1420 1060 '
    'M1350 930 L1380 1100 M1235 830 L1440 820" stroke="#c7b48e" stroke-width="4" fill="none"/>')
add('<circle cx="1150" cy="905" r="16" fill="#efe4c8" stroke="#b9a27e" stroke-width="2"/>')  # gate plaza
for i in range(330):
    x = rng.uniform(1040, 1590)
    y = rng.uniform(560, 1190)
    if x < bez(*WALL, max(0, min(1, (y - 520) / 740)))[0] + 22:
        continue
    if (x - 1300) ** 2 / 100 ** 2 + (y - 770) ** 2 / 75 ** 2 < 1:
        continue
    if (x - 1235) ** 2 + (y - 1065) ** 2 < 112 ** 2:
        continue
    if in_box((x, y), INSET, 10) or abs(x - 1150) + abs(y - 905) < 24:
        continue
    sz = rng.uniform(5, 9)
    add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{sz:.1f}" height="{sz*0.8:.1f}" '
        f'fill="#cdbf9f" stroke="#8a7b62" stroke-width=".7"/>')
# market stalls by the gate plaza
for i in range(16):
    x = 1160 + rng.uniform(-40, 70)
    y = 935 + rng.uniform(-15, 30)
    add(f'<rect x="{x:.0f}" y="{y:.0f}" width="5" height="5" fill="{rng.choice(["#b5603a", "#c9b86a", "#7a3a2a"])}"/>')

# Academy Arena (overhead icon): sunken bowl, parapet ring, moat, octagon.
AX, AY = 1235, 1065
add(f'<ellipse cx="{AX}" cy="{AY}" rx="104" ry="92" fill="#14243a" stroke="#0c1624" stroke-width="3"/>')
for r in range(3):
    add(f'<ellipse cx="{AX}" cy="{AY}" rx="{92-r*12}" ry="{80-r*11}" fill="none" stroke="#1f3b3a" stroke-width="5"/>')
add(f'<ellipse cx="{AX}" cy="{AY}" rx="56" ry="48" fill="#7a3a2a"/>')
add(f'<ellipse cx="{AX}" cy="{AY}" rx="51" ry="44" fill="#d9d2c0"/>')
add(f'<circle cx="{AX}" cy="{AY}" r="58" fill="url(#glow)" opacity=".6"/>')
add(f'<ellipse cx="{AX}" cy="{AY}" rx="45" ry="39" fill="#5fd6e8"/>')
octo = [(AX + 24 * math.cos(math.radians(22.5 + 45 * k)), AY + 24 * math.sin(math.radians(22.5 + 45 * k))) for k in range(8)]
add(f'<polygon points="{pts(octo)}" fill="#d8be8e" stroke="#a88a5a" stroke-width="2"/>')
add(f'<line x1="{AX}" y1="{AY-22}" x2="{AX}" y2="{AY+22}" stroke="#7a5a3a" stroke-width="1.2"/>')
# entrance ramp cutting through the stands (north-west, facing the plaza)
add(f'<polygon points="{AX-60},{AY-74} {AX-82},{AY-58} {AX-40},{AY-28} {AX-30},{AY-38}" fill="#c9b86a" stroke="#5a4636" stroke-width="1"/>')
for i in range(70):
    a = rng.uniform(0, 2 * math.pi)
    r = rng.uniform(0.62, 0.97)
    add(f'<circle cx="{AX+104*r*math.cos(a):.1f}" cy="{AY+92*r*math.sin(a):.1f}" r="1" fill="#c9b86a"/>')

# Wall over everything in the Breach, with towers and the Great Gate.
add(f'<path d="M{WALL[0][0]} {WALL[0][1]} C{WALL[1][0]} {WALL[1][1]} {WALL[2][0]} {WALL[2][1]} '
    f'{WALL[3][0]} {WALL[3][1]}" stroke="#9ea3a8" stroke-width="12" fill="none"/>')
add(f'<path d="M{WALL[0][0]} {WALL[0][1]} C{WALL[1][0]} {WALL[1][1]} {WALL[2][0]} {WALL[2][1]} '
    f'{WALL[3][0]} {WALL[3][1]}" stroke="#dcd8cc" stroke-width="7" fill="none"/>')
for k in range(1, 12):
    x, y = bez(*WALL, k / 12)
    if abs(k / 12 - 0.42) < 0.05:
        continue
    add(f'<rect x="{x-5:.0f}" y="{y-5:.0f}" width="10" height="10" fill="#dcd8cc" stroke="#6f6a60" stroke-width="1.5"/>')
gx, gy = GATE
add(f'<g transform="translate({gx:.0f} {gy:.0f}) rotate(-22)"><rect x="-13" y="-17" width="26" height="34" '
    f'fill="#7d7468" stroke="#4a443d" stroke-width="2"/><rect x="-5" y="-17" width="10" height="34" fill="#4a443d"/>'
    f'<circle cx="-13" cy="-17" r="5" fill="#7d7468" stroke="#4a443d"/><circle cx="-13" cy="17" r="5" fill="#7d7468" stroke="#4a443d"/></g>')

# ---------------------------------------------------------------- labels
label(310, 112, "THE ARROWHEAD", 26, bold=True)
label(310, 134, "desert port city", 14, italic=True)
label(452, 170, "great rock pillar", 12, anchor="start")
label(TIP[0] + 36, TIP[1] + 6, "the Arrowhead (obsidian)", 12, anchor="start", fill="#22232e")
label(TIP[0] + 36, TIP[1] + 22, "point buried, faces SE", 11, italic=True, anchor="start", fill="#7a2e1d")
label(250, 296, "palace", 11, anchor="end")
label(270, 406, "lagoon", 11)
label(150, 182, "deep bay", 12, anchor="end", fill="#e9f1fb", halo="#1f4f86")
label(150, 418, "causeway", 11, rot=-36)
label(62, 300, "THE SEA", 18, bold=True, fill="#e9f1fb", halo="#1f4f86")

vx, vy = (TIP[0] + MOUTH[0]) / 2, (TIP[1] + MOUTH[1]) / 2
label(vx - 26, vy + 26, "DEATH VALLEY", 19, bold=True, rot=45)
label(vx - 44, vy + 44, "the arrow's cut through the range (cutscene)", 11, italic=True, rot=45)
label(1010, 300, "MOUNTAIN RANGE", 22, bold=True, rot=-30)
label(1120, 205, "recedes into the distance →", 13, italic=True, rot=-30)

label(170, 760, "THE WILDLANDS", 26, bold=True)
label(170, 784, "of the West", 15, italic=True)

label(870, 1000, "CLEARED FARMLAND", 13, bold=True)
label(870, 1017, "the Breach's buffer zone", 11, italic=True)
label(gx - 26, gy + 6, "GREAT GATE", 15, bold=True, anchor="end")
label(1150, 534, "city wall", 12, anchor="start")
label(1300, 690, "Citadel on the Hill", 14, bold=True)
label(1300, 707, "seat of the Yikiza clan", 11, italic=True)
label(1150, 880, "gate plaza &amp; market", 11, anchor="middle")
label(AX, AY + 112, "ACADEMY ARENA", 14, bold=True)
label(AX, AY + 128, "where the Bouts are fought", 11, italic=True)
label(1440, 1150, "THE BREACH", 24, bold=True)
label(1440, 1172, "of Civilization · liars, thieves &amp; merchants", 12, italic=True)

# Compass (over the sea).
add('<g transform="translate(78 78)"><circle r="40" fill="#f4ead6" stroke="#5a4636" stroke-width="2"/>'
    '<path d="M0 -32 L7 0 L0 32 L-7 0Z" fill="#5a4636"/><path d="M0 -32 L7 0 L-7 0Z" fill="#7a2e1d"/>'
    '<path d="M-32 0 L0 -6 L32 0 L0 6Z" fill="#a88664"/>'
    '<path d="M0 0 L26 26" stroke="#22232e" stroke-width="3" stroke-dasharray="4 3"/>'
    '<text y="-45" text-anchor="middle" font-size="15" font-weight="bold" fill="#f4ead6">N</text>'
    '<text x="30" y="38" font-size="11" font-weight="bold" fill="#22232e">SE</text></g>')

# Legend.
add('<g transform="translate(24 952)"><rect width="380" height="224" rx="8" fill="#f4ead6" '
    'stroke="#5a4636" stroke-width="1.5" opacity=".96"/>'
    '<text x="16" y="28" font-size="17" font-weight="bold">Overhead layout</text>'
    '<text x="16" y="48" font-size="12">Not to scale. North is up.</text>'
    '<text x="16" y="70" font-size="12">Travel: Wildlands → the Arrowhead → Death Valley</text>'
    '<text x="16" y="86" font-size="12">→ farmland → Great Gate → the Breach</text>'
    f'<path d="{blade}" fill="#22232e" stroke="#5a5f8c" stroke-width="2" transform="translate(40 112) scale(.38)"/>'
    '<text x="66" y="116" font-size="12">the Arrowhead (fallen obsidian arrowhead)</text>'
    '<rect x="22" y="132" width="36" height="8" fill="#3f342b"/>'
    '<text x="66" y="140" font-size="12">Death Valley (the arrow\'s line of flight)</text>'
    '<rect x="22" y="152" width="36" height="7" fill="#dcd8cc" stroke="#9ea3a8" stroke-width="2"/>'
    '<text x="66" y="161" font-size="12">city wall</text>'
    '<rect x="22" y="172" width="36" height="12" fill="url(#farm)"/>'
    '<text x="66" y="182" font-size="12">cleared farmland (buffer zone)</text>'
    '<circle cx="40" cy="203" r="9" fill="#5fd6e8" stroke="#14243a" stroke-width="4"/>'
    '<text x="66" y="207" font-size="12">Academy Arena (sunken stadium, moat)</text></g>')

# ---------------------------------------------------------------- arena inset
x0, y0, x1, y1 = INSET
add(f'<g><rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" rx="8" fill="#f4ead6" '
    f'stroke="#5a4636" stroke-width="1.5"/>')
add(f'<text x="{(x0+x1)/2}" y="{y0+24}" font-size="15" font-weight="bold" text-anchor="middle">Academy Arena — plan</text>')
cx, cy = (x0 + x1) / 2, y0 + 150
add(f'<ellipse cx="{cx}" cy="{cy}" rx="128" ry="112" fill="#14243a"/>')
for r in range(6):
    add(f'<ellipse cx="{cx}" cy="{cy}" rx="{122-r*9}" ry="{106-r*8}" fill="none" stroke="#1f3b3a" stroke-width="4"/>')
for i in range(220):
    a = rng.uniform(0, 2 * math.pi)
    r = rng.uniform(0.6, 0.97)
    add(f'<circle cx="{cx+128*r*math.cos(a):.1f}" cy="{cy+112*r*math.sin(a):.1f}" r="1" fill="#c9b86a"/>')
add(f'<ellipse cx="{cx}" cy="{cy}" rx="70" ry="62" fill="#7a3a2a"/>')
add(f'<ellipse cx="{cx}" cy="{cy}" rx="65" ry="57" fill="#d9d2c0"/>')
add(f'<ellipse cx="{cx}" cy="{cy}" rx="58" ry="51" fill="#5fd6e8"/>')
add(f'<ellipse cx="{cx}" cy="{cy}" rx="52" ry="46" fill="none" stroke="#e8fbff" stroke-width="1.5" opacity=".7"/>')
oc = [(cx + 34 * math.cos(math.radians(22.5 + 45 * k)), cy + 34 * math.sin(math.radians(22.5 + 45 * k))) for k in range(8)]
add(f'<polygon points="{pts(oc)}" fill="#d8be8e" stroke="#a88a5a" stroke-width="2"/>')
add(f'<line x1="{cx}" y1="{cy-31}" x2="{cx}" y2="{cy+31}" stroke="#4a3a2a" stroke-width="1.4"/>')
for sx in (-1, 1):
    add(f'<line x1="{cx+sx*14}" y1="{cy-27}" x2="{cx+sx*14}" y2="{cy+27}" stroke="#4a3a2a" stroke-width=".9" stroke-dasharray="3 2"/>')
# entrance ramp
add(f'<polygon points="{cx-78},{cy-90} {cx-104},{cy-70} {cx-56},{cy-34} {cx-44},{cy-48}" fill="#c9b86a" stroke="#5a4636" stroke-width="1"/>')
# callouts
def callout(px, py, tx, ty, text, anchor="start"):
    add(f'<line x1="{px}" y1="{py}" x2="{tx}" y2="{ty}" stroke="#2b211a" stroke-width="1"/>'
        f'<circle cx="{px}" cy="{py}" r="2" fill="#2b211a"/>')
    label(tx + (3 if anchor == "start" else -3), ty + 4, text, 10, anchor=anchor)


callout(cx + 6, cy + 20, cx - 10, cy + 128, "octagonal platform", "middle")
callout(cx + 50, cy - 22, x1 - 6, cy - 120, "glowing moat", "end")
callout(cx + 100, cy + 52, x1 - 6, cy + 120, "sunken stands", "end")
callout(cx - 94, cy - 80, x0 + 10, cy - 116, "entrance ramp")
callout(cx - 66, cy + 10, x0 + 8, cy + 125, "parapet ring")
# section
sy = y0 + 330
add(f'<text x="{(x0+x1)/2}" y="{sy-18}" font-size="12" font-weight="bold" text-anchor="middle">Section (ground level dashed)</text>')
add(f'<line x1="{x0+8}" y1="{sy}" x2="{x1-8}" y2="{sy}" stroke="#5a4636" stroke-dasharray="4 3"/>')
sec = [(x0 + 12, sy), (x0 + 30, sy), (cx - 70, sy + 56), (cx - 58, sy + 56), (cx - 58, sy + 74),
       (cx + 58, sy + 74), (cx + 58, sy + 56), (cx + 70, sy + 56), (x1 - 30, sy), (x1 - 12, sy),
       (x1 - 12, sy + 84), (x0 + 12, sy + 84)]
add(f'<polygon points="{pts(sec)}" fill="#a88664" stroke="#5a4636" stroke-width="1.5"/>')
for k in range(1, 7):  # stepped tiers
    f = k / 7
    for side in (-1, 1):
        xa = cx + side * (cx - x0 - 30 - (cx - x0 - 100) * f)
        add(f'<line x1="{xa:.0f}" y1="{sy + 56*f:.0f}" x2="{xa + side*-9:.0f}" y2="{sy + 56*f:.0f}" stroke="#5a4636"/>')
add(f'<rect x="{cx-58}" y="{sy+60}" width="116" height="14" fill="#5fd6e8"/>')
add(f'<rect x="{cx-30}" y="{sy+44}" width="60" height="30" fill="#d8be8e" stroke="#a88a5a" stroke-width="1.5"/>')
label(cx, sy + 40, "arena", 10)
label(cx + 84, sy + 72, "moat", 10)
label(x0 + 50, sy + 40, "stands", 10)
add('</g>')

add("</svg>")
Path(__file__).with_name("overhead-layout.svg").write_text("\n".join(out))
print("wrote overhead-layout.svg", len(out), "elements; mouth", MOUTH, "gate", GATE)
