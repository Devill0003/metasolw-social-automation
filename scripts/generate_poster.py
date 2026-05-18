from PIL import Image, ImageDraw, ImageFont, ImageFilter
from datetime import datetime
import csv
import os
import math

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
CONTENT_FILE = os.path.join(BASE_DIR, "content.csv")
FESTIVAL_FILE = os.path.join(BASE_DIR, "festival_calendar.csv")

LOGO_PATH = os.path.join(ASSETS_DIR, "logo.png")
POSTER_PATH = os.path.join(OUTPUT_DIR, "status_today.png")
CAPTION_PATH = os.path.join(OUTPUT_DIR, "caption_today.txt")

W, H = 1080, 1920

# ---------------- FONTS ---------------- #

def get_font(size, bold=False):
    paths = [
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\calibrib.ttf" if bold else r"C:\Windows\Fonts\calibri.ttf",
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
    ]
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
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

def draw_multiline_center(draw, text, box, font, fill, line_gap=12):
    x1, y1, x2, y2 = box
    max_width = x2 - x1
    lines = wrap_text(draw, text, font, max_width)
    heights = [text_size(draw, line, font)[1] for line in lines]
    total_h = sum(heights) + line_gap * (len(lines) - 1)
    y = y1 + ((y2 - y1) - total_h) // 2

    for line, h in zip(lines, heights):
        tw, _ = text_size(draw, line, font)
        x = x1 + ((x2 - x1) - tw) // 2
        draw.text((x, y), line, font=font, fill=fill)
        y += h + line_gap

# ---------------- CONTENT ---------------- #

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
    row = rows[day % len(rows)]

    return {
        "category": row.get("category", "Insurance").strip() or "Insurance",
        "text": row.get("text", "Vehicle Insurance direct company se renew karwayein").strip() or "Vehicle Insurance direct company se renew karwayein",
        "cta": row.get("cta", "No Agent • No Commission").strip() or "No Agent • No Commission"
    }

def load_festival():
    today = datetime.now()
    yyyy_mm_dd = today.strftime("%Y-%m-%d")
    mm_dd = today.strftime("%m-%d")

    if not os.path.exists(FESTIVAL_FILE):
        return None

    with open(FESTIVAL_FILE, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row.get("date_key") or "").strip()
            if key == yyyy_mm_dd or key == mm_dd:
                return {
                    "festival_name": (row.get("festival_name") or "").strip(),
                    "theme_type": (row.get("theme_type") or "festive").strip().lower(),
                    "greeting_line": (row.get("greeting_line") or "").strip()
                }
    return None

# ---------------- STYLES ---------------- #

