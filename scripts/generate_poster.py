from PIL import Image, ImageDraw, ImageFont, ImageFilter
from datetime import datetime
import os, csv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
CONTENT_FILE = os.path.join(BASE_DIR, "content.csv")
FESTIVAL_FILE = os.path.join(BASE_DIR, "festival_calendar.csv")

POSTER_PATH = os.path.join(OUTPUT_DIR, "status_today.png")
CAPTION_PATH = os.path.join(OUTPUT_DIR, "caption_today.txt")

W, H = 1080, 1920
PHONE = "6390063999"
WEBSITE = "www.metasolwservices.in"

THEME = {
    "top": (2, 12, 35),
    "mid": (4, 31, 75),
    "bottom": (2, 12, 34),
    "gold": (226, 181, 79),
    "gold2": (255, 224, 150),
    "card": (3, 24, 60),
    "card2": (5, 36, 88),
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


def text_size(draw, text, f):
    b = draw.textbbox((0, 0), str(text), font=f)
    return b[2] - b[0], b[3] - b[1]


def wrap(draw, text, f, max_w):
    if "\n" in str(text):
        return str(text).split("\n")

    words = str(text).split()
    lines, line = [], ""

    for w in words:
        test = (line + " " + w).strip()
        if text_size(draw, test, f)[0] <= max_w:
            line = test
        else:
            if line:
                lines.append(line)
            line = w

    if line:
        lines.append(line)

    return lines


def fit(draw, text, max_w, max_h, max_size, min_size, bold=True):
    for s in range(max_size, min_size - 1, -2):
        f = font(s, bold)
        lines = wrap(draw, text, f, max_w)
        gap = max(6, int(s * 0.18))
        hs = [text_size(draw, ln, f)[1] for ln in lines]
        ws = [text_size(draw, ln, f)[0] for ln in lines] or [0]
        total = sum(hs) + gap * (len(lines) - 1)

        if max(ws) <= max_w and total <= max_h:
            return f, lines, gap

    f = font(min_size, bold)
    return f, wrap(draw, text, f, max_w), 8


def draw_text(draw, text, box, max_size, min_size, fill, bold=True, align="left"):
    x1, y1, x2, y2 = box
    f, lines, gap = fit(draw, text, x2 - x1, y2 - y1, max_size, min_size, bold)
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
        sd.rounded_rectangle((x1 + 10, y1 + 16, x2 + 10, y2 + 16), radius=radius, fill=(0, 0, 0, 95))
        sh = sh.filter(ImageFilter.GaussianBlur(18))
        img.alpha_composite(sh)

    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)
    img.alpha_composite(layer)


def background():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    d = ImageDraw.Draw(img)

    top, mid, bottom = THEME["top"], THEME["mid"], THEME["bottom"]

    for y in range(H):
        t = y / H
        if t < 0.48:
            p = t / 0.48
            a, b = top, mid
        else:
            p = (t - 0.48) / 0.52
            a, b = mid, bottom

        c = tuple(int(a[i] * (1 - p) + b[i] * p) for i in range(3))
        d.line((0, y, W, y), fill=(*c, 255))

    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((700, 115, 1260, 680), fill=(*THEME["gold"], 75))
    gd.ellipse((500, 360, 1160, 1050), fill=(35, 90, 180, 50))
    gd.ellipse((-350, 1100, 480, 2050), fill=(0, 180, 165, 26))
    glow = glow.filter(ImageFilter.GaussianBlur(42))
    img.alpha_composite(glow)

    pat = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pat)

    for i in range(-H, W, 76):
        pd.line((i, 0, i + H, H), fill=(255, 255, 255, 12), width=2)

    for r in range(260, 560, 38):
        pd.arc((770 - r, 260 - r, 770 + r, 260 + r), 305, 55, fill=(*THEME["gold"], 45), width=2)

    img.alpha_composite(pat)
    return img


def load_content():
    rows = []

    if os.path.exists(CONTENT_FILE):
        with open(CONTENT_FILE, "r", encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))

    if not rows:
        rows = [{
            "category": "AUDIT REPORT",
            "title": "Fleet audit report ke liye connect karein",
            "subtitle": "Fast checking • Clean report • Professional support",
            "cta": "Audit Report Support",
            "point1": "Vehicle document audit",
            "point2": "Insurance and fitness status check",
            "point3": "Risk summary support",
            "bullet1": "RC / Insurance check",
            "bullet2": "Fitness / Permit review",
            "bullet3": "Audit report guidance"
        }]

    day = datetime.now().timetuple().tm_yday
    return rows[day % len(rows)]


