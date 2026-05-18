from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
from datetime import datetime
import csv
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
CONTENT_FILE = os.path.join(BASE_DIR, "content.csv")

LOGO_PATH = os.path.join(ASSETS_DIR, "logo.png")
MODEL_PATH = os.path.join(ASSETS_DIR, "model.jpg")

POSTER_PATH = os.path.join(OUTPUT_DIR, "status_today.png")
CAPTION_PATH = os.path.join(OUTPUT_DIR, "caption_today.txt")

W, H = 1080, 1920

def font(size, bold=False):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\calibrib.ttf" if bold else r"C:\Windows\Fonts\calibri.ttf",
    ]
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def size(draw, text, f):
    b = draw.textbbox((0, 0), str(text), font=f)
    return b[2]-b[0], b[3]-b[1]

def wrap(draw, text, f, max_w):
    words = str(text).replace("\n", " ").split()
    lines, line = [], ""
    for word in words:
        test = (line + " " + word).strip()
        if size(draw, test, f)[0] <= max_w:
            line = test
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines

def fit(draw, text, max_w, max_h, max_size, min_size, bold=True):
    for s in range(max_size, min_size-1, -2):
        f = font(s, bold)
        lines = wrap(draw, text, f, max_w)
        gap = max(8, int(s*0.22))
        hs = [size(draw, l, f)[1] for l in lines]
        ws = [size(draw, l, f)[0] for l in lines] or [0]
        total = sum(hs) + gap*(len(lines)-1)
        if total <= max_h and max(ws) <= max_w:
            return f, lines, gap
    f = font(min_size, bold)
    return f, wrap(draw, text, f, max_w), max(8, int(min_size*0.22))

def draw_text(draw, text, box, max_size, min_size, fill, bold=True, align="left"):
    x1,y1,x2,y2 = box
    f, lines, gap = fit(draw, text, x2-x1, y2-y1, max_size, min_size, bold)
    hs = [size(draw, l, f)[1] for l in lines]
    total = sum(hs) + gap*(len(lines)-1)
    y = y1 + ((y2-y1)-total)//2
    for l,h in zip(lines, hs):
        tw,_ = size(draw, l, f)
        x = x1 if align == "left" else x1 + ((x2-x1)-tw)//2
        draw.text((x,y), l, font=f, fill=fill)
        y += h + gap

