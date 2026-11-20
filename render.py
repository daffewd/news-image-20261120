"""Render the 20 Nov 2026 front page (1024x1024), v2: lead visual panel
(Kyiv bridges night scene), big market figures, larger type, page filled
to the footer. Deterministic: fixed fonts, fixed layout, no timestamps."""
import math

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (250, 240, 214)
INK = (20, 20, 20)
RED = (178, 34, 34)
GREY = (90, 90, 90)
NAVY = (16, 26, 54)
RIVER = (32, 92, 165)
ORANGE = (255, 130, 20)

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def _wrap(draw, text, fnt, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_para(draw, x, y, width, text, fnt, leading, color=INK):
    for line in _wrap(draw, text, fnt, width):
        draw.text((x, y), line, font=fnt, fill=color)
        y += leading
    return y


def rule(draw, y, x0=40, x1=984, width=3):
    draw.line([(x0, y), (x1, y)], fill=INK, width=width)
    return y + width


img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)
y = 12

# top bar
f_top = font(SANS_B, 25)
d.text((40, y), "ONE PAGE  \u2022  THE WORLD", font=f_top, fill=INK)
right = "FRIDAY 20 NOVEMBER 2026"
d.text((984 - d.textlength(right, font=f_top), y), right, font=f_top, fill=INK)
y += 32
y = rule(d, y, width=4)

# masthead
f_mast = font(SERIF_B, 72)
mast = "THE WORLD TODAY"
d.text(((W - d.textlength(mast, font=f_mast)) / 2, y + 2), mast, font=f_mast, fill=INK)
y += 80
y = rule(d, y, width=4)

# subline
f_sub = font(SERIF_I, 26)
sub = "Friday 20 November 2026 \u2014 the day's world news, in one picture"
d.text(((W - d.textlength(sub, font=f_sub)) / 2, y + 5), sub, font=f_sub, fill=GREY)
y += 36
y = rule(d, y, width=2)

# lead headline, one line (second half in red)
f_lead = font(SERIF_B, 50)
l1 = "KYIV BRIDGES HIT "
l2 = "OVERNIGHT"
w1 = d.textlength(l1, font=f_lead)
w2 = d.textlength(l2, font=f_lead)
x_start = (W - w1 - w2) / 2
d.text((x_start, y + 6), l1, font=f_lead, fill=INK)
d.text((x_start + w1, y + 6), l2, font=f_lead, fill=RED)
y += 62
f_body = font(SERIF, 30)
y = draw_para(
    d, 40, y, 944,
    "Russian ballistic missiles and drones damage three bridges across the Dnipro "
    "in Kyiv overnight, killing at least eight across Ukraine and cutting power "
    "\u2014 hours after Putin's Shenzhen talks with Trump and Xi.",
    f_body, 34)
y += 6

# --- lead visual panel: night scene, broken bridge ---
panel_y = y
panel_h = 88
px0, px1 = 40, 984
d.rectangle([px0, panel_y, px1, panel_y + panel_h], fill=NAVY, outline=INK, width=2)
river_y = panel_y + panel_h - 26
# moon
d.ellipse([px1 - 104, panel_y + 12, px1 - 64, panel_y + 52], fill=(242, 236, 200))
# drones: X shapes with faint dotted arcs
for dx, dy in [(180, 30), (330, 20), (440, 28)]:
    cx, cy = px0 + dx, panel_y + dy
    d.line([(cx - 10, cy - 10), (cx + 10, cy + 10)], fill=(210, 215, 230), width=3)
    d.line([(cx - 10, cy + 10), (cx + 10, cy - 10)], fill=(210, 215, 230), width=3)
    for t in range(9):
        ang = 0.5 + t * 0.22
        ax = cx + 88 * math.cos(ang)
        ay = cy + 54 * math.sin(ang)
        d.ellipse([ax - 2, ay - 2, ax + 2, ay + 2], fill=(150, 160, 190))
# river band
d.rectangle([px0 + 2, river_y, px1 - 2, panel_y + panel_h - 2], fill=RIVER)
# bridge deck and arches
deck_y = river_y - 24
deck_col = (200, 205, 215)
gap0, gap1 = 472, 560
d.rectangle([px0 + 14, deck_y, gap0, deck_y + 8], fill=deck_col)
d.rectangle([gap1, deck_y, px1 - 14, deck_y + 8], fill=deck_col)
# tilted broken segment in the gap
d.polygon([(gap0 + 4, deck_y + 10), (gap1 - 8, deck_y + 24),
           (gap1 - 4, deck_y + 32), (gap0 + 8, deck_y + 18)], fill=deck_col)
