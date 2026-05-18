from PIL import Image, ImageDraw, ImageFont, ImageFilter
from datetime import datetime
import csv
import os
import math
import random

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
CONTENT_FILE = os.path.join(BASE_DIR, "content.csv")
FESTIVAL_FILE = os.path.join(BASE_DIR, "festival_calendar.csv")

LOGO_PATH = os.path.join(ASSETS_DIR, "logo.png")
POSTER_PATH = os.path.join(OUTPUT_DIR, "status_today.png")
CAPTION_PATH = os.path.join(OUTPUT_DIR, "caption_today.txt")

W, H = 1080, 1920

def font(size, bold=False):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\calibrib.ttf" if bold else r"C:\Windows\Fonts\calibri.ttf",
    ]
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def tsize(draw, text, f):
    b = draw.textbbox((0,0), str(text), font=f)
    return b[2]-b[0], b[3]-b[1]

def wrap_text(draw, text, f, max_w):
    words = str(text).replace("\n", " ").split()
    lines, line = [], ""
    for w in words:
        test = (line + " " + w).strip()
        if tsize(draw, test, f)[0] <= max_w:
            line = test
        else:
            if line:
                lines.append(line)
            line = w
    if line:
        lines.append(line)
    return lines

def fit_text(draw, text, max_w, max_h, max_size, min_size, bold=False):
    for s in range(max_size, min_size - 1, -2):
        f = font(s, bold)
        lines = wrap_text(draw, text, f, max_w)
        gap = max(4, int(s * 0.25))
        widths = [tsize(draw, ln, f)[0] for ln in lines] or [0]
        heights = [tsize(draw, ln, f)[1] for ln in lines] or [0]
        total_h = sum(heights) + gap * (len(lines) - 1)
        if max(widths) <= max_w and total_h <= max_h:
            return f, lines, gap
    f = font(min_size, bold)
    return f, wrap_text(draw, text, f, max_w), max(4, int(min_size * 0.25))

def draw_centered_text(draw, text, box, max_size, min_size, fill, bold=False):
    x1, y1, x2, y2 = box
    f, lines, gap = fit_text(draw, text, x2-x1, y2-y1, max_size, min_size, bold)
    hs = [tsize(draw, ln, f)[1] for ln in lines]
    total_h = sum(hs) + gap * (len(lines)-1)
    y = y1 + ((y2-y1) - total_h) // 2
    for ln, h in zip(lines, hs):
        tw, _ = tsize(draw, ln, f)
        x = x1 + ((x2-x1) - tw) // 2
        draw.text((x, y), ln, font=f, fill=fill)
        y += h + gap

def draw_left_text(draw, text, box, max_size, min_size, fill, bold=False):
    x1, y1, x2, y2 = box
    f, lines, gap = fit_text(draw, text, x2-x1, y2-y1, max_size, min_size, bold)
    hs = [tsize(draw, ln, f)[1] for ln in lines]
    total_h = sum(hs) + gap * (len(lines)-1)
    y = y1 + ((y2-y1) - total_h) // 2
    for ln, h in zip(lines, hs):
        draw.text((x1, y), ln, font=f, fill=fill)
        y += h + gap

def rounded_card(img, box, radius, fill, outline=None, width=2, shadow=True):
    x1, y1, x2, y2 = box
    if shadow:
        sh = Image.new("RGBA", (W, H), (0,0,0,0))
        sd = ImageDraw.Draw(sh)
        sd.rounded_rectangle((x1+10, y1+16, x2+10, y2+16), radius=radius, fill=(0,0,0,95))
        sh = sh.filter(ImageFilter.GaussianBlur(18))
        img.alpha_composite(sh)

    layer = Image.new("RGBA", (W, H), (0,0,0,0))
    ld = ImageDraw.Draw(layer)
    ld.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)
    img.alpha_composite(layer)

