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

NAVY = (4, 18, 45)
NAVY2 = (7, 39, 92)
NAVY3 = (9, 53, 118)
GOLD = (226, 181, 79)
GOLD2 = (255, 224, 150)
WHITE = (255, 255, 255)
SOFT = (229, 237, 247)
DARK = (8, 22, 42)

try:
    RESAMPLE = Image.Resampling.LANCZOS
except AttributeError:
    RESAMPLE = Image.LANCZOS


def clean(value):
    return str(value or "").replace("\\n", "\n").strip()


def get_font(size, bold=False):
    paths = [
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\calibrib.ttf" if bold else r"C:\Windows\Fonts\calibri.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]

    for path in paths:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)

    return ImageFont.load_default()


def text_size(draw, text, font):
    box = draw.textbbox((0, 0), str(text), font=font)
    return box[2] - box[0], box[3] - box[1]


def center(draw, text, box, font, fill):
    x1, y1, x2, y2 = box
    tw, th = text_size(draw, text, font)
    draw.text(
        (x1 + (x2 - x1 - tw) / 2, y1 + (y2 - y1 - th) / 2),
        text,
        font=font,
        fill=fill
    )


def center_fit(draw, text, box, max_size, min_size, fill, bold=True):
    x1, y1, x2, y2 = box
    text = clean(text).replace("\n", " ")

    for size in range(max_size, min_size - 1, -2):
        font = get_font(size, bold)
        tw, th = text_size(draw, text, font)
        if tw <= (x2 - x1) and th <= (y2 - y1):
            center(draw, text, box, font, fill)
            return

    center(draw, text, box, get_font(min_size, bold), fill)


def multiline_center(draw, text, box, max_size, min_size, fill, bold=True):
    x1, y1, x2, y2 = box
    lines = [line.strip() for line in clean(text).split("\n") if line.strip()]

    if not lines:
        lines = [""]

    for size in range(max_size, min_size - 1, -2):
        font = get_font(size, bold)
        gap = max(7, int(size * 0.18))
        sizes = [text_size(draw, line, font) for line in lines]
        total_h = sum(h for _, h in sizes) + gap * (len(lines) - 1)
        max_w = max(w for w, _ in sizes)

        if max_w <= (x2 - x1) and total_h <= (y2 - y1):
            y = y1 + ((y2 - y1) - total_h) / 2
            for line, (tw, th) in zip(lines, sizes):
                x = x1 + ((x2 - x1) - tw) / 2
                draw.text((x, y), line, font=font, fill=fill)
                y += th + gap
            return

    font = get_font(min_size, bold)
    gap = 7
    sizes = [text_size(draw, line, font) for line in lines]
    total_h = sum(h for _, h in sizes) + gap * (len(lines) - 1)
    y = y1 + ((y2 - y1) - total_h) / 2

    for line, (tw, th) in zip(lines, sizes):
        x = x1 + ((x2 - x1) - tw) / 2
        draw.text((x, y), line, font=font, fill=fill)
        y += th + gap


def card(img, box, radius, fill, outline=None, width=2, shadow=True):
    x1, y1, x2, y2 = box

    if shadow:
        shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        sd = ImageDraw.Draw(shadow)
        sd.rounded_rectangle(
            (x1 + 8, y1 + 10, x2 + 8, y2 + 10),
            radius=radius,
            fill=(0, 0, 0, 85)
        )
        shadow = shadow.filter(ImageFilter.GaussianBlur(14))
        img.alpha_composite(shadow)

    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)
    img.alpha_composite(layer)