def card(img, box, radius, fill, outline=None, width=2, shadow=True):
    x1,y1,x2,y2 = box
    if shadow:
        sh = Image.new("RGBA", (W,H), (0,0,0,0))
        sd = ImageDraw.Draw(sh)
        sd.rounded_rectangle((x1+12,y1+18,x2+12,y2+18), radius=radius, fill=(0,0,0,90))
        sh = sh.filter(ImageFilter.GaussianBlur(20))
        img.alpha_composite(sh)
    layer = Image.new("RGBA", (W,H), (0,0,0,0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)
    img.alpha_composite(layer)

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
        for r in csv.DictReader(f):
            if r.get("text"):
                rows.append(r)
    if not rows:
        return fallback
    r = rows[datetime.now().timetuple().tm_yday % len(rows)]
    return {
        "category": (r.get("category") or fallback["category"]).strip().upper(),
        "text": (r.get("text") or fallback["text"]).strip(),
        "cta": (r.get("cta") or fallback["cta"]).strip()
    }

def bg():
    img = Image.new("RGBA", (W,H), (0,0,0,255))
    d = ImageDraw.Draw(img)
    top = (12, 130, 95)
    mid = (12, 42, 78)
    bottom = (10, 18, 42)
    for y in range(H):
        t = y/H
        if t < .55:
            p = t/.55
            a,b = top, mid
        else:
            p = (t-.55)/.45
            a,b = mid, bottom
        c = tuple(int(a[i]*(1-p)+b[i]*p) for i in range(3))
        d.line((0,y,W,y), fill=(*c,255))

    glow = Image.new("RGBA",(W,H),(0,0,0,0))
    gd = ImageDraw.Draw(glow)
    gd.rounded_rectangle((560,260,1190,1015), radius=150, fill=(232,40,210,210))
    gd.ellipse((790,190,1070,470), fill=(255,190,82,240))
    gd.ellipse((-250,900,420,1700), fill=(0,220,180,42))
    glow = glow.filter(ImageFilter.GaussianBlur(4))
    img.alpha_composite(glow)

    pattern = Image.new("RGBA",(W,H),(0,0,0,0))
    pd = ImageDraw.Draw(pattern)
    for x in range(-H, W, 80):
        pd.line((x,0,x+H,H), fill=(255,255,255,18), width=2)
    img.alpha_composite(pattern)
    return img

def paste_logo(img):
    draw = ImageDraw.Draw(img)
    cx, cy = 95, 95
    draw.ellipse((cx-48,cy-48,cx+48,cy+48), fill=(255,255,255,240), outline=(255,210,110,255), width=3)
    if os.path.exists(LOGO_PATH):
        try:
            logo = Image.open(LOGO_PATH).convert("RGBA")
            logo.thumbnail((82,82))
            img.alpha_composite(logo, (cx-logo.width//2, cy-logo.height//2))
            return True
        except Exception:
            pass
    draw_text(draw, "MS", (cx-35,cy-25,cx+35,cy+25), 28, 20, (10,25,50,255), True, "center")
    return False

def paste_model(img):
    if not os.path.exists(MODEL_PATH):
        return False
    try:
        model = Image.open(MODEL_PATH).convert("RGB")
        model = ImageOps.fit(model, (440, 760), method=Image.Resampling.LANCZOS, centering=(0.5, 0.22)).convert("RGBA")

        mask = Image.new("L", (440,760), 0)
        md = ImageDraw.Draw(mask)
        md.rounded_rectangle((0,0,440,760), radius=55, fill=255)

        shadow = Image.new("RGBA",(W,H),(0,0,0,0))
        sd = ImageDraw.Draw(shadow)
        sd.rounded_rectangle((590,350,1030,1110), radius=55, fill=(0,0,0,120))
        shadow = shadow.filter(ImageFilter.GaussianBlur(25))
        img.alpha_composite(shadow)

        img.alpha_composite(model, (570,320), mask)
        border = Image.new("RGBA",(W,H),(0,0,0,0))
        bd = ImageDraw.Draw(border)
        bd.rounded_rectangle((570,320,1010,1080), radius=55, outline=(255,255,255,180), width=3)
        img.alpha_composite(border)
        return True
    except Exception:
        return False

def make():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    data = load_content()

    img = bg()
    draw = ImageDraw.Draw(img)

    card(img, (34,34,W-34,H-34), 48, (255,255,255,0), (255,255,255,120), 2, False)

    logo_ok = paste_logo(img)
    draw = ImageDraw.Draw(img)

    draw_text(draw, "METASOLW SERVICES", (160,54,760,105), 42, 28, (255,255,255,255), True)
    draw_text(draw, "Everything Solved • Direct Company Platform", (162,104,760,138), 20, 14, (225,248,240,255), False)

    card(img, (70,178,330,236), 28, (255,190,82,255), (255,255,255,160), 2, True)
    draw = ImageDraw.Draw(img)
    draw_text(draw, data["category"], (90,188,310,226), 30, 18, (12,28,45,255), True, "center")

    card(img, (350,178,565,236), 28, (10,35,70,225), (255,255,255,130), 2, True)
    draw = ImageDraw.Draw(img)
    draw_text(draw, datetime.now().strftime("%d %b %Y"), (370,188,545,226), 22, 14, (255,255,255,255), True, "center")

    model_ok = paste_model(img)
    draw = ImageDraw.Draw(img)

    card(img, (70,300,655,760), 50, (8,30,58,225), (255,255,255,120), 2, True)
    draw = ImageDraw.Draw(img)
    draw_text(draw, data["text"], (115,365,615,585), 62, 32, (255,255,255,255), True)

    card(img, (115,615,525,690), 36, (255,190,82,255), (255,255,255,160), 2, True)
    draw = ImageDraw.Draw(img)
    draw_text(draw, data["cta"], (140,628,500,678), 32, 18, (12,28,45,255), True, "center")

    draw_text(draw, "Fast support • Transparent service • Agent free", (116,708,625,742), 21, 13, (225,248,240,255), False)

    card(img, (70,820,1010,920), 42, (255,190,82,255), (255,255,255,170), 2, True)
    draw = ImageDraw.Draw(img)
    draw_text(draw, "PLATFORM BY METASOLW SERVICES", (110,840,970,900), 38, 22, (12,28,45,255), True, "center")

    features = [
        ("DIRECT", "Policy issued by Insurance Company"),
        ("ZERO", "No Agent • No Commission"),
        ("CONTROL", "Policy ownership with Customer"),
    ]

    fy = 980
    for i,(title,desc) in enumerate(features):
        x = 70 + i*315
        card(img, (x,fy,x+285,fy+210), 36, (8,30,58,235), (255,255,255,110), 2, True)
        draw = ImageDraw.Draw(img)
        draw_text(draw, title, (x+22,fy+28,x+263,fy+72), 28, 18, (255,218,135,255), True, "center")
        draw_text(draw, desc, (x+22,fy+88,x+263,fy+170), 22, 13, (225,248,240,255), False, "center")

    card(img, (70,1245,1010,1455), 38, (8,30,58,230), (255,255,255,90), 2, True)
    draw = ImageDraw.Draw(img)
    draw_text(draw, "Policy issued directly by Insurance Company", (110,1275,970,1320), 28, 18, (255,255,255,255), True, "center")
    draw_text(draw, "No Agent • No Commission • Direct Company Policy", (110,1330,970,1378), 28, 18, (255,218,135,255), True, "center")
    draw_text(draw, "India's Direct Insurance Support Platform", (110,1390,970,1435), 25, 16, (225,248,240,255), False, "center")

    card(img, (70,1515,1010,1690), 38, (255,255,255,28), (255,255,255,80), 1, True)
    draw = ImageDraw.Draw(img)
    bullets = ["Free document check", "Renewal alerts", "Claim support guidance"]
    for i,b in enumerate(bullets):
        yy = 1548 + i*48
        draw.ellipse((125,yy,151,yy+26), fill=(255,190,82,255))
        draw_text(draw, b, (170, yy-4, 880, yy+34), 26, 17, (255,255,255,255), False)

    card(img, (70,1745,1010,H-70), 34, (7,25,45,245), (255,255,255,100), 2, True)
    draw = ImageDraw.Draw(img)
    draw_text(draw, "WhatsApp: 6390063999", (110,1768,970,1815), 35, 24, (255,255,255,255), True, "center")
    draw_text(draw, "www.metasolwservices.in", (110,1820,970,1860), 29, 18, (255,218,135,255), False, "center")

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

    print("PRO POSTER CREATED:")
    print(POSTER_PATH)
    print("LOGO FOUND:", logo_ok)
    print("REAL MODEL FOUND:", model_ok)

if __name__ == "__main__":
    make()