def logo_paths():
    return [
        os.path.join(ASSETS_DIR, "logo.png"),
        os.path.join(ASSETS_DIR, "logo.jpg"),
        os.path.join(ASSETS_DIR, "metasolw_logo.png"),
        os.path.join(ASSETS_DIR, "metasolw_logo.jpg"),
    ]


def draw_logo(img):
    d = ImageDraw.Draw(img)
    cx, cy = 118, 104
    gold = (*THEME["gold"], 255)
    gold2 = (*THEME["gold2"], 255)

    d.ellipse((cx - 72, cy - 72, cx + 72, cy + 72), fill=(3, 22, 52, 255), outline=gold2, width=5)
    d.ellipse((cx - 62, cy - 62, cx + 62, cy + 62), outline=gold, width=3)

    for p in logo_paths():
        if os.path.exists(p):
            try:
                lg = Image.open(p).convert("RGBA")
                lg.thumbnail((126, 126), RESAMPLE)
                img.alpha_composite(lg, (cx - lg.width // 2, cy - lg.height // 2))
                return True
            except Exception:
                pass

    f = font(34, True)
    tw, th = text_size(d, "MS", f)
    d.text((cx - tw // 2, cy - th // 2), "MS", font=f, fill=gold2)
    return False


def service_chip(draw, box, text):
    x1, y1, x2, y2 = box
    gold = (*THEME["gold"], 255)
    gold2 = (*THEME["gold2"], 255)

    draw.rounded_rectangle(box, radius=(y2 - y1) // 2, fill=gold, outline=(255, 255, 255, 120), width=2)

    sx, sy = x1 + 55, y1 + 15
    draw.polygon(
        [(sx, sy), (sx + 36, sy + 12), (sx + 31, sy + 53), (sx, sy + 66), (sx - 31, sy + 53), (sx - 36, sy + 12)],
        fill=(5, 31, 73)
    )
    draw.line((sx - 17, sy + 36, sx - 4, sy + 49, sx + 24, sy + 20), fill=gold2, width=6)

    draw_text(draw, text, (x1 + 105, y1 + 9, x2 - 24, y2 - 8), 34, 18, (8, 24, 48, 255), True, "left")


def draw_audit_visual(img, c):
    x1, y1, x2, y2 = 610, 285, 1010, 820
    gold = (*THEME["gold"], 255)
    gold2 = (*THEME["gold2"], 255)
    card_col = (*THEME["card2"], 235)

    card(img, (x1, y1, x2, y2), 34, card_col, (*THEME["gold"], 160), 2, True)
    d = ImageDraw.Draw(img)

    # document paper
    px1, py1, px2, py2 = x1 + 55, y1 + 70, x2 - 55, y2 - 70
    d.rounded_rectangle((px1, py1, px2, py2), radius=24, fill=(245, 248, 255, 245), outline=gold2, width=3)

    # folded corner
    d.polygon([(px2 - 65, py1), (px2, py1 + 65), (px2, py1)], fill=(218, 225, 238, 255))
    d.line((px2 - 65, py1, px2, py1 + 65), fill=(180, 190, 205), width=2)

    # heading strip
    d.rounded_rectangle((px1 + 28, py1 + 34, px2 - 28, py1 + 92), radius=16, fill=(5, 31, 73, 255))
    draw_text(d, "AUDIT REPORT", (px1 + 42, py1 + 42, px2 - 42, py1 + 85), 28, 18, gold2, True, "center")

    # Checklist items
    items = ["RC CHECK", "INSURANCE", "FITNESS", "PERMIT"]
    yy = py1 + 135
    for item in items:
        d.rounded_rectangle((px1 + 32, yy, px2 - 32, yy + 48), radius=12, fill=(235, 240, 248, 255))
        d.ellipse((px1 + 48, yy + 12, px1 + 72, yy + 36), fill=(7, 42, 96, 255))
        d.line((px1 + 54, yy + 25, px1 + 62, yy + 33, px1 + 72, yy + 17), fill=gold, width=4)
        draw_text(d, item, (px1 + 88, yy + 5, px2 - 50, yy + 43), 19, 13, (8, 24, 48, 255), True, "left")
        yy += 62

    # risk summary bar
    d.rounded_rectangle((px1 + 32, py2 - 82, px2 - 32, py2 - 32), radius=14, fill=(255, 224, 150, 255))
    draw_text(d, "DOCUMENT RISK SUMMARY", (px1 + 45, py2 - 75, px2 - 45, py2 - 40), 18, 12, (8, 24, 48, 255), True, "center")

    # small audit seal
    d.ellipse((x1 + 18, y2 - 96, x1 + 112, y2 - 2), fill=(3, 24, 60, 255), outline=gold2, width=3)
    d.line((x1 + 43, y2 - 47, x1 + 61, y2 - 26, x1 + 92, y2 - 66), fill=gold2, width=7)


def feature_icon(draw, cx, cy, kind):
    gold2 = (*THEME["gold2"], 255)
    draw.ellipse((cx - 42, cy - 42, cx + 42, cy + 42), outline=gold2, width=3, fill=(7, 36, 86, 255))

    if kind == "direct":
        draw.polygon([(cx - 16, cy - 28), (cx + 20, cy - 15), (cx + 17, cy + 26), (cx, cy + 36), (cx - 28, cy + 18), (cx - 30, cy - 15)], outline=gold2)
        draw.line((cx - 17, cy + 3, cx - 4, cy + 18, cx + 25, cy - 16), fill=gold2, width=6)
    elif kind == "zero":
        f = font(38, True)
        tw, th = text_size(draw, "0%", f)
        draw.text((cx - tw // 2, cy - th // 2 - 2), "0%", font=f, fill=gold2)
    else:
        draw.ellipse((cx - 15, cy - 25, cx + 15, cy + 5), fill=gold2)
        draw.arc((cx - 32, cy - 5, cx + 32, cy + 48), 205, 335, fill=gold2, width=8)


def caption(c):
    cat = c.get("category", "AUDIT REPORT").upper()

    tags = "#MetaSolw #MetaSolwServices #EverythingSolved #AuditReport #FleetAudit #VehicleAudit #DocumentCheck #InsuranceCheck #FitnessCertificate #PermitCheck #Kanpur #UttarPradesh #India"

    if "INSURANCE" in cat:
        tags = "#MetaSolw #MetaSolwServices #VehicleInsurance #InsuranceRenewal #DirectCompanyPolicy #NoAgent #NoCommission #Kanpur #UttarPradesh #India"

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
    card_col = (*THEME["card"], 242)

    img = background()
    d = ImageDraw.Draw(img)

    # border
    d.rounded_rectangle((28, 28, W - 28, H - 28), radius=42, outline=(255, 255, 255, 190), width=3)
    d.rounded_rectangle((46, 46, W - 46, H - 46), radius=34, outline=(*THEME["gold"], 135), width=2)

    logo_ok = draw_logo(img)
    d = ImageDraw.Draw(img)

    # header
    draw_text(d, "METASOLW", (230, 45, 790, 112), 68, 42, (255, 255, 255, 255), True, "left")
    draw_text(d, "SERVICES", (230, 115, 790, 182), 68, 42, (255, 255, 255, 255), True, "left")

    tf = font(30, True)
    tag = "Everything Solved"
    tw, th = text_size(d, tag, tf)
    tag_x, tag_y = 325, 198
    d.line((245, tag_y + 18, tag_x - 25, tag_y + 18), fill=gold, width=3)
    d.text((tag_x, tag_y), tag, font=tf, fill=gold2)
    d.line((tag_x + tw + 25, tag_y + 18, tag_x + tw + 130, tag_y + 18), fill=gold, width=3)

    # service chip + date
    service_chip(d, (42, 285, 450, 375), c["category"].upper())

    d.rounded_rectangle((470, 295, 655, 365), radius=35, fill=(*THEME["card"], 238), outline=gold, width=2)
    draw_text(d, datetime.now().strftime("%d %b %Y"), (490, 303, 635, 356), 23, 15, (255, 255, 255, 255), True, "center")

    # right audit visual
    draw_audit_visual(img, c)
    d = ImageDraw.Draw(img)

    # left headline panel
    card(img, (42, 430, 590, 830), 34, card_col, (*THEME["gold"], 150), 2, True)
    d = ImageDraw.Draw(img)

    draw_text(d, c["title"], (78, 470, 550, 635), 48, 31, (255, 255, 255, 255), True, "left")

    cta_box = (78, 665, 520, 735)
    d.rounded_rectangle(cta_box, radius=35, fill=gold, outline=(255, 255, 255, 110), width=2)
    draw_text(d, c["cta"], (105, 675, 493, 724), 29, 18, (10, 24, 45, 255), True, "center")

    draw_text(d, c["subtitle"], (78, 748, 550, 800), 22, 14, (245, 245, 245, 255), False, "left")

    # platform band
    band_y = 890
    card(img, (42, band_y, W - 42, band_y + 92), 20, gold, (255, 255, 255, 110), 2, True)
    d = ImageDraw.Draw(img)
    draw_text(d, "PLATFORM BY METASOLW SERVICES", (80, band_y + 15, W - 80, band_y + 76), 38, 24, (8, 23, 48, 255), True, "center")

    # feature cards
    fy = 1015
    box_w, box_h, gap = 315, 245, 22

    feature_data = [
        ("DIRECT", c["point1"], "direct"),
        ("ZERO", c["point2"], "zero"),
        ("CONTROL", c["point3"], "control"),
    ]

    for i, (title, body, kind) in enumerate(feature_data):
        x1 = 42 + i * (box_w + gap)
        x2 = x1 + box_w

        card(img, (x1, fy, x2, fy + box_h), 22, card_col, (*THEME["gold"], 160), 2, True)
        d = ImageDraw.Draw(img)

        feature_icon(d, x1 + box_w // 2, fy + 58, kind)
        draw_text(d, title, (x1 + 22, fy + 112, x2 - 22, fy + 158), 32, 21, gold2, True, "center")
        draw_text(d, body, (x1 + 26, fy + 166, x2 - 26, fy + 228), 22, 14, (255, 255, 255, 255), False, "center")

    # assurance panel
    ty = 1305
    card(img, (42, ty, W - 42, ty + 330), 26, card_col, (*THEME["gold"], 160), 2, True)
    d = ImageDraw.Draw(img)

    sx, sy = 135, ty + 72
    shield = [(sx, sy), (sx + 72, sy + 24), (sx + 66, sy + 108), (sx, sy + 155), (sx - 66, sy + 108), (sx - 72, sy + 24)]
    d.polygon(shield, fill=(*THEME["card2"], 255), outline=gold2)
    d.line((sx - 35, sy + 83, sx - 10, sy + 112, sx + 45, sy + 47), fill=gold2, width=12)

    draw_text(d, "Audit report with clean document check", (245, ty + 45, W - 70, ty + 93), 32, 20, (255, 255, 255, 255), True, "left")
    draw_text(d, "RC • Insurance • Fitness • Permit • Risk Summary", (245, ty + 103, W - 70, ty + 148), 28, 17, gold2, True, "left")
    d.line((245, ty + 163, W - 70, ty + 163), fill=(*THEME["gold"], 180), width=2)
    draw_text(d, "Professional Audit Support Platform", (245, ty + 178, W - 70, ty + 225), 27, 18, (236, 236, 236, 255), False, "left")

    # bottom bullets
    by = ty + 238
    card(img, (70, by, W - 70, by + 72), 20, (8, 40, 92, 150), (255, 255, 255, 55), 1, False)
    d = ImageDraw.Draw(img)

    items = [c["bullet1"], c["bullet2"], c["bullet3"]]
    xs = [105, 420, 720]

    for idx, text in enumerate(items):
        x = xs[idx]
        d.ellipse((x, by + 15, x + 46, by + 61), outline=gold2, width=3)
        d.line((x + 13, by + 39, x + 22, by + 49, x + 34, by + 28), fill=gold2, width=4)
        draw_text(d, text, (x + 55, by + 12, x + 275, by + 62), 21, 13, (255, 255, 255, 255), False, "left")

        if idx < 2:
            d.line((x + 290, by + 14, x + 290, by + 58), fill=(*THEME["gold"], 120), width=2)

    # footer
    foot_y = 1745
    card(img, (42, foot_y, W - 42, H - 55), 26, card_col, (*THEME["gold"], 170), 2, True)
    d = ImageDraw.Draw(img)

    d.ellipse((100, foot_y + 34, 180, foot_y + 114), outline=gold2, width=4)
    d.arc((122, foot_y + 55, 158, foot_y + 90), 35, 330, fill=gold2, width=5)
    d.line((138, foot_y + 88, 160, foot_y + 106), fill=gold2, width=5)

    draw_text(d, f"WhatsApp: {PHONE}", (225, foot_y + 25, W - 75, foot_y + 86), 43, 27, (255, 255, 255, 255), True, "left")
    draw_text(d, WEBSITE, (325, foot_y + 90, W - 110, foot_y + 135), 29, 18, (255, 255, 255, 255), False, "left")
    d.ellipse((288, foot_y + 102, 312, foot_y + 126), outline=gold2, width=2)

    img.convert("RGB").save(POSTER_PATH, quality=96)

    with open(CAPTION_PATH, "w", encoding="utf-8") as f:
        f.write(caption(c))

    print("Poster created successfully:")
    print(POSTER_PATH)
    print("Caption created successfully:")
    print(CAPTION_PATH)
    print("Logo found:", logo_ok)
    print("Category:", c["category"])


if __name__ == "__main__":
    make_poster()