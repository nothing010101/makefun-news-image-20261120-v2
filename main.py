#!/usr/bin/env python3
"""news-image-20261120 v2: a DENSE front page of 20 November 2026's world news.

36 stories from 7 regions on one 1024x1024 newspaper front page: one lead
(the first-ever Trump-Xi-Putin trilateral summit in Shenzhen) and a 4x9 grid
of 35 more, plus a "by the numbers" box. Every story was verified against
real reporting dated Friday 20 November 2026 (Open Chronicle 20 Nov brief,
Standard Topic world archive, Medium 20 Nov strategic brief, IANS Live,
UN News 20 Nov, Russell Record daily headlines, Virginia Times Nov 20 recap,
OneTurn, Nepal Times). Pure Python 3.13 stdlib (zlib, struct, os). No
network, deterministic: two runs write byte-identical output. Writes
entry.png to $MAKEFUN_OUTPUT_DIR or /output.
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 234)
INK = (26, 26, 26)
NAVY = (20, 33, 61)
GOLD = (201, 162, 39)
WHITE = (255, 255, 255)
RED = (222, 41, 16)
DARKRED = (150, 40, 30)
BLUE = (0, 87, 183)
YELLOW = (255, 215, 0)
SEA = (18, 92, 140)
TEAL = (14, 116, 120)
GREEN = (34, 139, 34)
ORANGE = (230, 126, 34)
GREY = (90, 90, 96)
PURPLE = (90, 50, 130)


# ---------------------------------------------------------------- canvas
class Canvas:
    """RGB canvas backed by one flat bytearray; encodes its own PNG."""

    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bytes(bg) * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def hline(self, x0, x1, y, c):
        if y < 0 or y >= self.h:
            return
        x0, x1 = max(0, x0), min(self.w - 1, x1)
        for x in range(x0, x1 + 1):
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def vline(self, x, y0, y1, c):
        if x < 0 or x >= self.w:
            return
        for y in range(max(0, y0), min(self.h - 1, y1) + 1):
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def fill_rect(self, x, y, w, h, c):
        for yy in range(max(0, y), min(self.h, y + h)):
            self.hline(x, x + w - 1, yy, c)

    def rect(self, x, y, w, h, c, t=1):
        for k in range(t):
            self.hline(x, x + w - 1, y + k, c)
            self.hline(x, x + w - 1, y + h - 1 - k, c)
            self.vline(x + k, y, y + h - 1, c)
            self.vline(x + w - 1 - k, y, y + h - 1, c)

    def line(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def fill_poly(self, pts, c):
        ys = [p[1] for p in pts]
        for y in range(max(0, int(min(ys))), min(self.h - 1, int(max(ys))) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x1, y1 = pts[i]
                x2, y2 = pts[(i + 1) % n]
                if (y1 <= y < y2) or (y2 <= y < y1):
                    xs.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.hline(int(xs[i]), int(xs[i + 1]), y, c)

    def star(self, cx, cy, r_out, r_in, c):
        import math
        pts = []
        for i in range(10):
            r = r_out if i % 2 == 0 else r_in
            a = math.radians(-90 + i * 36)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        self.fill_poly(pts, c)

    def to_png(self):
        raw = b"".join(b"\x00" + bytes(self.px[y * self.w * 3:(y + 1) * self.w * 3])
                       for y in range(self.h))
        comp = zlib.compress(raw, 9)

        def chunk(typ, data):
            c = struct.pack(">I", len(data)) + typ + data
            return c + struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)

        ihdr = struct.pack(">IIBBBBB", self.w, self.h, 8, 2, 0, 0, 0)
        return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
                + chunk(b"IDAT", comp) + chunk(b"IEND", b""))

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 characters, '#' = on. Capitals, digits, punctuation.
FONT = {
    "A": [" ### ", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"],
    "B": ["#### ", "#   #", "#   #", "#### ", "#   #", "#   #", "#### "],
    "C": [" ####", "#    ", "#    ", "#    ", "#    ", "#    ", " ####"],
    "D": ["#### ", "#   #", "#   #", "#   #", "#   #", "#   #", "#### "],
    "E": ["#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#####"],
    "F": ["#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#    "],
    "G": [" ####", "#    ", "#    ", "# ###", "#   #", "#   #", " ### "],
    "H": ["#   #", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"],
    "I": ["#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "#####"],
    "J": ["  ###", "    #", "    #", "    #", "    #", "#   #", " ### "],
    "K": ["#   #", "#  # ", "# #  ", "##   ", "# #  ", "#  # ", "#   #"],
    "L": ["#    ", "#    ", "#    ", "#    ", "#    ", "#    ", "#####"],
    "M": ["#   #", "## ##", "# # #", "# # #", "#   #", "#   #", "#   #"],
    "N": ["#   #", "##  #", "# # #", "#  ##", "#   #", "#   #", "#   #"],
    "O": [" ### ", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "],
    "P": ["#### ", "#   #", "#   #", "#### ", "#    ", "#    ", "#    "],
    "Q": [" ### ", "#   #", "#   #", "#   #", "# # #", "#  # ", " ## #"],
    "R": ["#### ", "#   #", "#   #", "#### ", "# #  ", "#  # ", "#   #"],
    "S": [" ####", "#    ", "#    ", " ### ", "    #", "    #", "#### "],
    "T": ["#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  "],
    "U": ["#   #", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "],
    "V": ["#   #", "#   #", "#   #", "#   #", "#   #", " # # ", "  #  "],
    "W": ["#   #", "#   #", "#   #", "# # #", "# # #", "## ##", "#   #"],
    "X": ["#   #", "#   #", " # # ", "  #  ", " # # ", "#   #", "#   #"],
    "Y": ["#   #", "#   #", " # # ", "  #  ", "  #  ", "  #  ", "  #  "],
    "Z": ["#####", "    #", "   # ", "  #  ", " #   ", "#    ", "#####"],
    "0": [" ### ", "#  ##", "# # #", "##  #", "#   #", "#   #", " ### "],
    "1": ["  #  ", " ##  ", "  #  ", "  #  ", "  #  ", "  #  ", " ### "],
    "2": [" ### ", "#   #", "    #", "   # ", "  #  ", " #   ", "#####"],
    "3": ["#### ", "    #", "    #", " ### ", "    #", "    #", "#### "],
    "4": ["   # ", "  ## ", " # # ", "#  # ", "#####", "   # ", "   # "],
    "5": ["#####", "#    ", "#### ", "    #", "    #", "#   #", " ### "],
    "6": [" ### ", "#    ", "#    ", "#### ", "#   #", "#   #", " ### "],
    "7": ["#####", "    #", "   # ", "  #  ", "  #  ", "  #  ", "  #  "],
    "8": [" ### ", "#   #", "#   #", " ### ", "#   #", "#   #", " ### "],
    "9": [" ### ", "#   #", "#   #", " ####", "    #", "    #", " ### "],
    " ": ["     ", "     ", "     ", "     ", "     ", "     ", "     "],
    ".": ["     ", "     ", "     ", "     ", "     ", "     ", "  #  "],
    ",": ["     ", "     ", "     ", "     ", "     ", "  #  ", " #   "],
    ":": ["     ", "  #  ", "     ", "     ", "     ", "  #  ", "     "],
    ";": ["     ", "  #  ", "     ", "     ", "     ", "  #  ", " #   "],
    "'": ["  #  ", "  #  ", " #   ", "     ", "     ", "     ", "     "],
    "-": ["     ", "     ", "     ", " ### ", "     ", "     ", "     "],
    "/": ["    #", "    #", "   # ", "  #  ", " #   ", "#    ", "#    "],
    "!": ["  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "     ", "  #  "],
    "?": [" ### ", "#   #", "    #", "   # ", "  #  ", "     ", "  #  "],
    "(": ["   # ", "  #  ", " #   ", " #   ", " #   ", "  #  ", "   # "],
    ")": [" #   ", "  #  ", "   # ", "   # ", "   # ", "  #  ", " #   "],
    "%": ["#   #", "#  # ", "   # ", "  #  ", " #   ", "#  # ", "#   #"],
    "+": ["     ", "  #  ", "  #  ", " ### ", "  #  ", "  #  ", "     "],
    "$": ["  #  ", " ####", "# # #", " ### ", "# # #", " ####", "  #  "],
}


def text_width(s, scale):
    return len(s) * 6 * scale - scale if s else 0


def draw_text(cv, x, y, s, scale, color, align="left"):
    s = s.upper()  # the bitmap font only carries capitals, digits, punctuation
    if align == "center":
        x -= text_width(s, scale) // 2
    elif align == "right":
        x -= text_width(s, scale)
    for ch in s:
        g = FONT.get(ch, FONT[" "])
        for r in range(7):
            row = g[r]
            for c in range(5):
                if row[c] == "#":
                    cv.fill_rect(x + c * scale, y + r * scale, scale, scale, color)
        x += 6 * scale


def wrap_text(s, max_w, scale):
    """Greedy word wrap; returns list of lines fitting max_w pixels."""
    lines, cur = [], ""
    for word in s.split(" "):
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines

# ---------------------------------------------------------------- stories
# (region, headline, summary, accent). Headlines wrap to at most 2 lines at
# scale 2 in a 235 px column; summaries to at most 2 lines at scale 1.
STORIES = [
    ("EUROPE", "KYIV HIT, MISSILES LAND IN POLAND",
     "400 drones, 110 missiles hit Kyiv. Eight killed.", RED),
    ("ASIA", "ICJ: MYANMAR GUILTY OF GENOCIDE",
     "World court: Myanmar committed genocide on Rohingya.", NAVY),
    ("MARKETS", "ANTHROPIC IPO SOARS, SHARES SLIDE",
     "Record IPO tops $2tn; AI sell-off hits world stocks.", PURPLE),
    ("EUROPE", "UK AND EU SIGN NEW DEAL",
     "Food trade, carbon market, youth mobility agreed.", BLUE),
    ("S. ASIA", "CYCLONE AKVAN HITS EAST INDIA",
     "Landfall near Gopalpur, winds 90 km/h; 300,000 out.", SEA),
    ("EUROPE", "COP31 ENDS IN DEADLOCK",
     "Final day in Antalya: draft drops fossil fuels.", GREEN),
    ("MIDEAST", "HOUTHI STRIKE HITS RIYADH TOWER",
     "Strike hits PIF Tower, home of the Saudi wealth fund.", ORANGE),
    ("MIDEAST", "TANKER ON FIRE IN HORMUZ",
     "Oil tanker ablaze in the strait amid US blockade.", TEAL),
    ("AFRICA", "KENYA COUNTS DOWN TO EBOLA-FREE",
     "42-day countdown to an Ebola-free declaration.", GREEN),
    ("N. AMERICA", "US SENATE PASSES ENERGY BILL",
     "Energy-permitting bill passes 62-33; now to House.", NAVY),
    ("S. ASIA", "TOXIC LIQUOR KILLS 11 IN MANIPUR",
     "Tainted liquor kills 11, sickens 180+ in Manipur.", DARKRED),
    ("EUROPE", "UKRAINE STRIKES KERCH BRIDGE",
     "Neptune missiles damage road and rail links.", GREY),
    ("LATIN AM.", "HAITI POLICE KILL 34 GANG SUSPECTS",
     "Raid in Martissant kills 34 suspected gang members.", RED),
    ("EUROPE", "MERZ REJECTS A NEW YALTA DEAL",
     "Germany: no settlement on Europe without Europe.", NAVY),
    ("ASIA", "MYANMAR CALLS ICJ RULING 'UNFAIR'",
     "Myanmar rejects world court's genocide ruling.", NAVY),
    ("N. AMERICA", "SHUTDOWN RISK OVER IRAN WAR FUNDS",
     "Congress risks pre-Christmas shutdown over funding.", NAVY),
    ("MIDEAST", "SAUDI DEFENCES DOWN HOUTHI MISSILE",
     "Saudi air defences down a missile and five drones.", ORANGE),
    ("N. AMERICA", "TRUMP THREATENS DATA-CENTRE TAX",
     "Firms building AI centres abroad face a huge tax.", PURPLE),
    ("N. AMERICA", "WHITE HOUSE NAMES NEW CYBER CHIEF",
     "Kirsten Davies named acting national cyber director.", NAVY),
    ("LATIN AM.", "CHINESE CHEMICALS FUEL CARTEL: US",
     "US embassy: Chinese precursors fed Sinaloa cartel.", DARKRED),
    ("N. AMERICA", "CALIFORNIA SUBPOENAS NVIDIA",
     "State probes Nvidia over China risks, disclosures.", PURPLE),
    ("N. AMERICA", "VISA, MASTERCARD HIT BY BREACH",
     "Vendors breached; payment networks unaffected.", PURPLE),
    ("N. AMERICA", "ICE PAID MILLIONS FOR EMPTY BEDS",
     "Audit: ICE paid millions for unused detention beds.", NAVY),
    ("N. AMERICA", "DEMOCRATS: END OLD DEPORTATIONS",
     "Bid to end decades-old deportation orders.", NAVY),
    ("ASIA", "US SANCTIONS SCAM ENABLERS",
     "Sanctions hit Cambodia, Myanmar scam networks.", NAVY),
    ("S. ASIA", "INDIA DRIVES ENERGY GROWTH: IEA",
     "India among top drivers of energy growth in crisis.", SEA),
    ("S. ASIA", "INDIA TREASURY HOLDINGS $228BN",
     "India's US Treasury holdings rise to $228.2bn.", PURPLE),
    ("MIDEAST", "TREASURY SANCTIONS IRAN OIL RING",
     "Four sanctioned over alleged Iranian oil network.", TEAL),
    ("N. AMERICA", "SEC TO TAKE OVER AUDIT TRAIL",
     "SEC proposes direct control of audit trail.", NAVY),
    ("N. AMERICA", "JUDGE TO BLOCK TRUMP'S 250-FT ARCH",
     "Judge says she will block the 250-foot arch.", NAVY),
    ("N. AMERICA", "TEXANS ROUT COLTS 26-3",
     "Stroud throws three TDs as Texans rout Colts.", RED),
    ("ASIA", "AFGHAN CURBS BLOCK WOMEN'S CARE",
     "Curbs stop women seeking vital medical help: UN.", NAVY),
    ("S. ASIA", "NEPAL GETS $2M GRANT, $107M LOAN",
     "China grant, IMF loan for flood relief and recovery.", GREEN),
    ("S. ASIA", "MODI TO OPEN SCO DIALOGUE FORUM",
     "PM Modi to open first SCO civilisational forum.", NAVY),
    ("N. AMERICA", "ASIA TRIP SECURED $17BN: WHITE HOUSE",
     "White House: Asia trip secured $17bn in deals.", PURPLE),
]

LEAD_HEADLINE = ["TRUMP, XI AND PUTIN MEET", "IN SHENZHEN"]
LEAD_SUMMARY = ("First-ever three-way summit. Joint declaration: a nuclear "
                "war cannot be won and must never be fought.")
LEAD_DATELINE = "SHENZHEN, CHINA - APEC SIDELINES - 90-MINUTE MEETING"

NUMBERS_LINES = [
    "400+ DRONES, 110 MISSILES",
    "$2TN IPO, S AND P -3.7%",
    "300,000 EVACUATED",
    "62-33 SENATE VOTE",
    "42 DAYS TO EBOLA-FREE",
]


def draw_lead_flags(cv, x, y):
    """Three flags side by side: USA, China, Russia. Each 96x64."""
    cv.fill_rect(x, y, 96, 64, WHITE)
    for i in range(7):
        cv.fill_rect(x, y + i * 9, 96, 5, RED)
    cv.fill_rect(x, y, 38, 36, BLUE)
    for r in range(3):
        for c in range(4):
            cv.fill_rect(x + 5 + c * 9, y + 5 + r * 11, 3, 3, WHITE)
    cv.rect(x, y, 96, 64, INK, 1)
    cx = x + 104
    cv.fill_rect(cx, y, 96, 64, RED)
    cv.star(cx + 20, y + 20, 11, 5, YELLOW)
    for sx, sy in ((40, 10), (48, 18), (48, 28), (40, 36)):
        cv.star(cx + sx, y + sy, 4, 2, YELLOW)
    cv.rect(cx, y, 96, 64, INK, 1)
    rx = x + 208
    cv.fill_rect(rx, y, 96, 21, WHITE)
    cv.fill_rect(rx, y + 21, 96, 22, BLUE)
    cv.fill_rect(rx, y + 43, 96, 21, RED)
    cv.rect(rx, y, 96, 64, INK, 1)


# ---------------------------------------------------------------- layout
def panel(cv, x, y, w, h, accent):
    cv.fill_rect(x, y, w, h, WHITE)
    cv.fill_rect(x, y, w, 4, accent)
    cv.rect(x, y, w, h, INK, 1)


def grid_cell(cv, x, y, w, h, story):
    region, headline, summary, accent = story
    panel(cv, x, y, w, h, accent)
    tx = x + 8
    draw_text(cv, tx, y + 9, region, 1, accent)
    hl = wrap_text(headline, w - 16, 2)[:2]
    for i, ln in enumerate(hl):
        draw_text(cv, tx, y + 21 + i * 16, ln, 2, INK)
    sl = wrap_text(summary, w - 16, 1)[:2]
    for i, ln in enumerate(sl):
        draw_text(cv, tx, y + 53 + i * 9, ln, 1, INK)


def numbers_cell(cv, x, y, w, h):
    panel(cv, x, y, w, h, GOLD)
    draw_text(cv, x + 8, y + 9, "BY THE NUMBERS", 1, GOLD)
    for i, ln in enumerate(NUMBERS_LINES):
        draw_text(cv, x + 8, y + 22 + i * 9, ln, 1, INK)


def main():
    cv = Canvas(W, H, PAPER)

    # masthead
    cv.fill_rect(0, 0, W, 88, NAVY)
    draw_text(cv, W // 2, 12, "THE WORLD IN ONE DAY", 5, WHITE, "center")
    draw_text(cv, W // 2, 56,
              "FRIDAY 20 NOVEMBER 2026 - 36 STORIES, 7 REGIONS",
              2, GOLD, "center")
    cv.fill_rect(0, 88, W, 4, GOLD)

    # lead story: the Shenzhen trilateral
    panel(cv, 8, 92, 1008, 170, GOLD)
    draw_lead_flags(cv, 20, 104)
    draw_text(cv, 20 + 152, 178, "USA - CHINA - RUSSIA", 1, INK, "center")
    draw_text(cv, 336, 100, LEAD_HEADLINE[0], 4, INK)
    draw_text(cv, 336, 132, LEAD_HEADLINE[1], 4, INK)
    for i, ln in enumerate(wrap_text(LEAD_SUMMARY, 668, 2)[:2]):
        draw_text(cv, 336, 168 + i * 16, ln, 2, INK)
    draw_text(cv, 336, 224, LEAD_DATELINE, 1, GREY)

    # 4x9 dense grid: 35 stories + 1 numbers box
    cols, rows = 4, 9
    cw, chh, gap = 247, 73, 6
    gx0, gy0 = 8, 268
    for idx in range(cols * rows):
        col, row = idx % cols, idx // cols
        gx = gx0 + col * (cw + gap)
        gy = gy0 + row * (chh + gap)
        if idx < len(STORIES):
            grid_cell(cv, gx, gy, cw, chh, STORIES[idx])
        else:
            numbers_cell(cv, gx, gy, cw, chh)

    # footer
    cv.fill_rect(0, 978, W, 46, NAVY)
    draw_text(cv, W // 2, 986,
              "SOURCES: WSJ - CNN - LE MONDE - UN NEWS - IMD - THE HINDU - REUTERS - AP - OPEN CHRONICLE",
              1, WHITE, "center")
    draw_text(cv, W // 2, 1002,
              "STANDARD TOPIC - IANS - ONETURN - MEDIUM - RUSSELL RECORD - VIRGINIA TIMES - NEPAL TIMES",
              1, WHITE, "center")

    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out, exist_ok=True)
    data = cv.to_png()
    with open(os.path.join(out, "entry.png"), "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
