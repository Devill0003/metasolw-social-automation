from PIL import Image, ImageDraw, ImageFont, ImageFilter
from datetime import datetime
import csv
import os
import math

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ASSETS_DIR = os.path.join(BASE_DIR, "assets")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
CONTENT_FILE = os.path.join(BASE_DIR, "content.csv")

LOGO_PATH = os.path.join(ASSETS_DIR, "logo.png")
POSTER_PATH = os.path.join(OUTPUT_DIR, "status_today.png")
CAPTION_PATH = os.path.join(OUTPUT_DIR, "caption_today.txt")

W, H = 1080, 1920


def get_font(size, bold=False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\calibrib.ttf" if bold else r"C:\Windows\Fonts\calibri.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def text_size(draw, text, font):
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0], box[3] - box[1]


def wrap_text(draw, text, font, max_width):
    words = str(text).split()
    lines = []
    line = ""
    for word in words:
        test = f"{line} {word}".strip()
        if text_size(draw, test, font)[0] <= max_width:
            line = test
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def draw_center(draw, text, y, font, fill, max_width=960, line_gap=12):
    lines = wrap_text(draw, text, font, max_width)
    heights = [text_size(draw, line, font)[1] for line in lines]
    total = sum(heights) + line_gap * (len(lines) - 1)
    cy = y - total // 2

    for line, h in zip(lines, heights):
        tw, _ = text_size(draw, line, font)
        draw.text(((W - tw) // 2, cy), line, font=font, fill=fill)
        cy += h + line_gap


def draw_text_box_center(draw, text, box, font, fill, line_gap=14):
    x1, y1, x2, y2 = box
    max_width = x2 - x1
    lines = wrap_text(draw, text, font, max_width)
    heights = [text_size(draw, line, font)[1] for line in lines]
    total = sum(heights) + line_gap * (len(lines) - 1)
    cy = y1 + ((y2 - y1) - total) // 2

    for line, h in zip(lines, heights):
        tw, _ = text_size(draw, line, font)
        draw.text((x1 + (max_width - tw) // 2, cy), line, font=font, fill=fill)
        cy += h + line_gap


def rounded(layer, xy, radius, fill, outline=None, width=1):
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def shadow_card(img, xy, radius=40, fill=(10, 31, 58, 235), outline=(214, 168, 79, 180), shadow=(0, 0, 0, 120)):
    x1, y1, x2, y2 = xy

    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.rounded_rectangle((x1 + 8, y1 + 12, x2 + 8, y2 + 12), radius=radius, fill=shadow)
    sh = sh.filter(ImageFilter.GaussianBlur(18))
    img.alpha_composite(sh)

    card = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(card)
    cd.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=2)
    img.alpha_composite(card)


def create_bg():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    px = img.load()

    top = (3, 14, 31)
    mid = (8, 32, 65)
    bottom = (3, 12, 26)

    for y in range(H):
        r = y / H
        if r < 0.55:
            t = r / 0.55
            col = tuple(int(top[i] * (1 - t) + mid[i] * t) for i in range(3))
        else:
            t = (r - 0.55) / 0.45
            col = tuple(int(mid[i] * (1 - t) + bottom[i] * t) for i in range(3))
        for x in range(W):
            px[x, y] = (*col, 255)

    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((-260, 120, 520, 900), fill=(50, 150, 255, 40))
    gd.ellipse((620, -120, 1420, 730), fill=(214, 168, 79, 45))
    gd.ellipse((470, 1050, 1280, 1960), fill=(20, 120, 220, 38))
    glow = glow.filter(ImageFilter.GaussianBlur(80))
    img.alpha_composite(glow)

    return img


def load_content():
    fallback = {
        "category": "Insurance",
        "text": "Vehicle Insurance direct company se renew karwayein",
        "cta": "No Agent • No Commission"
    }

    if not os.path.exists(CONTENT_FILE):
        return fallback

    rows = []
    with open(CONTENT_FILE, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("text"):
                rows.append(row)

    if not rows:
        return fallback

    day = datetime.now().timetuple().tm_yday
    return rows[day % len(rows)]


def paste_logo(img):
    d = ImageDraw.Draw(img)
    cx, cy = W // 2, 170

    ring = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(ring)
    rd.ellipse((cx - 112, cy - 112, cx + 112, cy + 112), fill=(5, 22, 43, 245), outline=(214, 168, 79, 255), width=5)
    rd.ellipse((cx - 94, cy - 94, cx + 94, cy + 94), outline=(85, 170, 255, 110), width=2)
    img.alpha_composite(ring)

    if os.path.exists(LOGO_PATH):
        try:
            logo = Image.open(LOGO_PATH).convert("RGBA")
            logo.thumbnail((175, 175))
            lx = cx - logo.width // 2
            ly = cy - logo.height // 2
            img.alpha_composite(logo, (lx, ly))
            return
        except Exception:
            pass

    d.text((cx - 48, cy - 38), "MS", font=get_font(54, True), fill=(214, 168, 79, 255))


def draw_premium_poster():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    data = load_content()
    category = data.get("category", "Insurance").strip()
    headline = data.get("text", "Vehicle Insurance direct company se renew karwayein").strip()
    cta = data.get("cta", "No Agent • No Commission").strip()
    today = datetime.now().strftime("%d %B %Y")

    img = create_bg()
    draw = ImageDraw.Draw(img)

    gold = (214, 168, 79, 255)
    gold_light = (255, 219, 130, 255)
    white = (255, 255, 255, 255)
    soft = (218, 230, 246, 255)
    cyan = (106, 216, 255, 255)
    navy = (4, 16, 34, 255)

    # Outer premium frame
    frame = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(frame)
    fd.rounded_rectangle((38, 38, W - 38, H - 38), radius=52, outline=gold, width=5)
    fd.rounded_rectangle((58, 58, W - 58, H - 58), radius=42, outline=(87, 151, 222, 90), width=2)
    img.alpha_composite(frame)

    # Top logo and branding
    paste_logo(img)
    draw = ImageDraw.Draw(img)
    draw_center(draw, "METASOLW SERVICES", 340, get_font(56, True), gold_light, 900)
    draw_center(draw, "EVERYTHING SOLVED", 392, get_font(30, False), soft, 800)

    # Date pill
    pill = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pill)
    pd.rounded_rectangle((300, 430, 780, 500), radius=35, fill=(10, 38, 75, 235), outline=(106, 216, 255, 150), width=2)
    img.alpha_composite(pill)
    draw = ImageDraw.Draw(img)
    draw_center(draw, today, 465, get_font(31, True), white, 760)

    # Category bar
    cat_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cat_layer)
    cd.rounded_rectangle((130, 555, W - 130, 650), radius=45, fill=gold, outline=(255, 235, 160, 255), width=2)
    img.alpha_composite(cat_layer)
    draw = ImageDraw.Draw(img)
    draw_center(draw, category.upper(), 603, get_font(43, True), navy, 850)

    # Main headline card
    shadow_card(img, (88, 720, W - 88, 1138), radius=52, fill=(7, 27, 55, 238), outline=(106, 216, 255, 130))
    draw = ImageDraw.Draw(img)
    draw_text_box_center(draw, headline, (150, 775, W - 150, 1065), get_font(62, True), white, line_gap=20)

    # CTA gold strip
    cta_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cta_d = ImageDraw.Draw(cta_layer)
    cta_d.rounded_rectangle((135, 1188, W - 135, 1305), radius=52, fill=(214, 168, 79, 255), outline=(255, 234, 160, 255), width=3)
    img.alpha_composite(cta_layer)
    draw = ImageDraw.Draw(img)
    draw_text_box_center(draw, cta, (175, 1210, W - 175, 1284), get_font(40, True), navy, line_gap=10)

    # Trust cards
    trust_items = [
        ("DIRECT", "Policy issued by Insurance Company"),
        ("ZERO", "No Agent • No Commission"),
        ("CONTROL", "Policy ownership with Customer"),
    ]

    start_y = 1370
    card_w = 296
    gap = 24
    x0 = (W - (card_w * 3 + gap * 2)) // 2

    for i, (title, desc) in enumerate(trust_items):
        x = x0 + i * (card_w + gap)
        shadow_card(img, (x, start_y, x + card_w, start_y + 178), radius=35, fill=(8, 30, 58, 235), outline=(214, 168, 79, 110), shadow=(0, 0, 0, 80))
        draw = ImageDraw.Draw(img)
        draw_center(draw, title, start_y + 55, get_font(32, True), gold_light, card_w - 30)
        draw_text_box_center(draw, desc, (x + 18, start_y + 82, x + card_w - 18, start_y + 158), get_font(21, False), soft, line_gap=6)

    # Platform line
    platform = [
        "Platform by Metasolw Services",
        "Direct Company Policy • No Brokerage",
        "India's Direct Insurance Support Platform"
    ]

    y = 1600
    for line in platform:
        draw_center(draw, line, y, get_font(28, False), soft, 940)
        y += 43

    # Bottom contact card
    shadow_card(img, (80, 1722, W - 80, 1845), radius=38, fill=(4, 18, 36, 245), outline=(106, 216, 255, 110), shadow=(0, 0, 0, 100))
    draw = ImageDraw.Draw(img)
    draw_center(draw, "WhatsApp: 6390063999", 1768, get_font(38, True), white, 900)
    draw_center(draw, "www.metasolwservices.in", 1814, get_font(31, False), cyan, 900)

    img = img.convert("RGB")
    img.save(POSTER_PATH, quality=96)

    caption = f"""MetaSolw Services

{category}: {headline}

{cta}

Platform by Metasolw Services
Policy issued directly by Insurance Company
No Agent • No Commission • Direct Company Policy

Contact: 6390063999
Website: www.metasolwservices.in

#MetaSolw #EverythingSolved #{category.replace(" ", "")}"""

    with open(CAPTION_PATH, "w", encoding="utf-8") as f:
        f.write(caption)

    print("Premium poster created successfully:")
    print(POSTER_PATH)
    print("Caption created successfully:")
    print(CAPTION_PATH)


if __name__ == "__main__":
    draw_premium_poster()
