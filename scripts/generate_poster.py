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

W, H = 1080, 1350

PHONE = "6390063999"
WEBSITE = "www.metasolwservices.in"

NAVY = (3, 22, 52)
NAVY2 = (5, 35, 84)
GOLD = (226, 181, 79)
GOLD2 = (255, 224, 150)
WHITE = (255, 255, 255)
SOFT = (232, 240, 248)


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


def tsize(draw, text, f):
    b = draw.textbbox((0, 0), str(text), font=f)
    return b[2] - b[0], b[3] - b[1]


def center_text(draw, text, box, f, fill):
    x1, y1, x2, y2 = box
    tw, th = tsize(draw, text, f)
    draw.text(
        (x1 + (x2 - x1 - tw) / 2, y1 + (y2 - y1 - th) / 2),
        text,
        font=f,
        fill=fill
    )


def multiline(draw, text, x, y, f, fill, gap=8):
    for line in str(text).split("\n"):
        draw.text((x, y), line, font=f, fill=fill)
        _, h = tsize(draw, line, f)
        y += h + gap
    return y


def card(img, box, radius, fill, outline=None, width=2, shadow=True):
    x1, y1, x2, y2 = box

    if shadow:
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        sd = ImageDraw.Draw(sh)
        sd.rounded_rectangle(
            (x1 + 8, y1 + 10, x2 + 8, y2 + 10),
            radius=radius,
            fill=(0, 0, 0, 85)
        )
        sh = sh.filter(ImageFilter.GaussianBlur(12))
        img.alpha_composite(sh)

    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)
    img.alpha_composite(layer)


def background():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    d = ImageDraw.Draw(img)

    top = (2, 12, 35)
    mid = (6, 35, 82)
    bottom = (2, 12, 34)

    for y in range(H):
        t = y / (H - 1)

        if t < 0.55:
            p = t / 0.55
            a, b = top, mid
        else:
            p = (t - 0.55) / 0.45
            a, b = mid, bottom

        c = tuple(int(a[i] * (1 - p) + b[i] * p) for i in range(3))
        d.line((0, y, W, y), fill=(*c, 255))

    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((700, 40, 1250, 520), fill=(*GOLD, 55))
    gd.ellipse((-260, 820, 520, 1480), fill=(0, 170, 170, 22))
    glow = glow.filter(ImageFilter.GaussianBlur(34))
    img.alpha_composite(glow)

    pattern = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pattern)

    for i in range(-H, W, 82):
        pd.line((i, 0, i + H, H), fill=(255, 255, 255, 10), width=2)

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