NORMAL_STYLES = [
    {
        "name": "Luxury Dark Corporate",
        "bg_top": (5, 18, 37),
        "bg_mid": (9, 40, 75),
        "bg_bottom": (3, 15, 30),
        "gold": (214, 168, 79),
        "gold_light": (255, 228, 150),
        "white": (255, 255, 255),
        "soft": (220, 232, 247),
        "cyan": (112, 220, 255),
        "navy": (5, 20, 38),
        "accent1": (40, 140, 255, 40),
        "accent2": (214, 168, 79, 45),
        "main_card": (8, 30, 58, 238),
        "footer_card": (4, 18, 36, 245),
        "cta_fill": (214, 168, 79, 255),
        "cat_fill": (214, 168, 79, 255),
        "card_outline": (106, 216, 255, 120),
        "trust_fill": (7, 29, 57, 235),
        "text_dark": (5, 20, 38)
    },
    {
        "name": "Clean White Blue",
        "bg_top": (245, 249, 255),
        "bg_mid": (226, 238, 252),
        "bg_bottom": (245, 249, 255),
        "gold": (26, 93, 184),
        "gold_light": (20, 82, 160),
        "white": (17, 44, 86),
        "soft": (32, 70, 120),
        "cyan": (0, 114, 220),
        "navy": (255, 255, 255),
        "accent1": (0, 100, 220, 35),
        "accent2": (0, 145, 255, 28),
        "main_card": (255, 255, 255, 242),
        "footer_card": (255, 255, 255, 245),
        "cta_fill": (20, 82, 160, 255),
        "cat_fill": (20, 82, 160, 255),
        "card_outline": (20, 82, 160, 90),
        "trust_fill": (255, 255, 255, 238),
        "text_dark": (255, 255, 255)
    },
    {
        "name": "Premium Gold Brand",
        "bg_top": (24, 14, 6),
        "bg_mid": (62, 35, 10),
        "bg_bottom": (21, 12, 5),
        "gold": (214, 168, 79),
        "gold_light": (255, 236, 176),
        "white": (255, 250, 238),
        "soft": (245, 228, 196),
        "cyan": (255, 204, 110),
        "navy": (34, 20, 8),
        "accent1": (255, 190, 70, 40),
        "accent2": (214, 168, 79, 55),
        "main_card": (58, 33, 11, 236),
        "footer_card": (42, 24, 8, 245),
        "cta_fill": (214, 168, 79, 255),
        "cat_fill": (214, 168, 79, 255),
        "card_outline": (255, 221, 154, 100),
        "trust_fill": (50, 30, 10, 235),
        "text_dark": (34, 20, 8)
    },
    {
        "name": "Bold Modern Sales",
        "bg_top": (11, 17, 38),
        "bg_mid": (30, 58, 112),
        "bg_bottom": (10, 17, 36),
        "gold": (255, 98, 0),
        "gold_light": (255, 180, 110),
        "white": (255, 255, 255),
        "soft": (218, 228, 248),
        "cyan": (110, 220, 255),
        "navy": (18, 26, 46),
        "accent1": (255, 98, 0, 40),
        "accent2": (0, 180, 255, 45),
        "main_card": (14, 28, 60, 236),
        "footer_card": (9, 20, 46, 245),
        "cta_fill": (255, 98, 0, 255),
        "cat_fill": (255, 98, 0, 255),
        "card_outline": (110, 220, 255, 100),
        "trust_fill": (13, 27, 58, 235),
        "text_dark": (255, 255, 255)
    },
    {
        "name": "Minimal Elegant Blue",
        "bg_top": (232, 241, 250),
        "bg_mid": (210, 226, 244),
        "bg_bottom": (232, 241, 250),
        "gold": (9, 62, 122),
        "gold_light": (9, 62, 122),
        "white": (12, 43, 84),
        "soft": (36, 78, 130),
        "cyan": (0, 132, 214),
        "navy": (255, 255, 255),
        "accent1": (0, 132, 214, 24),
        "accent2": (9, 62, 122, 24),
        "main_card": (255, 255, 255, 245),
        "footer_card": (255, 255, 255, 246),
        "cta_fill": (9, 62, 122, 255),
        "cat_fill": (9, 62, 122, 255),
        "card_outline": (9, 62, 122, 80),
        "trust_fill": (255, 255, 255, 238),
        "text_dark": (255, 255, 255)
    }
]

