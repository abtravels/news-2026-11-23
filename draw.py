"""Render entry.png for the make.fun news-image-20261123 bounty.

A newspaper front page summing up Monday 23 November 2026: masthead,
lead story (COP31 collapses), and five more stories plus an "also" box.
Every pixel is drawn with Pillow primitives and text; no photos, no
network, no randomness. Deterministic: the same inputs always produce
the same bytes.

Run:  python3 draw.py   (writes ./entry.png, 1024x1024)
"""

import math

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
M = 28  # side margin

PAPER = (248, 244, 232)
INK = (27, 27, 27)
MUTED = (74, 74, 68)
RED = (176, 30, 36)
BLUE = (47, 111, 178)
GREEN = (46, 125, 50)
ORANGE = (232, 100, 28)
TEAL = (16, 78, 84)
DARK = (20, 28, 38)
RULE = (138, 133, 120)
GOLD = (245, 166, 35)
SKY = (176, 216, 230)
SEA = (38, 110, 160)

FD = "/usr/share/fonts/truetype"
SERIF_B = FD + "/noto/NotoSerif-Bold.ttf"
SANS_B = FD + "/noto/NotoSans-Bold.ttf"
SANS_R = FD + "/noto/NotoSans-Regular.ttf"


def F(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, f, max_w):
    """Split text into lines that fit max_w at font f."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def block(d, x, y, lines, f, fill, leading):
    """Draw lines top-left anchored; return the y below the last line."""
    for line in lines:
        d.text((x, y), line, font=f, fill=fill)
        y += leading
    return y


def centre(d, cx, y, text, f, fill):
    d.text((cx, y), text, font=f, fill=fill, anchor="ma")


# ---- small pictograms, each drawn inside a square box (x, y, s) ----

def icon_warship(d, x, y, s):
    # a grey warship with a radar mast and a red warning triangle above
    d.line((x + 4, y + s - 14, x + s - 4, y + s - 14), fill=SEA, width=3)
    d.arc((x + 6, y + s - 22, x + s - 6, y + s - 6), start=0, end=180,
          fill=SEA, width=3)
    # hull
    d.polygon([(x + 6, y + 40), (x + s - 6, y + 40), (x + s - 12, y + 52),
               (x + 12, y + 52)], fill=DARK)
    # deck + mast
    d.rectangle((x + 16, y + 30, x + 36, y + 40), fill=DARK)
    d.line((x + 26, y + 30, x + 26, y + 18), fill=INK, width=3)
    d.ellipse((x + 22, y + 13, x + 30, y + 21), outline=INK, width=2)
    # warning triangle above the mast
    tx, ty = x + s // 2 + 12, y + 2
    d.polygon([(tx, ty), (tx + 9, ty + 15), (tx - 9, ty + 15)], fill=GOLD,
              outline=INK)
    d.line((tx, ty + 5, tx, ty + 10), fill=INK, width=2)
    d.point((tx, ty + 12), fill=INK)


def icon_drone_ship(d, x, y, s):
    # a cargo ship with a smoke plume and a small drone above it
    d.line((x + 4, y + s - 14, x + s - 4, y + s - 14), fill=SEA, width=3)
    d.arc((x + 6, y + s - 22, x + s - 6, y + s - 6), start=0, end=180,
          fill=SEA, width=3)
    # hull
    d.polygon([(x + 6, y + 38), (x + s - 6, y + 38), (x + s - 14, y + 52),
               (x + 14, y + 52)], fill=INK)
    # containers
    d.rectangle((x + 12, y + 26, x + 22, y + 38), fill=RED)
    d.rectangle((x + 24, y + 30, x + 34, y + 38), fill=BLUE)
    # smoke plume from the stern
    d.ellipse((x + 38, y + 12, x + 46, y + 20), fill=MUTED)
    d.ellipse((x + 42, y + 6, x + 52, y + 16), fill=MUTED)
    # drone: body + rotors
    cx, cy = x + 14, y + 8
    d.ellipse((cx - 5, cy - 3, cx + 5, cy + 3), fill=INK)
    for dx in (-10, 10):
        d.line((cx + dx - 6, cy - 6, cx + dx + 6, cy - 6), fill=INK, width=2)


def icon_rubble(d, x, y, s):
    # a cracked apartment block with a rubble pile and a rescue ladder
    # standing block, left half
    d.rectangle((x + 6, y + 8, x + 26, y + s - 16), fill=MUTED)
    # jagged crack down the middle
    d.line((x + 26, y + 8, x + 30, y + 18, x + 26, y + 28, x + 31, y + 38,
            x + 27, y + 48), fill=INK, width=2)
    # collapsed right half: tilted slab
    d.polygon([(x + 30, y + 22), (x + 50, y + 30), (x + 48, y + 38),
               (x + 28, y + 30)], fill=DARK)
    # windows on the standing block
    for wy in (14, 26, 38):
        d.rectangle((x + 11, y + wy, x + 19, y + wy + 6), fill=GOLD)
    # rubble pile at the base
    d.polygon([(x + 4, y + s - 8), (x + 16, y + s - 20), (x + 28, y + s - 12),
               (x + 40, y + s - 20), (x + 52, y + s - 8)], fill=INK)
    # ladder leaning on the rubble
    d.line((x + 40, y + s - 20, x + 50, y + s - 40), fill=RED, width=3)
    d.line((x + 44, y + s - 28, x + 48, y + s - 26), fill=RED, width=2)


def icon_capitol(d, x, y, s):
    # the US Capitol dome on a columned base
    cx = x + s // 2
    # dome
    d.pieslice((cx - 16, y + 6, cx + 16, y + 34), start=180, end=360,
               fill=(255, 255, 255), outline=INK, width=2)
    d.line((cx, y + 2, cx, y + 8), fill=INK, width=2)
    d.ellipse((cx - 2, y, cx + 2, y + 4), fill=INK)
    # drum + columns
    d.rectangle((cx - 16, y + 30, cx + 16, y + 34), fill=INK)
    for col in range(-12, 13, 8):
        d.line((cx + col, y + 36, cx + col, y + 48), fill=INK, width=3)
    # base steps
    d.rectangle((x + 6, y + 48, x + s - 6, y + 52), fill=INK)
    # ballot box in front, with a red check
    d.rectangle((cx - 22, y + 40, cx - 8, y + 52), fill=BLUE)
    d.line((cx - 20, y + 46, cx - 16, y + 50, cx - 10, y + 42), fill=RED,
           width=2)


def icon_ballot(d, x, y, s):
    # a ballot box with a red check, beside a small rising bar chart
    # --- ballot paper sliding into the slot, tilted slightly right ---
    d.polygon([(x + 12, y + 2), (x + 24, y + 4), (x + 22, y + 22),
               (x + 10, y + 20)], fill=(255, 255, 255), outline=INK)
    # two ruled lines on the paper
    d.line((x + 14, y + 8, x + 21, y + 9), fill=MUTED, width=1)
    d.line((x + 14, y + 12, x + 21, y + 13), fill=MUTED, width=1)
    # a small red tick on the paper itself
    d.line((x + 14, y + 16, x + 17, y + 19, x + 21, y + 14), fill=RED,
           width=2)
    # --- slot across the top of the box, drawn over the paper's foot ---
    d.rectangle((x + 6, y + 20, x + 30, y + 24), fill=INK)
    # --- box body with a lid lip and a gold seal dot ---
    d.rectangle((x + 4, y + 24, x + 32, y + 52), fill=BLUE)
    d.rectangle((x + 4, y + 24, x + 32, y + 52), outline=INK, width=2)
    d.line((x + 4, y + 28, x + 32, y + 28), fill=(255, 255, 255), width=1)
    d.ellipse((x + 26, y + 30, x + 30, y + 34), fill=GOLD, outline=INK)
    # --- big red check across the box front ---
    d.line((x + 9, y + 38, x + 15, y + 45, x + 27, y + 30), fill=RED,
           width=3)
    # --- small rising bar chart on the right, three bars ---
    base = y + 52
    # vertical axis and baseline for the chart
    d.line((x + 34, y + 20, x + 34, base), fill=MUTED, width=1)
    d.line((x + 36, base, x + s - 4, base), fill=INK, width=2)
    # shortest bar
    d.rectangle((x + 36, base - 10, x + 41, base), fill=BLUE)
    # middle bar
    d.rectangle((x + 43, base - 18, x + 48, base), fill=GREEN)
    # tallest bar, with an arrowhead on top
    d.rectangle((x + 50, base - 26, x + 55, base), fill=RED)
    d.polygon([(x + 50, base - 32), (x + 55, base - 32),
               (x + 52, base - 27)], fill=RED)
    # a faint tick under the shortest bar
    d.line((x + 36, base + 1, x + 41, base + 1), fill=MUTED, width=1)


def icon_castle(d, x, y, s):
    # Shuri Castle: tiered red roofs over white walls
    cx = x + s // 2
    # top roof
    d.polygon([(cx - 12, y + 10), (cx + 12, y + 10), (cx + 16, y + 18),
               (cx - 16, y + 18)], fill=RED)
    d.rectangle((cx - 9, y + 18, cx + 9, y + 26), fill=(255, 255, 255),
                outline=INK, width=2)
    # middle roof
    d.polygon([(cx - 18, y + 26), (cx + 18, y + 26), (cx + 23, y + 34),
               (cx - 23, y + 34)], fill=RED)
    d.rectangle((cx - 14, y + 34, cx + 14, y + 42), fill=(255, 255, 255),
                outline=INK, width=2)
    # base roof + walls
    d.polygon([(cx - 24, y + 42), (cx + 24, y + 42), (cx + 28, y + 50),
               (cx - 28, y + 50)], fill=RED)
    d.rectangle((cx - 19, y + 50, cx + 19, y + 56), fill=(255, 255, 255),
                outline=INK, width=2)
    # door
    d.rectangle((cx - 3, y + 50, cx + 3, y + 56), fill=INK)


def lead_art(d, x, y, w, h):
    """A climate summit scene: teal sky, sun, globe, flags, sea waves,
    and a red prohibition mark over a pact document — no deal."""
    d.rectangle((x, y, x + w, y + h), fill=TEAL)
    # sun, top left
    sx, sy, sr = x + 42, y + 30, 22
    for k in range(8):
        a = math.pi * k / 4
        d.line((x + sx + int(1.3 * sr * math.cos(a)),
                y + sy + int(1.3 * sr * math.sin(a)),
                x + sx + int(1.8 * sr * math.cos(a)),
                y + sy + int(1.8 * sr * math.sin(a))), fill=GOLD, width=3)
    d.ellipse((sx - sr, sy - sr, sx + sr, sy + sr), fill=GOLD)
    # globe, centre right
    gx, gy, gr = x + 215, y + 88, 58
    d.ellipse((gx - gr, gy - gr, gx + gr, gy + gr), fill=SKY,
              outline=(255, 255, 255), width=3)
    # land blobs
    d.ellipse((gx - 34, gy - 30, gx - 2, gy - 2), fill=GREEN)
    d.ellipse((gx + 4, gy + 6, gx + 34, gy + 34), fill=GREEN)
    d.ellipse((gx - 10, gy - 44, gx + 18, gy - 22), fill=GREEN)
    # meridians
    d.arc((gx - gr, gy - gr, gx + gr, gy + gr), start=90, end=270,
          fill=(255, 255, 255), width=2)
    d.line((gx, gy - gr, gx, gy + gr), fill=(255, 255, 255), width=2)
    d.line((gx - gr, gy, gx + gr, gy), fill=(255, 255, 255), width=2)
    # three small flags on poles, bottom left
    flag_cols = [(220, 20, 60), (47, 111, 178), (46, 125, 50)]
    for i, col in enumerate(flag_cols):
        fx = x + 24 + i * 34
        fy = y + h - 58
        d.line((fx, fy - 34, fx, fy), fill=(255, 255, 255), width=2)
        d.rectangle((fx, fy - 34, fx + 24, fy - 18), fill=col)
        d.rectangle((fx, fy - 34, fx + 24, fy - 26), fill=(255, 255, 255))
    # sea waves along the bottom, tiled to fit the panel exactly
    base = y + h
    step = w / 8
    for i in range(8):
        x0 = x + int(i * step)
        x1 = x + int((i + 1) * step)
        d.arc((x0, base - 22, x1, base + 6), start=180,
              end=360, fill=(255, 255, 255), width=3)
    # "no deal" mark, bottom right: a white pact sheet crossed out in red
    px, py = x + w - 84, base - 62
    d.rectangle((px, py, px + 34, py + 44), fill=(255, 255, 255),
                outline=INK, width=2)
    for ly in (py + 8, py + 16, py + 24):
        d.line((px + 6, ly, px + 28, ly), fill=MUTED, width=2)
    ccx, ccy, cr = px + 17, py + 22, 26
    d.ellipse((ccx - cr, ccy - cr, ccx + cr, ccy + cr), outline=RED, width=5)
    d.line((ccx - 18, ccy + 18, ccx + 18, ccy - 18), fill=RED, width=5)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---------- masthead ----------
    d.line((M, 16, W - M, 16), fill=INK, width=3)
    d.line((M, 22, W - M, 22), fill=INK, width=1)
    centre(d, W // 2, 30, "THE WORLD IN ONE DAY", F(SERIF_B, 60), INK)
    centre(d, W // 2, 96, "MONDAY, 23 NOVEMBER 2026", F(SANS_B, 25), INK)
    d.line((M, 126, W - M, 126), fill=INK, width=2)

    # ---------- lead story ----------
    lx, lw = M, 612
    ax, aw = 664, 332
    d.text((lx, 140), "LEAD STORY  ·  CLIMATE  ·  ANTALYA, TURKEY",
           font=F(SANS_B, 18), fill=RED)
    head = wrap(d, "COP31 COLLAPSES: NO DEAL AT LONGEST-EVER TALKS",
                F(SANS_B, 42), lw)
    assert len(head) <= 2, head
    y = block(d, lx, 164, head, F(SANS_B, 42), INK, 48)
    sub = wrap(d, "The EU and island nations reject a pact that never "
                  "mentions fossil fuels, ending the summit with no "
                  "agreement for the first time since 2009.",
               F(SANS_R, 20), lw)
    assert len(sub) <= 3, sub
    block(d, lx, y + 10, sub, F(SANS_R, 20), MUTED, 26)
    lead_art(d, ax, 158, aw, 186)

    # ---------- double rule ----------
    d.line((M, 362, W - M, 362), fill=INK, width=3)
    d.line((M, 368, W - M, 368), fill=INK, width=1)
    d.text((M, 382), "THE DAY IN BRIEF", font=F(SANS_B, 18), fill=INK)

    # ---------- grid: 5 stories + 1 "also" box ----------
    stories = [
        ("WASHINGTON  ·  TEHRAN",
         "TRUMP: IRAN STRIKES COULD RESUME AFTER NEW YEAR",
         "Trump says ships testing the US blockade will be sunk as "
         "Hormuz tanker attacks go on.", icon_warship),
        ("BENGHAZI, LIBYA",
         "RUSSIAN SHIP HIT BY DRONES AT BENGHAZI PORT",
         "Libya files a UN complaint after drone attacks on Russian "
         "and Maltese ships.", icon_drone_ship),
        ("DYMER, UKRAINE",
         "BOY PULLED ALIVE AFTER 14 HOURS AS DYMER TOLL HITS 11",
         "A seven-year-old is rescued from a collapsed block north "
         "of Kyiv as the search goes on.", icon_rubble),
        ("WASHINGTON",
         "DEMOCRATS TAKE 258 HOUSE SEATS, BIGGEST SINCE 1992",
         "A 44-seat midterm gain gives Democrats their strongest "
         "House showing in three decades.", icon_ballot),
        ("OKINAWA, JAPAN",
         "SHURI CASTLE REOPENS SEVEN YEARS AFTER FIRE",
         "The restored main hall opens to the public in Okinawa, "
         "seven years after the 2019 fire.", icon_castle),
    ]
    col_w, row_h = 314, 260
    xs = [M, M + col_w + 12, M + 2 * (col_w + 12)]
    ys = [410, 682]
    for i, (kicker, headline, sub, icon) in enumerate(stories):
        cx, cy = xs[i % 3], ys[i // 3]
        d.text((cx, cy), kicker, font=F(SANS_B, 16), fill=RED)
        icon(d, cx, cy + 26, 56)
        lines = wrap(d, headline, F(SANS_B, 23), col_w)
        assert len(lines) <= 3, (headline, lines)
        y = block(d, cx, cy + 92, lines, F(SANS_B, 23), INK, 28)
        slines = wrap(d, sub, F(SANS_R, 18), col_w)
        assert len(slines) <= 3, (headline, slines)
        block(d, cx, y + 6, slines, F(SANS_R, 18), MUTED, 22)

    # "also" cell, bottom right
    cx, cy = xs[2], ys[1]
    d.text((cx, cy), "ALSO ON MONDAY", font=F(SANS_B, 16), fill=RED)
    y = cy + 30
    d.rectangle((cx, y + 7, cx + 9, y + 16), fill=RED)
    lines = wrap(d, "EU and Indonesia sign a landmark trade pact after "
                    "a decade of talks", F(SANS_R, 18), col_w - 20)
    assert len(lines) <= 2, lines
    block(d, cx + 18, y, lines, F(SANS_R, 18), INK, 22)

    # column / row separators
    for vx in (xs[1] - 6, xs[2] - 6):
        d.line((vx, ys[0], vx, ys[1] + row_h), fill=RULE, width=1)
    d.line((M, ys[1] - 6, W - M, ys[1] - 6), fill=RULE, width=1)

    # ---------- footer ----------
    d.line((M, 962, W - M, 962), fill=INK, width=2)
    centre(d, W // 2, 974, "THE WORLD IN ONE DAY  ·  MONDAY 23 NOVEMBER 2026  ·  "
                            "SIX STORIES THAT DEFINED THE DAY",
           F(SANS_R, 15), MUTED)

    img.save("entry.png")
    print("saved entry.png", img.size)


if __name__ == "__main__":
    main()
