#!/usr/bin/env python3
"""Draw the 18 November 2026 world-news infographic (1024x1024 PNG).

Every story was checked against live reporting on 18 November 2026
(AP, Reuters, BBC, CNA, NPR, India Today, Nvidia's own release):
  - Trump lands in Shenzhen; Xi greets him; Xi and Putin met that day
    ahead of Thursday's trilateral talks.
  - Iran attacks US bases in Kuwait and Bahrain after the US struck
    a missile site on Qeshm Island; a tanker was hit in Hormuz.
  - Ukraine strikes the Kerch Bridge a second day; a road span collapses.
  - Cyclone Akvan strengthens over the Bay of Bengal; landfall on the
    Andhra-Odisha coast is due 20 November.
  - Nvidia reports $115.8bn of revenue, up 103% year on year; China
    curbs H200 chip imports.
  - Mary Peltola wins Alaska's Senate seat; Democrats take a 56-44
    majority in the incoming Senate.

Layout is a newspaper front page: one masthead naming the day, then
six story cards across regions and fields, each with a short label
and a plain factual line. Nothing is invented, hyped or speculated.
Run: python3 generate_image.py  ->  writes entry.png beside this file.
"""
import math
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
PAPER = (251, 247, 237)
INK = (17, 24, 39)
RED = (178, 34, 34)
BLUE = (30, 64, 175)
GOLD = (180, 130, 29)

BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, width):
    """Wrap text to a pixel width, returning lines."""
    lines, line = [], ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if draw.textlength(trial, font=fnt) <= width:
            line = trial
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def draw_globe(d, cx, cy, r, colour):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=colour)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 255, 255), width=3)
    d.arc([cx - r, cy - r, cx + r, cy + r], 0, 360, fill=(255, 255, 255), width=2)
    d.ellipse([cx - r // 2, cy - r, cx + r // 2, cy + r], outline=(255, 255, 255), width=2)
    d.line([cx - r, cy, cx + r, cy], fill=(255, 255, 255), width=2)
    d.arc([cx - r, cy - r // 2, cx + r, cy + r // 2], 0, 360, fill=(255, 255, 255), width=2)


def draw_flame(d, cx, cy, r):
    pts = [
        (cx, cy - r), (cx + r * 0.55, cy - r * 0.2), (cx + r * 0.8, cy + r * 0.3),
        (cx + r * 0.4, cy + r * 0.6), (cx + r * 0.55, cy + r), (cx, cy + r * 0.7),
        (cx - r * 0.55, cy + r), (cx - r * 0.4, cy + r * 0.6),
        (cx - r * 0.8, cy + r * 0.3), (cx - r * 0.55, cy - r * 0.2),
    ]
    d.polygon(pts, fill=(220, 60, 30))
    d.polygon([(cx, cy - r * 0.3), (cx + r * 0.3, cy + r * 0.3),
               (cx, cy + r * 0.75), (cx - r * 0.3, cy + r * 0.3)], fill=(255, 200, 40))


def draw_bridge(d, x0, y0, x1, y1, colour):
    # Suspension bridge seen from the side: two towers, a deck, cables.
    mid_y = (y0 + y1) // 2
    d.line([x0, y1, x1, y1], fill=colour, width=6)
    for tx in (x0 + 8, x1 - 8):
        d.line([tx, y0 + 4, tx, y1], fill=colour, width=5)
    d.line([x0 + 8, y0 + 4, (x0 + x1) // 2, mid_y + 6], fill=colour, width=3)
    d.line([x1 - 8, y0 + 4, (x0 + x1) // 2, mid_y + 6], fill=colour, width=3)
    for fx in (0.3, 0.5, 0.7):
        x = x0 + (x1 - x0) * fx
        d.line([x, mid_y + 2, x, y1], fill=colour, width=3)
    # A broken gap in the deck, in red, where the span collapsed.
    gap = (x0 + x1) // 2
    d.line([gap - 12, y1, gap + 12, y1], fill=(220, 60, 30), width=7)


def draw_cyclone(d, cx, cy, r, colour):
    for i, frac in enumerate((1.0, 0.72, 0.45)):
        rr = r * frac
        d.arc([cx - rr, cy - rr, cx + rr, cy + rr], 20 + i * 40, 300 + i * 40,
              fill=colour, width=6)
    d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=colour)


def draw_chip(d, cx, cy, r, colour):
    d.rectangle([cx - r, cy - r, cx + r, cy + r], fill=colour)
    for i in range(3):
        off = -r // 2 + i * (r // 2)
        d.line([cx + off, cy - r - 10, cx + off, cy - r], fill=colour, width=5)
        d.line([cx + off, cy + r, cx + off, cy + r + 10], fill=colour, width=5)
        d.line([cx - r - 10, cy + off, cx - r, cy + off], fill=colour, width=5)
        d.line([cx + r, cy + off, cx + r + 10, cy + off], fill=colour, width=5)
    d.rectangle([cx - r // 2, cy - r // 2, cx + r // 2, cy + r // 2],
                outline=(255, 255, 255), width=3)


def draw_ballot(d, cx, cy, r, colour):
    d.rectangle([cx - r, cy - r * 0.7, cx + r, cy + r * 0.7], fill=colour)
    d.rectangle([cx - r * 0.45, cy - r * 0.7 - 12, cx + r * 0.45, cy - r * 0.7 + 4],
                fill=colour)
    d.line([cx - r * 0.55, cy, cx - r * 0.1, cy + r * 0.4, cx + r * 0.6, cy - r * 0.45],
           fill=(255, 255, 255), width=7, joint="curve")


ICONS = {
    "globe": lambda d, cx, cy, r: draw_globe(d, cx, cy, r, BLUE),
    "flame": lambda d, cx, cy, r: draw_flame(d, cx, cy, r),
    "bridge": lambda d, cx, cy, r: draw_bridge(d, cx - r, cy - r // 2, cx + r, cy + r // 2, (70, 70, 90)),
    "cyclone": lambda d, cx, cy, r: draw_cyclone(d, cx, cy, r, (13, 148, 136)),
    "chip": lambda d, cx, cy, r: draw_chip(d, cx, cy, r, (17, 24, 39)),
    "ballot": lambda d, cx, cy, r: draw_ballot(d, cx, cy, r, (124, 58, 237)),
}

STORIES = [
    ("CHINA  ·  DIPLOMACY", "TRUMP LANDS IN CHINA",
     "Xi greets him in Shenzhen. Xi and Putin met today; all three meet on Thursday.",
     "globe", BLUE),
    ("GULF  ·  WAR", "IRAN HITS US BASES",
     "Drones strike US bases in Kuwait and Bahrain after the US hit a missile site on Qeshm Island.",
     "flame", (220, 60, 30)),
    ("UKRAINE  ·  WAR", "KERCH BRIDGE HIT AGAIN",
     "Ukraine strikes the bridge a second day. Part of the road span collapses.",
     "bridge", (70, 70, 90)),
    ("INDIA  ·  WEATHER", "CYCLONE AKVAN NEARS",
     "Severe storm strengthens in the Bay of Bengal. Landfall on the Andhra-Odisha coast due 20 Nov.",
     "cyclone", (13, 148, 136)),
    ("TECH  ·  MARKETS", "NVIDIA DOUBLES REVENUE",
     "$115.8bn in the quarter, up 103%. China curbs imports of its H200 AI chips.",
     "chip", (17, 24, 39)),
    ("USA  ·  POLITICS", "SENATE FLIPS IN ALASKA",
     "Peltola beats Sullivan. Democrats take a 56-44 majority in the incoming Senate.",
     "ballot", (124, 58, 237)),
]


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # Masthead
    d.rectangle([0, 0, W, 168], fill=INK)
    d.text((512, 28), "WEDNESDAY", font=font(BOLD, 30), fill=(255, 255, 255), anchor="ma")
    d.text((512, 96), "18 NOVEMBER 2026", font=font(SERIF, 68), fill=(255, 255, 255), anchor="ma")
    d.rectangle([0, 168, W, 176], fill=RED)
    d.text((512, 206), "THE WORLD IN ONE DAY  —  SIX STORIES THAT SUM UP THE NEWS",
           font=font(BOLD, 22), fill=INK, anchor="ma")

    # Story cards: 2 columns x 3 rows
    margin, gap = 28, 20
    card_w = (W - 2 * margin - gap) // 2
    card_h = 228
    top = 248
    for i, (kicker, headline, body, icon, colour) in enumerate(STORIES):
        row, col = divmod(i, 2)
        x0 = margin + col * (card_w + gap)
        y0 = top + row * (card_h + gap)
        x1, y1 = x0 + card_w, y0 + card_h
        d.rectangle([x0, y0, x1, y1], fill=(255, 255, 255), outline=INK, width=2)
        d.rectangle([x0, y0, x0 + 10, y1], fill=colour)
        # Icon in a coloured disc
        cx, cy = x0 + 62, y0 + 58
        d.ellipse([cx - 34, cy - 34, cx + 34, cy + 34], fill=(240, 240, 235), outline=colour, width=3)
        ICONS[icon](d, cx, cy, 24)
        # Kicker + headline + body
        tx = x0 + 116
        d.text((tx, y0 + 18), kicker, font=font(BOLD, 18), fill=RED)
        for j, line in enumerate(wrap(d, headline, font(BOLD, 27), card_w - 136)):
            d.text((tx, y0 + 48 + j * 34), line, font=font(BOLD, 27), fill=INK)
        body_lines = wrap(d, body, font(REG, 20), card_w - 36)
        for j, line in enumerate(body_lines[:3]):
            d.text((x0 + 22, y0 + 128 + j * 28), line, font=font(REG, 20), fill=(55, 65, 81))

    # Footer
    fy = top + 3 * card_h + 2 * gap + 14
    d.line([margin, fy, W - margin, fy], fill=INK, width=2)
    d.text((512, fy + 12), "Sources: AP, Reuters, BBC, CNA, NPR, India Today, Nvidia  ·  18 November 2026",
           font=font(REG, 18), fill=(55, 65, 81), anchor="ma")

    out = Path(__file__).resolve().parent / "entry.png"
    img.save(out, format="PNG", optimize=True)
    print(f"wrote {out} {out.stat().st_size} bytes {img.size}")


if __name__ == "__main__":
    main()