FESTIVAL_THEMES = {
    "patriotic": {
        "bg_top": (255, 245, 236),
        "bg_mid": (238, 247, 255),
        "bg_bottom": (236, 255, 238),
        "gold": (19, 92, 44),
        "gold_light": (255, 120, 0),
        "white": (8, 48, 95),
        "soft": (9, 88, 42),
        "cyan": (0, 116, 214),
        "navy": (255, 255, 255),
        "accent1": (255, 120, 0, 35),
        "accent2": (19, 92, 44, 35),
        "main_card": (255, 255, 255, 240),
        "footer_card": (255, 255, 255, 246),
        "cta_fill": (255, 120, 0, 255),
        "cat_fill": (19, 92, 44, 255),
        "card_outline": (0, 116, 214, 80),
        "trust_fill": (255, 255, 255, 238),
        "text_dark": (255, 255, 255)
    },
    "festive": {
        "bg_top": (52, 15, 8),
        "bg_mid": (112, 30, 8),
        "bg_bottom": (44, 13, 8),
        "gold": (255, 181, 55),
        "gold_light": (255, 230, 170),
        "white": (255, 248, 235),
        "soft": (255, 222, 180),
        "cyan": (255, 202, 112),
        "navy": (58, 20, 7),
        "accent1": (255, 160, 50, 50),
        "accent2": (255, 220, 120, 35),
        "main_card": (87, 25, 8, 236),
        "footer_card": (70, 20, 8, 245),
        "cta_fill": (255, 181, 55, 255),
        "cat_fill": (255, 181, 55, 255),
        "card_outline": (255, 230, 170, 100),
        "trust_fill": (82, 24, 8, 235),
        "text_dark": (58, 20, 7)
    },
    "celebration": {
        "bg_top": (17, 28, 65),
        "bg_mid": (39, 65, 128),
        "bg_bottom": (15, 24, 56),
        "gold": (255, 128, 0),
        "gold_light": (255, 218, 120),
        "white": (255, 255, 255),
        "soft": (216, 230, 255),
        "cyan": (124, 228, 255),
        "navy": (22, 28, 50),
        "accent1": (255, 128, 0, 40),
        "accent2": (124, 228, 255, 40),
        "main_card": (18, 32, 72, 236),
        "footer_card": (12, 24, 58, 245),
        "cta_fill": (255, 128, 0, 255),
        "cat_fill": (255, 128, 0, 255),
        "card_outline": (124, 228, 255, 100),
        "trust_fill": (17, 30, 68, 235),
        "text_dark": (255, 255, 255)
    }
}

def choose_style(festival):
    if festival:
        theme = festival.get("theme_type", "festive").lower()
        return FESTIVAL_THEMES.get(theme, FESTIVAL_THEMES["festive"]), f"Festival Theme - {theme.title()}"
    idx = datetime.now().timetuple().tm_yday % len(NORMAL_STYLES)
    style = NORMAL_STYLES[idx]
    return style, style["name"]

# ---------------- DRAW HELPERS ---------------- #

def make_bg(style):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    px = img.load()

    top = style["bg_top"]
    mid = style["bg_mid"]
    bottom = style["bg_bottom"]

    for y in range(H):
        t = y / H
        if t < 0.55:
            tt = t / 0.55
            c = tuple(int(top[i] * (1 - tt) + mid[i] * tt) for i in range(3))
        else:
            tt = (t - 0.55) / 0.45
            c = tuple(int(mid[i] * (1 - tt) + bottom[i] * tt) for i in range(3))
        for x in range(W):
            px[x, y] = (*c, 255)

    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((-250, 100, 500, 850), fill=style["accent1"])
    gd.ellipse((650, 0, 1350, 700), fill=style["accent2"])
    gd.ellipse((450, 1200, 1250, 1950), fill=style["accent1"])
    glow = glow.filter(ImageFilter.GaussianBlur(85))
    img.alpha_composite(glow)

    # subtle diagonal pattern
    pattern = Image.new("RGBA", (W, H), (0,0,0,0))
    pd = ImageDraw.Draw(pattern)
    for i in range(-H, W, 70):
        pd.line((i, 0, i + H, H), fill=(255,255,255,12), width=2)
    pattern = pattern.filter(ImageFilter.GaussianBlur(1))
    img.alpha_composite(pattern)

    return img

def shadow_card(img, box, style, radius=38, fill=None, outline=None):
    x1, y1, x2, y2 = box

    if fill is None:
        fill = style["main_card"]
    if outline is None:
        outline = style["card_outline"]

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((x1 + 8, y1 + 12, x2 + 8, y2 + 12), radius=radius, fill=(0, 0, 0, 100))
    shadow = shadow.filter(ImageFilter.GaussianBlur(18))
    img.alpha_composite(shadow)

    card = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(card)
    cd.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=2)
    img.alpha_composite(card)

