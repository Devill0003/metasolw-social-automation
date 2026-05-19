from PIL import Image, ImageDraw, ImageFont, ImageFilter
from datetime import datetime
import os
import csv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
CONTENT_FILE = os.path.join(BASE_DIR, "content.csv")

POSTER_PATH = os.path.join(OUTPUT_DIR, "status_today.png")
CAPTION_PATH = os.path.join(OUTPUT_DIR, "caption_today.txt")

W, H = 1080, 1920
PHONE = "6390063999"
WEBSITE = "www.metasolwservices.in"

THEME = {
    "top": (2, 12, 35),
    "mid": (6, 35, 82),
    "bottom": (2, 12, 34),
    "gold": (226, 181, 79),
    "gold2": (255, 224, 150),
    "card": (3, 24, 60),
    "card2": (5, 36, 88),
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


def text_size(draw, text, f):
    b = draw.textbbox((0, 0), str(text), font=f)
    return b[2] - b[0], b[3] - b[1]


def wrap_text(draw, text, f, max_w):
    result = []
    for part in str(text).split("\n"):
        words = part.split()
        line = ""
        for word in words:
            test = (line + " " + word).strip()
            if text_size(draw, test, f)[0] <= max_w:
                line = test
            else:
                if line:
                    result.append(line)
                line = word
        if line:
            result.append(line)
    return result or [""]


def fit_text(draw, text, max_w, max_h, max_size, min_size, bold=True):
    for s in range(max_size, min_size - 1, -2):
        f = font(s, bold)
        lines = wrap_text(draw, text, f, max_w)
        gap = max(5, int(s * 0.18))
        hs = [text_size(draw, ln, f)[1] for ln in lines]
        ws = [text_size(draw, ln, f)[0] for ln in lines] or [0]
        total = sum(hs) + gap * (len(lines) - 1)
        if max(ws) <= max_w and total <= max_h:
            return f, lines, gap

    f = font(min_size, bold)
    return f, wrap_text(draw, text, f, max_w), 8


def draw_text(draw, text, box, max_size, min_size, fill, bold=True, align="left"):
    x1, y1, x2, y2 = box
    f, lines, gap = fit_text(draw, text, x2 - x1, y2 - y1, max_size, min_size, bold)
    hs = [text_size(draw, ln, f)[1] for ln in lines]
    total = sum(hs) + gap * (len(lines) - 1)
    y = y1 + ((y2 - y1) - total) // 2

    for ln, h in zip(lines, hs):
        tw, _ = text_size(draw, ln, f)
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
        sd.rounded_rectangle((x1 + 9, y1 + 13, x2 + 9, y2 + 13), radius=radius, fill=(0, 0, 0, 90))
        sh = sh.filter(ImageFilter.GaussianBlur(15))
        img.alpha_composite(sh)

    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)
    img.alpha_composite(layer)