def gradient_background(style):
    img = Image.new("RGBA", (W, H), (0,0,0,255))
    d = ImageDraw.Draw(img)

    top = style["bg_top"]
    mid = style["bg_mid"]
    bottom = style["bg_bottom"]

    for y in range(H):
        t = y / H
        if t < 0.55:
            p = t / 0.55
            c = tuple(int(top[i] * (1-p) + mid[i] * p) for i in range(3))
        else:
            p = (t - 0.55) / 0.45
            c = tuple(int(mid[i] * (1-p) + bottom[i] * p) for i in range(3))
        d.line((0, y, W, y), fill=(*c, 255))

    glow = Image.new("RGBA", (W, H), (0,0,0,0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((-220, 120, 470, 820), fill=style["glow1"])
    gd.ellipse((650, -120, 1320, 520), fill=style["glow2"])
    gd.ellipse((420, 1120, 1220, 1940), fill=style["glow3"])
    glow = glow.filter(ImageFilter.GaussianBlur(85))
    img.alpha_composite(glow)

    lines = Image.new("RGBA", (W, H), (0,0,0,0))
    ld = ImageDraw.Draw(lines)
    for x in range(-H, W, 70):
        ld.line((x, 0, x+H, H), fill=(255,255,255,12), width=2)
    img.alpha_composite(lines)

    return img

STYLES = [
    {
        "name": "Royal Navy Gold",
        "bg_top": (4, 16, 38),
        "bg_mid": (10, 39, 84),
        "bg_bottom": (3, 14, 32),
        "primary": (217, 170, 67),
        "primary2": (255, 232, 168),
        "accent": (96, 204, 255),
        "white": (255,255,255),
        "soft": (224,236,249),
        "dark": (8, 22, 43),
        "card": (7, 27, 59, 240),
        "card2": (8, 31, 68, 236),
        "footer": (5, 20, 42, 245),
        "glow1": (90, 196, 255, 36),
        "glow2": (217, 170, 67, 46),
        "glow3": (42, 122, 224, 34),
        "skin": (224, 180, 145),
        "shirt": (244, 248, 255),
        "suit": (10, 28, 68),
        "tie": (217, 170, 67),
        "hair": (25, 17, 10)
    },
    {
        "name": "Modern Orange Blue",
        "bg_top": (5, 19, 46),
        "bg_mid": (16, 57, 120),
        "bg_bottom": (6, 20, 48),
        "primary": (255, 115, 22),
        "primary2": (255, 206, 145),
        "accent": (116, 222, 255),
        "white": (255,255,255),
        "soft": (228,236,252),
        "dark": (255,255,255),
        "card": (9, 31, 72, 240),
        "card2": (10, 36, 78, 236),
        "footer": (7, 24, 58, 245),
        "glow1": (255, 115, 22, 40),
        "glow2": (116, 222, 255, 34),
        "glow3": (255, 115, 22, 30),
        "skin": (229, 188, 156),
        "shirt": (250, 251, 255),
        "suit": (12, 38, 85),
        "tie": (255, 115, 22),
        "hair": (28, 18, 12)
    },
    {
        "name": "Executive Black Gold",
        "bg_top": (15, 12, 9),
        "bg_mid": (48, 31, 14),
        "bg_bottom": (12, 9, 8),
        "primary": (226, 180, 78),
        "primary2": (255, 235, 182),
        "accent": (255, 210, 115),
        "white": (255, 250, 241),
        "soft": (245, 228, 198),
        "dark": (31, 19, 9),
        "card": (45, 30, 15, 240),
        "card2": (52, 34, 16, 236),
        "footer": (34, 22, 11, 245),
        "glow1": (255, 190, 92, 35),
        "glow2": (226, 180, 78, 45),
        "glow3": (255, 195, 95, 28),
        "skin": (220, 175, 142),
        "shirt": (248, 244, 238),
        "suit": (33, 23, 14),
        "tie": (226, 180, 78),
        "hair": (22, 14, 9)
    },
    {
        "name": "Premium White Blue",
        "bg_top": (244, 249, 255),
        "bg_mid": (226, 238, 252),
        "bg_bottom": (247, 250, 255),
        "primary": (18, 80, 163),
        "primary2": (0, 123, 217),
        "accent": (31, 155, 255),
        "white": (13, 38, 80),
        "soft": (52, 84, 125),
        "dark": (255,255,255),
        "card": (255,255,255,246),
        "card2": (255,255,255,240),
        "footer": (255,255,255,250),
        "glow1": (0, 118, 210, 28),
        "glow2": (18, 80, 163, 24),
        "glow3": (31, 155, 255, 20),
        "skin": (225, 183, 150),
        "shirt": (255,255,255),
        "suit": (18, 80, 163),
        "tie": (31, 155, 255),
        "hair": (30, 19, 12)
    }
]

FESTIVE_STYLE = {
    "name": "Festival Corporate",
    "bg_top": (68, 20, 11),
    "bg_mid": (118, 36, 14),
    "bg_bottom": (48, 16, 10),
    "primary": (255, 188, 66),
    "primary2": (255, 231, 170),
    "accent": (255, 214, 120),
    "white": (255, 248, 232),
    "soft": (255, 231, 190),
    "dark": (74, 26, 10),
    "card": (92, 30, 12, 238),
    "card2": (82, 25, 11, 234),
    "footer": (62, 20, 10, 245),
    "glow1": (255, 186, 62, 48),
    "glow2": (255, 226, 130, 40),
    "glow3": (255, 156, 62, 28),
    "skin": (225, 183, 150),
    "shirt": (255, 247, 240),
    "suit": (112, 42, 18),
    "tie": (255, 188, 66),
    "hair": (28, 18, 10)
}

def load_content():
    fallback = {
        "category": "INSURANCE",
        "text": "Vehicle Insurance direct company se renew karwayein",
        "cta": "No Agent • No Commission"
    }
    if not os.path.exists(CONTENT_FILE):
        return fallback

    rows = []
    with open(CONTENT_FILE, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for r in reader:
            if r.get("text"):
                rows.append(r)

    if not rows:
        return fallback

    idx = datetime.now().timetuple().tm_yday % len(rows)
    r = rows[idx]
    return {
        "category": (r.get("category") or fallback["category"]).strip().upper(),
        "text": (r.get("text") or fallback["text"]).strip(),
        "cta": (r.get("cta") or fallback["cta"]).strip()
    }

def load_festival():
    today_full = datetime.now().strftime("%Y-%m-%d")
    today_md = datetime.now().strftime("%m-%d")
    if not os.path.exists(FESTIVAL_FILE):
        return None

    with open(FESTIVAL_FILE, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for r in reader:
            key = (r.get("date_key") or "").strip()
            if key in [today_full, today_md]:
                return {
                    "festival_name": (r.get("festival_name") or "").strip(),
                    "theme_type": (r.get("theme_type") or "festive").strip().lower(),
                    "greeting_line": (r.get("greeting_line") or "").strip()
                }
    return None

def choose_style(festival):
    if festival:
        return FESTIVE_STYLE
    return STYLES[datetime.now().timetuple().tm_yday % len(STYLES)]

def paste_logo(img, style):
    cx, cy = 150, 145
    layer = Image.new("RGBA", (W,H), (0,0,0,0))
    d = ImageDraw.Draw(layer)
    d.ellipse((cx-62, cy-62, cx+62, cy+62), fill=(7,25,52,250), outline=(*style["primary"],255), width=4)
    img.alpha_composite(layer)

    if os.path.exists(LOGO_PATH):
        try:
            logo = Image.open(LOGO_PATH).convert("RGBA")
            logo.thumbnail((100,100))
            img.alpha_composite(logo, (cx-logo.width//2, cy-logo.height//2))
            return True
        except Exception:
            pass

    d = ImageDraw.Draw(img)
    f = font(28, True)
    tw, th = tsize(d, "MS", f)
    d.text((cx-tw//2, cy-th//2), "MS", font=f, fill=(*style["primary2"],255))
    return False

def draw_badge(draw, style, x, y, text):
    fill = (*style["primary"],255)
    txt = (*style["dark"],255)
    box = (x, y, x+220, y+52)
    draw.rounded_rectangle(box, radius=24, fill=fill)
    draw_centered_text(draw, text, box, 22, 15, txt, True)

def draw_model(img, style, x, y, scale=1.0, female=False):
    layer = Image.new("RGBA", (W,H), (0,0,0,0))
    d = ImageDraw.Draw(layer)

    skin = (*style["skin"],255)
    suit = (*style["suit"],255)
    shirt = (*style["shirt"],255)
    tie = (*style["tie"],255)
    hair = (*style["hair"],255)
    outline = (255,255,255,35)

    # shadow
    d.ellipse((x+35, y+450, x+305, y+505), fill=(0,0,0,70))

    # back glow
    d.ellipse((x-20, y+30, x+330, y+580), fill=(*style["accent"], 28))
    d.ellipse((x+10, y+65, x+300, y+530), fill=(*style["primary"], 18))

    # head
    d.ellipse((x+95, y+15, x+225, y+145), fill=skin, outline=outline, width=2)

    # hair
    if female:
        d.pieslice((x+82, y+0, x+240, y+165), start=180, end=360, fill=hair)
        d.rounded_rectangle((x+78, y+44, x+110, y+180), radius=18, fill=hair)
        d.rounded_rectangle((x+210, y+44, x+242, y+180), radius=18, fill=hair)
    else:
        d.pieslice((x+88, y-4, x+232, y+132), start=180, end=360, fill=hair)

    # neck
    d.rounded_rectangle((x+136, y+128, x+184, y+176), radius=16, fill=skin)

    # torso / suit
    d.rounded_rectangle((x+68, y+168, x+252, y+420), radius=44, fill=suit, outline=outline, width=2)

    # shoulders
    d.rounded_rectangle((x+40, y+195, x+282, y+282), radius=38, fill=suit)
    d.rounded_rectangle((x+20, y+222, x+96, y+370), radius=32, fill=suit)
    d.rounded_rectangle((x+226, y+222, x+302, y+370), radius=32, fill=suit)

    # shirt
    d.polygon([(x+118,y+175),(x+202,y+175),(x+178,y+250),(x+142,y+250)], fill=shirt)
    d.polygon([(x+142,y+250),(x+178,y+250),(x+192,y+404),(x+128,y+404)], fill=shirt)

    # tie
    d.polygon([(x+149,y+184),(x+171,y+184),(x+183,y+232),(x+159,y+255),(x+137,y+232)], fill=tie)
    d.polygon([(x+159,y+255),(x+178,y+255),(x+169,y+365),(x+149,y+365),(x+140,y+255)], fill=tie)

    # lapels
    d.polygon([(x+92,y+184),(x+142,y+184),(x+123,y+258)], fill=(max(style["suit"][0]-12,0), max(style["suit"][1]-12,0), max(style["suit"][2]-12,0),255))
    d.polygon([(x+228,y+184),(x+178,y+184),(x+197,y+258)], fill=(max(style["suit"][0]-12,0), max(style["suit"][1]-12,0), max(style["suit"][2]-12,0),255))

    # hands
    d.ellipse((x+10, y+332, x+52, y+374), fill=skin)
    d.ellipse((x+270, y+332, x+312, y+374), fill=skin)

    # one arm holding folder
    d.rounded_rectangle((x+220, y+250, x+296, y+370), radius=28, fill=suit)
    d.rounded_rectangle((x+208, y+286, x+292, y+398), radius=16, fill=(255,255,255,245), outline=(*style["primary"],200), width=3)
    d.rectangle((x+224, y+308, x+276, y+316), fill=(*style["accent"],180))
    d.rectangle((x+224, y+330, x+276, y+336), fill=(190,200,220,150))
    d.rectangle((x+224, y+346, x+266, y+352), fill=(190,200,220,120))

    # body details
    d.line((x+160, y+262, x+160, y+400), fill=(255,255,255,45), width=2)
    d.ellipse((x+126, y+292, x+136, y+302), fill=(*style["primary2"],255))
    d.ellipse((x+126, y+324, x+136, y+334), fill=(*style["primary2"],255))

    # legs
    d.rounded_rectangle((x+100, y+410, x+145, y+520), radius=18, fill=suit)
    d.rounded_rectangle((x+175, y+410, x+220, y+520), radius=18, fill=suit)
    d.rounded_rectangle((x+88, y+506, x+152, y+530), radius=12, fill=(16,16,18,255))
    d.rounded_rectangle((x+163, y+506, x+227, y+530), radius=12, fill=(16,16,18,255))

    layer = layer.filter(ImageFilter.GaussianBlur(0.15))
    img.alpha_composite(layer)

def make_poster():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    data = load_content()
    festival = load_festival()
    style = choose_style(festival)

    img = gradient_background(style)
    draw = ImageDraw.Draw(img)

    primary = (*style["primary"],255)
    primary2 = (*style["primary2"],255)
    accent = (*style["accent"],255)
    white = (*style["white"],255)
    soft = (*style["soft"],255)
    dark = (*style["dark"],255)

    # Main frame
    frame = Image.new("RGBA", (W,H), (0,0,0,0))
    fd = ImageDraw.Draw(frame)
    fd.rounded_rectangle((36,36,W-36,H-36), radius=54, outline=primary, width=5)
    fd.rounded_rectangle((54,54,W-54,H-54), radius=42, outline=(*style["accent"],110), width=2)
    img.alpha_composite(frame)

    logo_found = paste_logo(img, style)
    draw = ImageDraw.Draw(img)

    # Brand header
    draw_left_text(draw, "METASOLW SERVICES", (240, 92, 820, 145), 48, 34, primary2, True)
    draw_left_text(draw, "Everything Solved", (242, 142, 740, 180), 24, 18, soft, False)

    # Festival chip
    top_y = 200
    if festival:
        rounded_card(img, (70, top_y, W-70, top_y+78), 32, (*style["primary"],255), (255,255,255,150), 2, True)
        draw_centered_text(draw, festival.get("greeting_line","") + " • " + festival.get("festival_name",""), (100, top_y+10, W-100, top_y+68), 30, 18, dark, True)
        top_y += 95

    # top date + category
    rounded_card(img, (72, top_y, 470, top_y+62), 28, style["card2"], (*style["accent"],120), 2, True)
    draw_centered_text(draw, datetime.now().strftime("%d %B %Y"), (90, top_y+8, 452, top_y+54), 26, 18, white, True)

    rounded_card(img, (72, top_y+78, 470, top_y+158), 36, (*style["primary"],255), (255,255,255,155), 2, True)
    draw_centered_text(draw, data["category"], (98, top_y+92, 444, top_y+146), 36, 24, dark, True)

    # Right top model area
    rounded_card(img, (560, top_y-5, 985, top_y+450), 48, style["card"], (*style["accent"],110), 2, True)
    female = (datetime.now().day % 2 == 0)
    draw_model(img, style, 620, top_y+10, 1.0, female)
    draw = ImageDraw.Draw(img)

    # model label
    draw_badge(draw, style, 660, top_y+368, "DIRECT SERVICE")
    draw_badge(draw, style, 660, top_y+430, "AGENT FREE")

    # Main content card
    body_y = top_y + 190
    rounded_card(img, (72, body_y, 1008, body_y+355), 52, style["card"], (*style["accent"],110), 2, True)
    draw_left_text(draw, data["text"], (120, body_y+54, 620, body_y+250), 56, 28, white, True)

    # CTA pill
    rounded_card(img, (118, body_y+250, 610, body_y+320), 34, (*style["primary"],255), (255,255,255,150), 2, True)
    draw_centered_text(draw, data["cta"], (140, body_y+260, 588, body_y+308), 30, 18, dark, True)

    # Small feature line
    draw_left_text(draw, "Fast support • Direct company policy • Transparent assistance", (122, body_y+320, 700, body_y+348), 20, 14, soft, False)

    # Mid strip
    mid_y = body_y + 392
    rounded_card(img, (72, mid_y, 1008, mid_y+86), 38, (*style["primary"],255), (255,255,255,160), 2, True)
    draw_centered_text(draw, "PLATFORM BY METASOLW SERVICES", (100, mid_y+14, 980, mid_y+70), 34, 22, dark, True)

    # Feature cards
    features = [
        ("DIRECT", "Policy issued by Insurance Company"),
        ("ZERO", "No Agent • No Commission"),
        ("CONTROL", "Customer policy ownership")
    ]

    fy = mid_y + 130
    card_w = 280
    gap = 40
    start_x = 80

    for i, (title, desc) in enumerate(features):
        x1 = start_x + i * (card_w + gap)
        x2 = x1 + card_w
        rounded_card(img, (x1, fy, x2, fy+205), 34, style["card2"], (*style["accent"],110), 2, True)
        draw_centered_text(draw, title, (x1+20, fy+26, x2-20, fy+72), 28, 18, primary2, True)
        draw_centered_text(draw, desc, (x1+22, fy+86, x2-22, fy+172), 22, 14, soft, False)

    # Bottom body block
    b2y = fy + 238
    rounded_card(img, (72, b2y, 1008, b2y+170), 36, style["card2"], (*style["accent"],100), 2, True)
    draw_centered_text(draw, "Policy issued directly by Insurance Company", (110, b2y+20, 970, b2y+58), 26, 18, white, True)
    draw_centered_text(draw, "No Agent • No Commission • Direct Company Policy", (110, b2y+60, 970, b2y+96), 26, 18, primary2, True)
    draw_centered_text(draw, "India's Direct Insurance Support Platform", (110, b2y+104, 970, b2y+140), 24, 16, soft, False)

    # Footer
    foot_y = H - 190
    rounded_card(img, (72, foot_y, 1008, H-72), 34, style["footer"], (*style["accent"],110), 2, True)
    draw_centered_text(draw, "WhatsApp: 6390063999", (100, foot_y+24, 980, foot_y+70), 34, 24, white, True)
    draw_centered_text(draw, "www.metasolwservices.in", (100, foot_y+76, 980, foot_y+114), 28, 18, accent, False)

    img = img.convert("RGB")
    img.save(POSTER_PATH, quality=96)

    caption = f"""MetaSolw Services

{data["category"]}: {data["text"]}

{data["cta"]}

Platform by Metasolw Services
Policy issued directly by Insurance Company
No Agent • No Commission • Direct Company Policy

WhatsApp: 6390063999
Website: www.metasolwservices.in

#MetaSolw #EverythingSolved #{data["category"].replace(" ", "")}
"""

    with open(CAPTION_PATH, "w", encoding="utf-8") as f:
        f.write(caption)

    print("SMART MODEL POSTER CREATED:")
    print(POSTER_PATH)
    print("LOGO FOUND:", logo_found)
    print("STYLE:", style["name"])
    print("CAPTION:", CAPTION_PATH)

if __name__ == "__main__":
    make_poster()