def draw_logo(img):
    d = ImageDraw.Draw(img)
    cx, cy = 98, 84

    d.ellipse((cx - 54, cy - 54, cx + 54, cy + 54), fill=NAVY, outline=GOLD2, width=4)
    d.ellipse((cx - 45, cy - 45, cx + 45, cy + 45), outline=GOLD, width=2)

    logo_files = ["logo.png", "logo.jpg", "metasolw_logo.png", "metasolw_logo.jpg"]

    for name in logo_files:
        p = os.path.join(ASSETS_DIR, name)
        if os.path.exists(p):
            try:
                logo = Image.open(p).convert("RGBA")
                logo.thumbnail((92, 92))
                img.alpha_composite(logo, (cx - logo.width // 2, cy - logo.height // 2))
                return True
            except Exception:
                pass

    center_text(d, "MS", (cx - 34, cy - 25, cx + 34, cy + 25), font(24, True), GOLD2)
    return False


def audit_document(img):
    x1, y1, x2, y2 = 645, 300, 970, 585

    card(img, (x1, y1, x2, y2), 26, (*NAVY2, 235), (*GOLD, 150), 2, True)
    d = ImageDraw.Draw(img)

    center_text(d, "AUDIT REPORT", (x1 + 24, y1 + 14, x2 - 24, y1 + 48), font(21, True), GOLD2)

    px1, py1, px2, py2 = x1 + 42, y1 + 62, x2 - 42, y2 - 28

    d.rounded_rectangle((px1, py1, px2, py2), radius=18, fill=(246, 249, 255, 245), outline=GOLD2, width=3)
    d.polygon([(px2 - 45, py1), (px2, py1 + 45), (px2, py1)], fill=(214, 224, 238, 255))

    d.rounded_rectangle((px1 + 22, py1 + 22, px2 - 22, py1 + 62), radius=12, fill=NAVY)
    center_text(d, "FLEET CHECK", (px1 + 25, py1 + 25, px2 - 25, py1 + 58), font(16, True), GOLD2)

    items = ["RC / INSURANCE", "FITNESS STATUS", "PERMIT REVIEW"]
    yy = py1 + 86

    for item in items:
        d.rounded_rectangle((px1 + 22, yy, px2 - 22, yy + 40), radius=10, fill=(236, 242, 250, 255))
        d.ellipse((px1 + 35, yy + 10, px1 + 59, yy + 34), fill=(7, 42, 96))
        d.line((px1 + 41, yy + 23, px1 + 49, yy + 31, px1 + 62, yy + 14), fill=GOLD, width=4)
        d.text((px1 + 72, yy + 11), item, font=font(14, True), fill=(8, 24, 48))
        yy += 50


def feature_box(img, x, y, w, title, desc, icon_type):
    card(img, (x, y, x + w, y + 175), 24, (*NAVY, 238), (*GOLD, 150), 2, True)
    d = ImageDraw.Draw(img)

    cx = x + w // 2
    cy = y + 48

    d.ellipse((cx - 34, cy - 34, cx + 34, cy + 34), outline=GOLD2, width=3, fill=(7, 36, 86))

    if icon_type == "doc":
        d.rectangle((cx - 15, cy - 20, cx + 15, cy + 22), outline=GOLD2, width=3)
        d.line((cx - 10, cy + 5, cx - 2, cy + 14, cx + 16, cy - 12), fill=GOLD2, width=4)

    elif icon_type == "status":
        d.line((cx - 20, cy - 5, cx - 7, cy + 10, cx + 22, cy - 20), fill=GOLD2, width=5)
        d.arc((cx - 26, cy - 26, cx + 26, cy + 26), 20, 330, fill=GOLD2, width=3)

    else:
        center_text(d, "!", (cx - 25, cy - 25, cx + 25, cy + 25), font(32, True), GOLD2)

    center_text(d, title, (x + 18, y + 88, x + w - 18, y + 118), font(24, True), GOLD2)
    center_text(d, desc, (x + 20, y + 126, x + w - 20, y + 160), font(17, False), WHITE)


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

    img = background()
    d = ImageDraw.Draw(img)

    # SAME MARGIN FRAME
    d.rounded_rectangle((34, 34, W - 34, H - 34), radius=44, outline=(255, 255, 255, 180), width=3)
    d.rounded_rectangle((52, 52, W - 52, H - 52), radius=34, outline=(*GOLD, 130), width=2)

    logo_ok = draw_logo(img)
    d = ImageDraw.Draw(img)

    # HEADER
    d.text((175, 48), "METASOLW SERVICES", font=font(48, True), fill=WHITE)
    d.text((178, 105), "Everything Solved • Direct Company Platform", font=font(21, False), fill=GOLD2)

    # BADGES
    d.rounded_rectangle((60, 165, 355, 225), radius=30, fill=GOLD, outline=(255, 255, 255, 120), width=2)
    center_text(d, "AUDIT REPORT", (80, 174, 335, 214), font(28, True), (8, 24, 48))

    d.rounded_rectangle((380, 165, 585, 225), radius=30, fill=(*NAVY, 238), outline=GOLD, width=2)
    center_text(d, datetime.now().strftime("%d %b %Y"), (400, 174, 565, 214), font(20, True), WHITE)

    # HERO
    card(img, (60, 255, 1020, 615), 30, (*NAVY, 238), (*GOLD, 145), 2, True)
    d = ImageDraw.Draw(img)

    headline = "Fleet audit report\nke liye connect\nkarein"
    multiline(d, headline, 100, 300, font(53, True), WHITE, 8)

    d.rounded_rectangle((100, 470, 500, 535), radius=32, fill=GOLD, outline=(255, 255, 255, 110), width=2)
    center_text(d, "Audit Report Support", (120, 482, 480, 523), font(25, True), (8, 24, 48))

    d.text((100, 562), "Fast checking • Clean report • Professional support", font=font(20, False), fill=SOFT)

    audit_document(img)

    # PLATFORM
    card(img, (60, 650, 1020, 720), 18, (*GOLD, 255), (255, 255, 255, 110), 2, True)
    d = ImageDraw.Draw(img)
    center_text(d, "PLATFORM BY METASOLW SERVICES", (95, 665, 985, 707), font(32, True), (8, 23, 48))

    # FEATURE BOXES
    y = 755
    bw = 302
    gap = 26

    feature_box(img, 60, y, bw, "DOCUMENT", "RC / Insurance Audit", "doc")
    feature_box(img, 60 + bw + gap, y, bw, "STATUS", "Fitness / Permit Review", "status")
    feature_box(img, 60 + 2 * (bw + gap), y, bw, "RISK", "Clean Risk Summary", "risk")

    # ASSURANCE
    y = 970
    card(img, (60, y, 1020, y + 210), 28, (*NAVY, 242), (*GOLD, 160), 2, True)
    d = ImageDraw.Draw(img)

    sx, sy = 150, y + 50
    shield = [
        (sx, sy),
        (sx + 58, sy + 20),
        (sx + 52, sy + 88),
        (sx, sy + 128),
        (sx - 52, sy + 88),
        (sx - 58, sy + 20)
    ]

    d.polygon(shield, fill=NAVY2, outline=GOLD2)
    d.line((sx - 28, sy + 68, sx - 8, sy + 92, sx + 38, sy + 38), fill=GOLD2, width=10)

    d.text((250, y + 38), "Audit report with clean document check", font=font(30, True), fill=WHITE)
    d.text((250, y + 88), "RC • Insurance • Fitness • Permit • Risk Summary", font=font(23, True), fill=GOLD2)
    d.line((250, y + 125, 960, y + 125), fill=(*GOLD, 180), width=2)
    d.text((250, y + 145), "Professional Audit Support Platform", font=font(23, False), fill=SOFT)

    # FOOTER
    y = 1210
    card(img, (60, y, 1020, H - 55), 26, (*NAVY, 245), (*GOLD, 170), 2, True)
    d = ImageDraw.Draw(img)

    d.rounded_rectangle((105, y + 28, 180, y + 103), radius=38, outline=GOLD2, width=4)
    center_text(d, "WA", (118, y + 42, 167, y + 88), font(24, True), GOLD2)

    d.text((215, y + 25), f"WhatsApp: {PHONE}", font=font(38, True), fill=WHITE)
    d.text((215, y + 82), WEBSITE, font=font(25, False), fill=GOLD2)

    img.convert("RGB").save(POSTER_PATH, quality=96)

    with open(CAPTION_PATH, "w", encoding="utf-8") as f:
        f.write(make_caption(c))

    print("Poster created successfully:")
    print(POSTER_PATH)
    print("Caption created successfully:")
    print(CAPTION_PATH)
    print("Size: 1080x1350 FIXED ALIGNMENT")
    print("Logo found:", logo_ok)


if __name__ == "__main__":
    make_poster()