# arch spans (left intact, right intact, middle broken stubs)
d.arc([px0 + 30, deck_y - 6, px0 + 300, river_y + 20], start=0, end=180, fill=deck_col, width=4)
d.arc([px1 - 300, deck_y - 6, px1 - 30, river_y + 20], start=0, end=180, fill=deck_col, width=4)
d.arc([gap0 - 130, deck_y - 6, gap0 + 30, river_y + 20], start=0, end=95, fill=deck_col, width=4)
d.arc([gap1 - 30, deck_y - 6, gap1 + 130, river_y + 20], start=85, end=180, fill=deck_col, width=4)
# piers
for pier_x in [px0 + 165, px1 - 165]:
    d.rectangle([pier_x - 5, deck_y + 8, pier_x + 5, river_y], fill=deck_col)
# orange starburst at the break
bcx, bcy = 516, deck_y + 6
for i in range(8):
    ang = i * math.pi / 4
    d.line([(bcx, bcy), (bcx + 24 * math.cos(ang), bcy + 24 * math.sin(ang))],
           fill=ORANGE, width=4)
d.ellipse([bcx - 8, bcy - 8, bcx + 8, bcy + 8], fill=(255, 180, 40))
y = panel_y + panel_h + 4
y = rule(d, y, width=2)

# two-column row: Markets / Climate
f_kick = font(SANS_B, 26)
f_head = font(SERIF_B, 34)
f_small = font(SERIF, 28)
col_w = 452
y0 = y + 8
x = 40
d.text((x, y0), "MARKETS", font=f_kick, fill=RED)
y1 = draw_para(d, x, y0 + 32, col_w, "AI sell-off spreads", f_head, 38)
# big red figures with proportional down-bars
f_fig = font(SANS_B, 36)
fig_y = y1 + 2
d.text((x, fig_y), "NIKKEI \u22124.8%", font=f_fig, fill=RED)
d.rectangle([x, fig_y + 40, x + 260, fig_y + 52], fill=RED)
d.text((x, fig_y + 54), "S&P 500 \u22122.0%", font=f_fig, fill=RED)
d.rectangle([x, fig_y + 94, x + 108, fig_y + 106], fill=RED)
y1 = fig_y + 108
y1 = draw_para(
    d, x, y1, col_w,
    "AI valuation doubts grow after Anthropic's debut failed to lift tech shares.",
    f_small, 32)
d.line([(512, y0), (512, y1)], fill=GREY, width=2)
x = 532
d.text((x, y0), "CLIMATE", font=f_kick, fill=RED)
y2 = draw_para(d, x, y0 + 32, col_w, "COP31 draft drops fossil fuels", f_head, 38)
y2 = draw_para(
    d, x, y2 + 2, col_w,
    "Revised COP31 text in Antalya drops all mention of phasing out fossil "
    "fuels and a $120bn adaptation-finance target at the Friday deadline.",
    f_small, 32)
y = max(y1, y2) + 6
y = rule(d, y, width=2)

# three-column row
f_small3 = font(SERIF, 27)
col_w3 = 300
y0 = y + 8
cols = [
    ("POLAND", "Air alert lifted",
     "Poland lifts an air-threat warning, probes unknown objects near the Ukrainian border."),
    ("GAZA", "Ground operation ends",
     "Gazans return after Israel ends a rare ground operation in central Gaza."),
    ("SUMMIT", "Trump briefs Tokyo",
     "Trump briefs Japan's PM Takaichi on Shenzhen; White House press conference planned Friday."),
]
ys = []
for i, (kick, head, body) in enumerate(cols):
    x = 40 + i * 322
    d.text((x, y0), kick, font=f_kick, fill=RED)
    yy = draw_para(d, x, y0 + 32, col_w3, head, f_head, 36)
    yy = draw_para(d, x, yy + 2, col_w3, body, f_small3, 29)
    ys.append(yy)
    if i < 2:
        d.line([(40 + (i + 1) * 322 - 11, y0), (40 + (i + 1) * 322 - 11, yy)], fill=GREY, width=2)
y = max(ys) + 6
y = rule(d, y, width=2)

# also strip
f_also = font(SERIF_B, 24)
y = draw_para(
    d, 40, y + 8, 944,
    "ALSO \u2022 UK-EU youth mobility \u2022 Meta rethinks net-zero \u2022 Van Gogh $190.4m",
    f_also, 30)
y += 6
y = rule(d, y, width=2)

# footer
f_foot = font(SERIF_I, 24)
foot = "All stories from Friday 20 November 2026"
d.text(((W - d.textlength(foot, font=f_foot)) / 2, y + 6), foot, font=f_foot, fill=GREY)

print("final y:", y)
img.save("/home/hatch/workspace/makefun-entries/news-image-20261120/entry.png")
print("saved", img.size)
