from PIL import Image, ImageDraw, ImageFont, ImageFilter
from datetime import datetime
import os, csv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
CONTENT_FILE = os.path.join(BASE_DIR, "content.csv")

POSTER_PATH = os.path.join(OUTPUT_DIR, "status_today.png")
CAPTION_PATH = os.path.join(OUTPUT_DIR, "caption_today.txt")

# Instagram / Facebook feed safe size: 4:5
W, H = 1080, 1350

PHONE = "6390063999"
WEBSITE = "www.metasolwservices.in"

THEME = {
    "top": (2, 12, 35),
    "mid": (5, 34, 82),
    "bottom": (2, 12, 34),
    "gold": (226, 181, 79),
    "gold2": (255, 224, 150),
    "card": (3, 24, 60),
    "card2": (5, 36, 88),
    "white": (255, 255, 255),
    "soft": (235, 241, 248),
}

RESAMPLE = Image.Resampling.LANCZOS if hasattr(Image, "Resampling") else Image.LANCZOS


def font(size, bold=False):
    paths = [
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\calibrib.ttf" if bold else r"C:\Windows\Fonts\calibri.ttf",
    ]
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def ts(draw, text, f):
    b = draw.textbbox((0, 0), str(text), font=f)
    return b[2] - b[0], b[3] - b[1]


def wrap(draw, text, f, max_w):
    lines = []
    for part in str(text).split("\n"):
        words = part.split()
        current = ""
        for w in words:
            test = (current + " " + w).strip()
            if ts(draw, test, f)[0] <= max_w:
                current = test
            else:
                if current:
                    lines.append(current)
                current = w
        if current:
            lines.append(current)
    return lines or [""]


def fit(draw, text, max_w, max_h, max_size, min_size, bold=True):
    for s in range(max_size, min_size - 1, -2):
        f = font(s, bold)
        lines = wrap(draw, text, f, max_w)
        gap = max(4, int(s * 0.16))
        hs = [ts(draw, ln, f)[1] for ln in lines]
        ws = [ts(draw, ln, f)[0] for ln in lines] or [0]
        total = sum(hs) + gap * (len(lines) - 1)
        if max(ws) <= max_w and total <= max_h:
            return f, lines, gap
    f = font(min_size, bold)
    return f, wrap(draw, text, f, max_w), 6


def draw_text(draw, text, box, max_size, min_size, fill, bold=True, align="left"):
    x1, y1, x2, y2 = box
    f, lines, gap = fit(draw, text, x2 - x1, y2 - y1, max_size, min_size, bold)
    hs = [ts(draw, ln, f)[1] for ln in lines]
    total = sum(hs) + gap * (len(lines) - 1)
    y = y1 + ((y2 - y1) - total) // 2

    for ln, h in zip(lines, hs):
        tw, _ = ts(draw, ln, f)
        if align == "center":
            x = x1 + ((x2 - x1) - tw) // 2
        elif align == "right":
            x = x2 - tw
        else:
            x = x1
        draw.text((x, y), ln, font=f, fill=fill)
        y += h + gap


def card(img, box, radius, fill, outline=None, width=2, shadow=True):
    x1, y1, x2, y2 = box

    if shadow:
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        sd = ImageDraw.Draw(sh)
        sd.rounded_rectangle((x1 + 8, y1 + 10, x2 + 8, y2 + 10), radius=radius, fill=(0, 0, 0, 90))
        sh = sh.filter(ImageFilter.GaussianBlur(13))
        img.alpha_composite(sh)

    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)
    img.alpha_composite(layer)


def bg():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    d = ImageDraw.Draw(img)

    for y in range(H):
        t = y / (H - 1)
        if t < 0.55:
            p = t / 0.55
            a, b = THEME["top"], THEME["mid"]
        else:
            p = (t - 0.55) / 0.45
            a, b = THEME["mid"], THEME["bottom"]

        c = tuple(int(a[i] * (1 - p) + b[i] * p) for i in range(3))
        d.line((0, y, W, y), fill=(*c, 255))

    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((690, 80, 1240, 560), fill=(*THEME["gold"], 65))
    gd.ellipse((-260, 820, 520, 1480), fill=(0, 170, 170, 24))
    gd.ellipse((420, 300, 1220, 950), fill=(40, 80, 180, 35))
    glow = glow.filter(ImageFilter.GaussianBlur(34))
    img.alpha_composite(glow)

    pat = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pat)
    for i in range(-H, W, 78):
        pd.line((i, 0, i + H, H), fill=(255, 255, 255, 12), width=2)

    for r in range(230, 560, 48):
        pd.arc((800 - r, 210 - r, 800 + r, 210 + r), 300, 60, fill=(*THEME["gold"], 42), width=2)

    img.alpha_composite(pat)
    return img