def background():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    d = ImageDraw.Draw(img)

    top = (2, 12, 34)
    mid = (7, 42, 100)
    bottom = (2, 13, 34)

    for y in range(H):
        t = y / (H - 1)

        if t < 0.55:
            p = t / 0.55
            a, b = top, mid
        else:
            p = (t - 0.55) / 0.45
            a, b = mid, bottom

        color = tuple(int(a[i] * (1 - p) + b[i] * p) for i in range(3))
        d.line((0, y, W, y), fill=(*color, 255))

    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((700, 20, 1250, 520), fill=(*GOLD, 55))
    gd.ellipse((-270, 820, 500, 1480), fill=(0, 175, 165, 22))
    gd.ellipse((300, 250, 1080, 1050), fill=(30, 60, 160, 30))
    glow = glow.filter(ImageFilter.GaussianBlur(36))
    img.alpha_composite(glow)

    pattern = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pattern)
    for i in range(-H, W, 84):
        pd.line((i, 0, i + H, H), fill=(255, 255, 255, 9), width=2)
    img.alpha_composite(pattern)

    return img


def draw_logo(img):
    d = ImageDraw.Draw(img)
    cx, cy = 96, 86

    d.ellipse((cx - 54, cy - 54, cx + 54, cy + 54), fill=NAVY, outline=GOLD2, width=4)
    d.ellipse((cx - 45, cy - 45, cx + 45, cy + 45), outline=GOLD, width=2)

    for name in ["logo.png", "logo.jpg", "metasolw_logo.png", "metasolw_logo.jpg"]:
        path = os.path.join(ASSETS_DIR, name)

        if os.path.exists(path):
            try:
                logo = Image.open(path).convert("RGBA")
                logo.thumbnail((90, 90), RESAMPLE)
                img.alpha_composite(logo, (cx - logo.width // 2, cy - logo.height // 2))
                return True
            except Exception:
                pass

    center(d, "MS", (cx - 35, cy - 25, cx + 35, cy + 25), get_font(24, True), GOLD2)
    return False


def check_icon(draw, cx, cy, r=26):
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=NAVY3, outline=GOLD2, width=3)
    draw.line((cx - 11, cy + 1, cx - 2, cy + 11, cx + 15, cy - 13), fill=GOLD2, width=5)


def feature_row(img, y, title, subtitle):
    card(img, (80, y, 1000, y + 112), 26, (*NAVY, 238), (*GOLD, 130), 2, True)

    d = ImageDraw.Draw(img)
    check_icon(d, 140, y + 56, 31)

    title_text = clean(title).replace("\n", " ")
    subtitle_text = clean(subtitle).replace("\n", " ")

    center_fit(d, title_text, (205, y + 18, 970, y + 52), 30, 22, GOLD2, True)
    center_fit(d, subtitle_text, (205, y + 60, 970, y + 94), 22, 16, WHITE, False)


def badge(draw, box, text, fill, text_fill, outline=None):
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=(y2 - y1) // 2, fill=fill, outline=outline, width=2)
    center_fit(draw, clean(text), (x1 + 15, y1 + 6, x2 - 15, y2 - 6), 24, 16, text_fill, True)


def load_today_content():
    default = {
        "category": "AUDIT REPORT",
        "badge": "AUDIT REPORT",
        "hero_title": "FLEET AUDIT REPORT",
        "hero_subtitle": "Vehicle documents insurance fitness aur permit ka clean check",
        "button": "Audit Report Support",
        "row1_title": "RC / INSURANCE AUDIT",
        "row1_desc": "Vehicle RC aur insurance document status check",
        "row2_title": "FITNESS / PERMIT REVIEW",
        "row2_desc": "Commercial vehicle fitness aur permit review",
        "row3_title": "CLEAN RISK SUMMARY",
        "row3_desc": "Fleet ka simple professional risk summary",
        "support_title": "Professional Audit Support Platform",
        "support_subtitle": "RC • Insurance • Fitness • Permit • Risk Summary",
        "hashtags": "#MetaSolwServices #AuditReport #FleetAudit #Kanpur"
    }

    rows = []

    if os.path.exists(CONTENT_FILE):
        with open(CONTENT_FILE, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("category") and row.get("hero_title"):
                    rows.append(row)

    if not rows:
        return default

    day_index = datetime.now().timetuple().tm_yday - 1
    return rows[day_index % len(rows)]


def make_caption(c):
    hero = clean(c.get("hero_title")).replace("\n", " ")

    return f"""{hero}

✅ {clean(c.get('button'))}
✅ {clean(c.get('row1_title')).replace(chr(10), ' ')}
✅ {clean(c.get('row2_title')).replace(chr(10), ' ')}
✅ {clean(c.get('row3_title')).replace(chr(10), ' ')}

Direct support chahiye? Aaj hi connect karein.
📞 WhatsApp: {PHONE}
🌐 {WEBSITE}
📍 Kanpur, Uttar Pradesh

{clean(c.get('hashtags'))}"""


def make_poster():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    c = load_today_content()

    img = background()
    d = ImageDraw.Draw(img)

    d.rounded_rectangle((34, 34, W - 34, H - 34), radius=44, outline=(255, 255, 255, 185), width=3)
    d.rounded_rectangle((52, 52, W - 52, H - 52), radius=34, outline=(*GOLD, 135), width=2)

    logo_ok = draw_logo(img)
    d = ImageDraw.Draw(img)

    d.text((170, 48), "METASOLW SERVICES", font=get_font(47, True), fill=WHITE)
    d.text((173, 105), "Everything Solved • Direct Company Platform", font=get_font(20, False), fill=GOLD2)

    badge(d, (60, 158, 370, 220), clean(c.get("badge")), GOLD, DARK, (255, 255, 255, 120))
    badge(d, (395, 158, 610, 220), datetime.now().strftime("%d %b %Y"), (*NAVY, 238), WHITE, GOLD)

    card(img, (60, 255, 1020, 560), 34, (*NAVY, 242), (*GOLD, 155), 2, True)
    d = ImageDraw.Draw(img)

    multiline_center(d, clean(c.get("hero_title")), (90, 292, 990, 365), 56, 38, WHITE, True)
    center_fit(d, clean(c.get("hero_subtitle")), (90, 370, 990, 415), 25, 18, SOFT, False)

    d.rounded_rectangle((300, 455, 780, 520), radius=34, fill=GOLD, outline=(255, 255, 255, 120), width=2)
    center_fit(d, clean(c.get("button")), (330, 465, 750, 510), 28, 20, DARK, True)

    feature_row(img, 605, clean(c.get("row1_title")), clean(c.get("row1_desc")))
    feature_row(img, 745, clean(c.get("row2_title")), clean(c.get("row2_desc")))
    feature_row(img, 885, clean(c.get("row3_title")), clean(c.get("row3_desc")))

    card(img, (60, 1045, 1020, 1175), 30, (*NAVY, 242), (*GOLD, 160), 2, True)
    d = ImageDraw.Draw(img)

    check_icon(d, 125, 1110, 31)
    center_fit(d, clean(c.get("support_title")), (190, 1062, 970, 1105), 33, 22, WHITE, True)
    center_fit(d, clean(c.get("support_subtitle")), (190, 1114, 970, 1150), 24, 16, GOLD2, True)

    card(img, (60, 1198, 1020, H - 55), 28, (*NAVY, 245), (*GOLD, 170), 2, True)
    d = ImageDraw.Draw(img)

    d.rounded_rectangle((105, 1224, 180, 1290), radius=34, outline=GOLD2, width=4)
    center(d, "WA", (118, 1236, 167, 1278), get_font(22, True), GOLD2)

    d.text((215, 1218), f"WhatsApp: {PHONE}", font=get_font(36, True), fill=WHITE)
    d.text((215, 1268), WEBSITE, font=get_font(22, False), fill=GOLD2)

    img.convert("RGB").save(POSTER_PATH, quality=96)

    with open(CAPTION_PATH, "w", encoding="utf-8") as f:
        f.write(make_caption(c))

    print("Poster created successfully:")
    print(POSTER_PATH)
    print("Caption created successfully:")
    print(CAPTION_PATH)
    print("Daily topic:", clean(c.get("category")))
    print("Logo found:", logo_ok)


if __name__ == "__main__":
    make_poster()