def paste_logo(img, style):
    draw = ImageDraw.Draw(img)
    cx = W // 2
    cy = 178

    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse((cx - 115, cy - 115, cx + 115, cy + 115), fill=(5, 22, 43, 245), outline=(*style["gold"], 255), width=5)
    d.ellipse((cx - 95, cy - 95, cx + 95, cy + 95), outline=(*style["cyan"], 90), width=2)
    img.alpha_composite(layer)

    if os.path.exists(LOGO_PATH):
        try:
            logo = Image.open(LOGO_PATH).convert("RGBA")
            logo.thumbnail((170, 170))
            lx = cx - logo.width // 2
            ly = cy - logo.height // 2
            img.alpha_composite(logo, (lx, ly))
            return True
        except Exception:
            pass

    draw.text((cx - 45, cy - 30), "MS", font=get_font(52, True), fill=(*style["gold"], 255))
    return False

def draw_premium_poster():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    content = load_content()
    festival = load_festival()
    style, style_name = choose_style(festival)

    category = content["category"]
    headline = content["text"]
    cta = content["cta"]
    today = datetime.now().strftime("%d %B %Y")

    festival_name = festival["festival_name"] if festival else ""
    greeting_line = festival["greeting_line"] if festival else ""

    img = make_bg(style)
    draw = ImageDraw.Draw(img)

    gold = (*style["gold"], 255)
    gold_light = (*style["gold_light"], 255)
    white = (*style["white"], 255)
    soft = (*style["soft"], 255)
    cyan = (*style["cyan"], 255)
    navy = (*style["navy"], 255)
    text_dark = (*style["text_dark"], 255)

    # outer premium frame
    frame = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(frame)
    fd.rounded_rectangle((40, 40, W - 40, H - 40), radius=52, outline=gold, width=5)
    fd.rounded_rectangle((58, 58, W - 58, H - 58), radius=42, outline=(*style["cyan"], 90), width=2)
    img.alpha_composite(frame)

    logo_found = paste_logo(img, style)
    draw = ImageDraw.Draw(img)

    # branding
    draw_multiline_center(draw, "METASOLW SERVICES", (120, 300, W - 120, 370), get_font(54, True), gold_light)
    draw_multiline_center(draw, "EVERYTHING SOLVED", (180, 370, W - 180, 415), get_font(28, False), soft)

    # festival ribbon
    if festival:
        ribbon = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        rd = ImageDraw.Draw(ribbon)
        rd.rounded_rectangle((140, 432, W - 140, 522), radius=40, fill=(*style["cta_fill"][:3], 255), outline=(255, 255, 255, 120), width=2)
        img.alpha_composite(ribbon)
        draw = ImageDraw.Draw(img)
        festive_text = f"{greeting_line} • {festival_name}"
        draw_multiline_center(draw, festive_text, (165, 445, W - 165, 508), get_font(32, True), text_dark)
        date_top = 542
    else:
        date_top = 432

    # date pill
    pill = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pill)
    pd.rounded_rectangle((315, date_top, 765, date_top + 70), radius=34, fill=(10, 38, 75, 230), outline=(*style["cyan"], 120), width=2)
    img.alpha_composite(pill)
    draw = ImageDraw.Draw(img)
    draw_multiline_center(draw, today, (330, date_top + 10, 750, date_top + 60), get_font(30, True), (255,255,255,255))

    # category bar
    cat_y1 = date_top + 125
    cat_y2 = cat_y1 + 90
    cat = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cat)
    cd.rounded_rectangle((140, cat_y1, W - 140, cat_y2), radius=42, fill=(*style["cat_fill"][:3], 255), outline=(255, 238, 165, 180), width=2)
    img.alpha_composite(cat)
    draw = ImageDraw.Draw(img)
    draw_multiline_center(draw, category.upper(), (170, cat_y1 + 10, W - 170, cat_y2 - 10), get_font(42, True), text_dark)

    # main headline card
    head_y1 = cat_y2 + 65
    head_y2 = head_y1 + 395
    shadow_card(img, (85, head_y1, W - 85, head_y2), style, radius=48, fill=style["main_card"], outline=style["card_outline"])
    draw = ImageDraw.Draw(img)
    draw_multiline_center(draw, headline, (145, head_y1 + 70, W - 145, head_y2 - 65), get_font(58, True), white, line_gap=18)

    # CTA strip
    cta_y1 = head_y2 + 55
    cta_y2 = cta_y1 + 113
    cta_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ctd = ImageDraw.Draw(cta_layer)
    ctd.rounded_rectangle((130, cta_y1, W - 130, cta_y2), radius=50, fill=(*style["cta_fill"][:3], 255), outline=(255, 237, 160, 200), width=3)
    img.alpha_composite(cta_layer)
    draw = ImageDraw.Draw(img)
    draw_multiline_center(draw, cta, (160, cta_y1 + 15, W - 160, cta_y2 - 15), get_font(38, True), text_dark)

    # trust cards
    titles = [
        ("DIRECT", "Policy issued by Insurance Company"),
        ("ZERO", "No Agent • No Commission"),
        ("CONTROL", "Policy ownership with Customer")
    ]

    start_y = cta_y2 + 72
    card_w = 295
    gap = 28
    start_x = (W - (card_w * 3 + gap * 2)) // 2

    for i, (t, desc) in enumerate(titles):
        x1 = start_x + i * (card_w + gap)
        x2 = x1 + card_w
        shadow_card(img, (x1, start_y, x2, start_y + 178), style, radius=34, fill=style["trust_fill"], outline=style["card_outline"])
        draw = ImageDraw.Draw(img)
        draw_multiline_center(draw, t, (x1 + 10, start_y + 20, x2 - 10, start_y + 72), get_font(31, True), gold_light)
        draw_multiline_center(draw, desc, (x1 + 16, start_y + 78, x2 - 16, start_y + 156), get_font(21, False), soft, line_gap=6)

    # platform lines
    platform_lines = [
        "Platform by Metasolw Services",
        "Direct Company Policy • No Brokerage",
        "India's Direct Insurance Support Platform"
    ]
    if festival:
        platform_lines[0] = f"{festival_name} Special by Metasolw Services"

    yy = start_y + 225
    for line in platform_lines:
        draw_multiline_center(draw, line, (100, yy - 15, W - 100, yy + 20), get_font(28, False), soft)
        yy += 42

    # footer card
    foot_y1 = H - 200
    foot_y2 = H - 75
    shadow_card(img, (80, foot_y1, W - 80, foot_y2), style, radius=36, fill=style["footer_card"], outline=style["card_outline"])
    draw = ImageDraw.Draw(img)
    draw_multiline_center(draw, "WhatsApp: 6390063999", (140, foot_y1 + 18, W - 140, foot_y1 + 63), get_font(37, True), white)
    draw_multiline_center(draw, "www.metasolwservices.in", (140, foot_y1 + 65, W - 140, foot_y2 - 8), get_font(30, False), cyan)

    img = img.convert("RGB")
    img.save(POSTER_PATH, quality=96)

    if festival:
        caption = f"""{greeting_line}

{festival_name} Special from MetaSolw Services

{category}: {headline}

{cta}

Platform by Metasolw Services
Policy issued directly by Insurance Company
No Agent • No Commission • Direct Company Policy

Contact: 6390063999
Website: www.metasolwservices.in

#MetaSolw #EverythingSolved #{festival_name.replace(" ", "")} #{category.replace(" ", "")}
"""
    else:
        caption = f"""MetaSolw Services

{category}: {headline}

{cta}

Platform by Metasolw Services
Policy issued directly by Insurance Company
No Agent • No Commission • Direct Company Policy

Contact: 6390063999
Website: www.metasolwservices.in

#MetaSolw #EverythingSolved #{category.replace(" ", "")}
"""

    with open(CAPTION_PATH, "w", encoding="utf-8") as f:
        f.write(caption)

    print("SMART POSTER CREATED SUCCESSFULLY:")
    print(POSTER_PATH)
    print("CAPTION CREATED SUCCESSFULLY:")
    print(CAPTION_PATH)
    print("LOGO FOUND:", logo_found)
    print("STYLE USED:", style_name)
    print("FESTIVAL MATCHED:", festival["festival_name"] if festival else "None")
    print("FESTIVAL FILE:", FESTIVAL_FILE)

if __name__ == "__main__":
    draw_premium_poster()