def load_content():
    if os.path.exists(CONTENT_FILE):
        with open(CONTENT_FILE, "r", encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))
            if rows:
                return rows[0]

    return {
        "category": "AUDIT REPORT",
        "title": "Fleet audit report ke liye connect karein",
        "subtitle": "Fast checking • Clean report • Professional support",
        "cta": "Audit Report Support",
        "point1": "RC / Insurance Audit",
        "point2": "Fitness / Permit Review",
        "point3": "Clean Risk Summary",
        "bullet1": "RC / Insurance check",
        "bullet2": "Fitness / Permit review",
        "bullet3": "Audit report guidance",
    }


def logo_paths():
    return [
        os.path.join(ASSETS_DIR, "logo.png"),
        os.path.join(ASSETS_DIR, "logo.jpg"),
        os.path.join(ASSETS_DIR, "metasolw_logo.png"),
        os.path.join(ASSETS_DIR, "metasolw_logo.jpg"),
    ]


def draw_logo(img):
    d = ImageDraw.Draw(img)
    cx, cy = 96, 85
    gold = (*THEME["gold"], 255)
    gold2 = (*THEME["gold2"], 255)

    d.ellipse((cx - 56, cy - 56, cx + 56, cy + 56), fill=(3, 22, 52, 255), outline=gold2, width=4)
    d.ellipse((cx - 47, cy - 47, cx + 47, cy + 47), outline=gold, width=2)

    for p in logo_paths():
        if os.path.exists(p):
            try:
                lg = Image.open(p).convert("RGBA")
                lg.thumbnail((96, 96), RESAMPLE)
                img.alpha_composite(lg, (cx - lg.width // 2, cy - lg.height // 2))
                return True
            except Exception:
                pass

    f = font(24, True)
    tw, th = ts(d, "MS", f)
    d.text((cx - tw / 2, cy - th / 2), "MS", font=f, fill=gold2)
    return False


def audit_visual(img, box):
    x1, y1, x2, y2 = box
    gold = (*THEME["gold"], 255)
    gold2 = (*THEME["gold2"], 255)

    card(img, box, 28, (*THEME["card2"], 235), (*THEME["gold"], 150), 2, True)
    d = ImageDraw.Draw(img)

    draw_text(d, "AUDIT REPORT", (x1 + 24, y1 + 18, x2 - 24, y1 + 54), 24, 15, gold2, True, "center")

    px1, py1 = x1 + 38, y1 + 68
    px2, py2 = x2 - 38, y2 - 30

    d.rounded_rectangle((px1, py1, px2, py2), radius=20, fill=(246, 249, 255, 245), outline=gold2, width=3)
    d.polygon([(px2 - 48, py1), (px2, py1 + 48), (px2, py1)], fill=(214, 224, 238, 255))
    d.line((px2 - 48, py1, px2, py1 + 48), fill=(175, 187, 203), width=2)

    d.rounded_rectangle((px1 + 22, py1 + 24, px2 - 22, py1 + 68), radius=12, fill=(5, 31, 73, 255))
    draw_text(d, "FLEET CHECK", (px1 + 30, py1 + 30, px2 - 30, py1 + 62), 18, 12, gold2, True, "center")

    items = ["RC / INSURANCE", "FITNESS STATUS", "PERMIT REVIEW"]
    yy = py1 + 92

    for item in items:
        d.rounded_rectangle((px1 + 22, yy, px2 - 22, yy + 42), radius=11, fill=(236, 242, 250, 255), outline=(220, 226, 236, 255), width=1)
        d.ellipse((px1 + 36, yy + 11, px1 + 60, yy + 35), fill=(7, 42, 96, 255))
        d.line((px1 + 42, yy + 24, px1 + 50, yy + 32, px1 + 62, yy + 14), fill=gold, width=4)
        draw_text(d, item, (px1 + 74, yy + 6, px2 - 30, yy + 36), 14, 10, (8, 24, 48, 255), True, "left")
        yy += 54


def service_chip(draw, box, text):
    x1, y1, x2, y2 = box
    gold = (*THEME["gold"], 255)

    draw.rounded_rectangle(box, radius=(y2 - y1) // 2, fill=gold, outline=(255, 255, 255, 120), width=2)
    draw_text(draw, text, (x1 + 25, y1 + 8, x2 - 25, y2 - 8), 30, 18, (8, 24, 48, 255), True, "center")


def icon(draw, cx, cy, kind):
    gold2 = (*THEME["gold2"], 255)
    draw.ellipse((cx - 34, cy - 34, cx + 34, cy + 34), outline=gold2, width=3, fill=(7, 36, 86, 255))

    if kind == "doc":
        draw.rectangle((cx - 15, cy - 22, cx + 15, cy + 22), outline=gold2, width=3)
        draw.line((cx - 10, cy + 5, cx - 2, cy + 14, cx + 16, cy - 13), fill=gold2, width=4)
    elif kind == "status":
        draw.line((cx - 20, cy - 5, cx - 7, cy + 10, cx + 22, cy - 20), fill=gold2, width=5)
        draw.arc((cx - 26, cy - 26, cx + 26, cy + 26), 20, 330, fill=gold2, width=3)
    else:
        f = font(30, True)
        tw, th = ts(draw, "!", f)
        draw.text((cx - tw / 2, cy - th / 2 - 2), "!", font=f, fill=gold2)


def make_caption(c):
    tags = "#MetaSolw #MetaSolwServices #EverythingSolved #AuditReport #FleetAudit #VehicleAudit #DocumentCheck #InsuranceCheck #FitnessCertificate #PermitCheck #Kanpur #UttarPradesh #India"

    return f"""{c['title']}

✅ {c['cta']}
✅ {c['point1']}
✅ {c['point2']}
✅ {c['point3']}

Direct support chahiye? Aaj hi connect karein.
📞 WhatsApp: {PHONE}
🌐 {WEBSITE}
📍 Kanpur, Uttar Pradesh

{tags}"""


def make_poster():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    c = load_content()
    gold = (*THEME["gold"], 255)
    gold2 = (*THEME["gold2"], 255)
    card_col = (*THEME["card"], 238)

    img = bg()
    d = ImageDraw.Draw(img)

    d.rounded_rectangle((34, 34, W - 34, H - 34), radius=44, outline=(255, 255, 255, 180), width=3)
    d.rounded_rectangle((52, 52, W - 52, H - 52), radius=34, outline=(*THEME["gold"], 130), width=2)

    logo_ok = draw_logo(img)
    d = ImageDraw.Draw(img)

    draw_text(d, "METASOLW SERVICES", (180, 45, 930, 105), 52, 34, (255, 255, 255, 255), True, "left")
    draw_text(d, "Everything Solved • Direct Company Platform", (182, 110, 900, 145), 22, 14, gold2, False, "left")

    service_chip(d, (60, 175, 360, 240), "AUDIT REPORT")

    d.rounded_rectangle((385, 178, 600, 238), radius=30, fill=card_col, outline=gold, width=2)
    draw_text(d, datetime.now().strftime("%d %b %Y"), (405, 187, 580, 228), 21, 14, (255, 255, 255, 255), True, "center")

    hero_y1, hero_y2 = 275, 600
    card(img, (60, hero_y1, 1020, hero_y2), 30, card_col, (*THEME["gold"], 145), 2, True)
    d = ImageDraw.Draw(img)

    draw_text(d, c["title"], (100, hero_y1 + 34, 585, hero_y1 + 160), 44, 30, (255, 255, 255, 255), True, "left")

    d.rounded_rectangle((100, hero_y1 + 185, 505, hero_y1 + 255), radius=35, fill=gold, outline=(255, 255, 255, 120), width=2)
    draw_text(d, c["cta"], (130, hero_y1 + 198, 475, hero_y1 + 245), 27, 17, (8, 24, 48, 255), True, "center")

    draw_text(d, c["subtitle"], (100, hero_y1 + 268, 585, hero_y1 + 304), 20, 13, (235, 241, 248, 255), False, "left")

    audit_visual(img, (635, 305, 965, 570))

    band_y = 630
    card(img, (60, band_y, 1020, band_y + 75), 18, gold, (255, 255, 255, 110), 2, True)
    d = ImageDraw.Draw(img)
    draw_text(d, "PLATFORM BY METASOLW SERVICES", (100, band_y + 12, 980, band_y + 62), 33, 22, (8, 23, 48, 255), True, "center")

    feature_y = 735
    gap = 26
    bw = (960 - 2 * gap) // 3
    xs = [60, 60 + bw + gap, 60 + 2 * (bw + gap)]

    features = [
        ("DOCUMENT", c["point1"], "doc"),
        ("STATUS", c["point2"], "status"),
        ("RISK", c["point3"], "risk"),
    ]

    for i, (title, body, kind) in enumerate(features):
        x = xs[i]
        card(img, (x, feature_y, x + bw, feature_y + 190), 24, card_col, (*THEME["gold"], 145), 2, True)
        d = ImageDraw.Draw(img)

        icon(d, x + bw // 2, feature_y + 48, kind)
        draw_text(d, title, (x + 20, feature_y + 88, x + bw - 20, feature_y + 125), 24, 16, gold2, True, "center")
        draw_text(d, body, (x + 24, feature_y + 130, x + bw - 24, feature_y + 174), 19, 12, (255, 255, 255, 255), False, "center")

    assurance_y = 955
    card(img, (60, assurance_y, 1020, assurance_y + 230), 28, card_col, (*THEME["gold"], 160), 2, True)
    d = ImageDraw.Draw(img)

    sx, sy = 155, assurance_y + 52
    shield = [
        (sx, sy), (sx + 60, sy + 20), (sx + 54, sy + 88),
        (sx, sy + 128), (sx - 54, sy + 88), (sx - 60, sy + 20)
    ]
    d.polygon(shield, fill=(*THEME["card2"], 255), outline=gold2)
    d.line((sx - 28, sy + 68, sx - 8, sy + 92, sx + 38, sy + 38), fill=gold2, width=10)

    draw_text(d, "Audit report with clean document check", (255, assurance_y + 35, 960, assurance_y + 75), 30, 19, (255, 255, 255, 255), True, "left")
    draw_text(d, "RC • Insurance • Fitness • Permit • Risk Summary", (255, assurance_y + 86, 960, assurance_y + 122), 24, 15, gold2, True, "left")
    d.line((255, assurance_y + 135, 960, assurance_y + 135), fill=(*THEME["gold"], 180), width=2)
    draw_text(d, "Professional Audit Support Platform", (255, assurance_y + 145, 960, assurance_y + 185), 23, 15, (236, 236, 236, 255), False, "left")

    by = assurance_y + 168
    card(img, (255, by, 960, by + 42), 14, (8, 40, 92, 135), (255, 255, 255, 45), 1, False)
    d = ImageDraw.Draw(img)
    draw_text(d, "RC / Insurance check  •  Fitness / Permit review  •  Audit report guidance", (275, by + 5, 940, by + 37), 17, 11, (255, 255, 255, 255), False, "center")

    footer_y = 1210
    card(img, (60, footer_y, 1020, H - 55), 26, (*THEME["card"], 245), (*THEME["gold"], 170), 2, True)
    d = ImageDraw.Draw(img)

    d.rounded_rectangle((105, footer_y + 28, 180, footer_y + 103), radius=38, outline=gold2, width=4)
    draw_text(d, "WA", (118, footer_y + 42, 167, footer_y + 88), 24, 16, gold2, True, "center")

    draw_text(d, f"WhatsApp: {PHONE}", (215, footer_y + 25, 965, footer_y + 75), 38, 24, (255, 255, 255, 255), True, "left")
    draw_text(d, WEBSITE, (215, footer_y + 82, 965, footer_y + 120), 25, 16, gold2, False, "left")

    img.convert("RGB").save(POSTER_PATH, quality=96)

    with open(CAPTION_PATH, "w", encoding="utf-8") as f:
        f.write(make_caption(c))

    print("Poster created successfully:")
    print(POSTER_PATH)
    print("Caption created successfully:")
    print(CAPTION_PATH)
    print("Size: 1080x1350 Instagram Feed Safe")
    print("Logo found:", logo_ok)


if __name__ == "__main__":
    make_poster()