def background():
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
    gd.ellipse((700, 120, 1260, 710), fill=(*THEME["gold"], 70))
    gd.ellipse((-300, 1150, 520, 2050), fill=(0, 170, 170, 26))
    gd.ellipse((420, 430, 1220, 1250), fill=(40, 80, 180, 40))
    glow = glow.filter(ImageFilter.GaussianBlur(36))
    img.alpha_composite(glow)

    pattern = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pattern)

    for i in range(-H, W, 80):
        pd.line((i, 0, i + H, H), fill=(255, 255, 255, 12), width=2)

    for r in range(240, 620, 50):
        pd.arc((790 - r, 250 - r, 790 + r, 250 + r), 300, 60, fill=(*THEME["gold"], 45), width=2)

    img.alpha_composite(pattern)
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
    cx, cy = 122, 110
    gold = (*THEME["gold"], 255)
    gold2 = (*THEME["gold2"], 255)

    d.ellipse((cx - 70, cy - 70, cx + 70, cy + 70), fill=(3, 22, 52, 255), outline=gold2, width=5)
    d.ellipse((cx - 58, cy - 58, cx + 58, cy + 58), outline=gold, width=3)

    for p in logo_paths():
        if os.path.exists(p):
            try:
                lg = Image.open(p).convert("RGBA")
                lg.thumbnail((126, 126), RESAMPLE)
                img.alpha_composite(lg, (cx - lg.width // 2, cy - lg.height // 2))
                return True
            except Exception:
                pass

    f = font(28, True)
    tw, th = text_size(d, "MS", f)
    d.text((cx - tw / 2, cy - th / 2), "MS", font=f, fill=gold2)
    return False


def audit_visual(img, box):
    x1, y1, x2, y2 = box
    gold = (*THEME["gold"], 255)
    gold2 = (*THEME["gold2"], 255)

    card(img, box, 36, (*THEME["card2"], 235), (*THEME["gold"], 150), 2, True)
    d = ImageDraw.Draw(img)

    draw_text(d, "AUDIT REPORT", (x1 + 34, y1 + 22, x2 - 34, y1 + 70), 30, 18, gold2, True, "center")

    px1, py1 = x1 + 54, y1 + 88
    px2, py2 = x2 - 54, y2 - 36

    d.rounded_rectangle((px1, py1, px2, py2), radius=24, fill=(245, 248, 255, 245), outline=gold2, width=3)
    d.polygon([(px2 - 55, py1), (px2, py1 + 55), (px2, py1)], fill=(214, 224, 238, 255))
    d.line((px2 - 55, py1, px2, py1 + 55), fill=(175, 187, 203), width=2)

    d.rounded_rectangle((px1 + 26, py1 + 30, px2 - 26, py1 + 78), radius=14, fill=(5, 31, 73, 255))
    draw_text(d, "FLEET CHECK", (px1 + 36, py1 + 36, px2 - 36, py1 + 72), 20, 13, gold2, True, "center")

    items = ["RC / INSURANCE", "FITNESS STATUS", "PERMIT REVIEW"]
    yy = py1 + 105

    for item in items:
        d.rounded_rectangle((px1 + 26, yy, px2 - 26, yy + 46), radius=12, fill=(236, 242, 250, 255), outline=(220, 226, 236, 255), width=1)
        d.ellipse((px1 + 42, yy + 12, px1 + 66, yy + 36), fill=(7, 42, 96, 255))
        d.line((px1 + 48, yy + 25, px1 + 56, yy + 33, px1 + 69, yy + 15), fill=gold, width=4)
        draw_text(d, item, (px1 + 80, yy + 7, px2 - 38, yy + 40), 16, 10, (8, 24, 48, 255), True, "left")
        yy += 58


def feature_icon(draw, cx, cy, kind):
    gold2 = (*THEME["gold2"], 255)
    draw.ellipse((cx - 38, cy - 38, cx + 38, cy + 38), outline=gold2, width=3, fill=(7, 36, 86, 255))

    if kind == "doc":
        draw.rectangle((cx - 18, cy - 24, cx + 18, cy + 26), outline=gold2, width=3)
        draw.line((cx - 11, cy + 7, cx - 3, cy + 16, cx + 18, cy - 12), fill=gold2, width=5)
    elif kind == "status":
        draw.line((cx - 22, cy - 8, cx - 8, cy + 8, cx + 25, cy - 24), fill=gold2, width=6)
        draw.arc((cx - 30, cy - 30, cx + 30, cy + 30), 20, 330, fill=gold2, width=3)
    else:
        f = font(30, True)
        tw, th = text_size(draw, "!", f)
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

    img = background()
    d = ImageDraw.Draw(img)

    d.rounded_rectangle((36, 36, W - 36, H - 36), radius=48, outline=(255, 255, 255, 180), width=3)
    d.rounded_rectangle((54, 54, W - 54, H - 54), radius=38, outline=(*THEME["gold"], 130), width=2)

    logo_ok = draw_logo(img)
    d = ImageDraw.Draw(img)

    draw_text(d, "METASOLW SERVICES", (220, 54, 920, 132), 64, 42, (255, 255, 255, 255), True, "left")
    draw_text(d, "Everything Solved • Direct Company Platform", (222, 132, 880, 170), 23, 15, gold2, False, "left")

    d.rounded_rectangle((62, 210, 410, 290), radius=40, fill=gold, outline=(255, 255, 255, 120), width=2)
    draw_text(d, "AUDIT REPORT", (100, 225, 390, 276), 32, 20, (8, 24, 48, 255), True, "center")

    d.rounded_rectangle((430, 215, 660, 285), radius=35, fill=card_col, outline=gold, width=2)
    draw_text(d, datetime.now().strftime("%d %b %Y"), (455, 226, 635, 276), 24, 15, (255, 255, 255, 255), True, "center")

    hero = (62, 330, 1018, 800)
    card(img, hero, 38, card_col, (*THEME["gold"], 145), 2, True)
    d = ImageDraw.Draw(img)

    draw_text(d, c["title"], (102, 370, 560, 560), 56, 34, (255, 255, 255, 255), True, "left")

    d.rounded_rectangle((102, 590, 520, 670), radius=40, fill=gold, outline=(255, 255, 255, 120), width=2)
    draw_text(d, c["cta"], (130, 603, 492, 658), 30, 18, (8, 24, 48, 255), True, "center")

    draw_text(d, c["subtitle"], (102, 700, 560, 745), 23, 14, (235, 241, 248, 255), False, "left")

    audit_visual(img, (610, 365, 960, 745))

    y = 845
    card(img, (62, y, 1018, y + 88), 22, gold, (255, 255, 255, 110), 2, True)
    d = ImageDraw.Draw(img)
    draw_text(d, "PLATFORM BY METASOLW SERVICES", (100, y + 15, 980, y + 73), 38, 24, (8, 23, 48, 255), True, "center")

    y = 975
    gap = 28
    bw = (956 - 2 * gap) // 3
    xs = [62, 62 + bw + gap, 62 + 2 * (bw + gap)]

    features = [
        ("DOCUMENT", c["point1"], "doc"),
        ("STATUS", c["point2"], "status"),
        ("RISK", c["point3"], "risk"),
    ]

    for i, (title, body, kind) in enumerate(features):
        x = xs[i]
        card(img, (x, y, x + bw, y + 210), 28, card_col, (*THEME["gold"], 145), 2, True)
        d = ImageDraw.Draw(img)

        cx = x + bw // 2
        cy = y + 55
        feature_icon(d, cx, cy, kind)

        draw_text(d, title, (x + 20, y + 103, x + bw - 20, y + 140), 26, 18, gold2, True, "center")
        draw_text(d, body, (x + 24, y + 145, x + bw - 24, y + 195), 21, 13, (255, 255, 255, 255), False, "center")

    y = 1225
    card(img, (62, y, 1018, y + 330), 30, card_col, (*THEME["gold"], 160), 2, True)
    d = ImageDraw.Draw(img)

    sx, sy = 150, y + 76
    shield = [
        (sx, sy), (sx + 72, sy + 24), (sx + 66, sy + 108),
        (sx, sy + 155), (sx - 66, sy + 108), (sx - 72, sy + 24)
    ]

    d.polygon(shield, fill=(*THEME["card2"], 255), outline=gold2)
    d.line((sx - 35, sy + 83, sx - 10, sy + 112, sx + 45, sy + 47), fill=gold2, width=12)

    draw_text(d, "Audit report with clean document check", (260, y + 50, 970, y + 100), 34, 22, (255, 255, 255, 255), True, "left")
    draw_text(d, "RC • Insurance • Fitness • Permit • Risk Summary", (260, y + 113, 970, y + 156), 28, 17, gold2, True, "left")
    d.line((260, y + 172, 970, y + 172), fill=(*THEME["gold"], 180), width=2)
    draw_text(d, "Professional Audit Support Platform", (260, y + 185, 970, y + 230), 26, 17, (236, 236, 236, 255), False, "left")

    by = y + 244
    card(img, (95, by, 985, by + 72), 20, (8, 40, 92, 150), (255, 255, 255, 55), 1, False)
    d = ImageDraw.Draw(img)

    items = [c["bullet1"], c["bullet2"], c["bullet3"]]
    item_x = [122, 420, 710]

    for idx, text in enumerate(items):
        x = item_x[idx]
        d.ellipse((x, by + 16, x + 42, by + 58), outline=gold2, width=3)
        d.line((x + 11, by + 38, x + 19, by + 47, x + 32, by + 27), fill=gold2, width=4)
        draw_text(d, text, (x + 55, by + 10, x + 245, by + 62), 19, 12, (255, 255, 255, 255), False, "left")

        if idx < 2:
            d.line((x + 270, by + 16, x + 270, by + 56), fill=(*THEME["gold"], 120), width=2)

    y = 1665
    card(img, (62, y, 1018, H - 70), 30, (*THEME["card"], 245), (*THEME["gold"], 170), 2, True)
    d = ImageDraw.Draw(img)

    d.rounded_rectangle((115, y + 42, 205, y + 132), radius=45, outline=gold2, width=4)
    draw_text(d, "WA", (128, y + 58, 192, y + 114), 28, 18, gold2, True, "center")

    draw_text(d, f"WhatsApp: {PHONE}", (245, y + 35, 960, y + 95), 44, 28, (255, 255, 255, 255), True, "left")
    draw_text(d, WEBSITE, (245, y + 105, 960, y + 150), 30, 18, gold2, False, "left")

    img.convert("RGB").save(POSTER_PATH, quality=96)

    with open(CAPTION_PATH, "w", encoding="utf-8") as f:
        f.write(make_caption(c))

    print("Poster created successfully:")
    print(POSTER_PATH)
    print("Caption created successfully:")
    print(CAPTION_PATH)
    print("Logo found:", logo_ok)


if __name__ == "__main__":
    make_poster()