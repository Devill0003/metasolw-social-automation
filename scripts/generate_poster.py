from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
from datetime import datetime
import os, csv, re

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

RESAMPLE = Image.Resampling.LANCZOS if hasattr(Image, "Resampling") else Image.LANCZOS

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

def size(draw, text, f):
    b = draw.textbbox((0, 0), str(text), font=f)
    return b[2]-b[0], b[3]-b[1]

def wrap(draw, text, f, max_w):
    if "\n" in str(text):
        return str(text).split("\n")

    words = str(text).split()
    lines, line = [], ""
    for w in words:
        test = (line + " " + w).strip()
        if size(draw, test, f)[0] <= max_w:
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
        hs = [size(draw, ln, f)[1] for ln in lines]
        ws = [size(draw, ln, f)[0] for ln in lines] or [0]
        total = sum(hs) + gap * (len(lines)-1)
        if max(ws) <= max_w and total <= max_h:
            return f, lines, gap
    f = font(min_size, bold)
    return f, wrap(draw, text, f, max_w), 8

def draw_box_text(draw, text, box, max_size, min_size, fill, bold=True, align="left"):
    x1,y1,x2,y2 = box
    f, lines, gap = fit(draw, text, x2-x1, y2-y1, max_size, min_size, bold)
    hs = [size(draw, ln, f)[1] for ln in lines]
    total = sum(hs) + gap * (len(lines)-1)
    y = y1 + ((y2-y1)-total)//2

    for ln, h in zip(lines, hs):
        tw, _ = size(draw, ln, f)
        if align == "center":
            x = x1 + ((x2-x1)-tw)//2
        else:
            x = x1
        draw.text((x, y), ln, font=f, fill=fill)
        y += h + gap

def card(img, box, radius, fill, outline=None, width=2, shadow=True):
    x1,y1,x2,y2 = box

    if shadow:
        sh = Image.new("RGBA", (W,H), (0,0,0,0))
        sd = ImageDraw.Draw(sh)
        sd.rounded_rectangle((x1+10,y1+16,x2+10,y2+16), radius=radius, fill=(0,0,0,95))
        sh = sh.filter(ImageFilter.GaussianBlur(18))
        img.alpha_composite(sh)

    layer = Image.new("RGBA", (W,H), (0,0,0,0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)
    img.alpha_composite(layer)

def background():
    img = Image.new("RGBA", (W,H), (0,0,0,255))
    d = ImageDraw.Draw(img)

    top, mid, bottom = THEME["top"], THEME["mid"], THEME["bottom"]

    for y in range(H):
        t = y/H
        if t < 0.48:
            p = t/0.48
            a,b = top,mid
        else:
            p = (t-0.48)/0.52
            a,b = mid,bottom
        c = tuple(int(a[i]*(1-p)+b[i]*p) for i in range(3))
        d.line((0,y,W,y), fill=(*c,255))

    glow = Image.new("RGBA", (W,H), (0,0,0,0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((690,120,1250,690), fill=(*THEME["gold"],95))
    gd.ellipse((470,360,1120,1050), fill=(130,40,180,55))
    gd.ellipse((-360,1120,460,2020), fill=(0,180,165,28))
    glow = glow.filter(ImageFilter.GaussianBlur(40))
    img.alpha_composite(glow)

    pat = Image.new("RGBA", (W,H), (0,0,0,0))
    pd = ImageDraw.Draw(pat)

    for i in range(-H, W, 78):
        pd.line((i,0,i+H,H), fill=(255,255,255,14), width=2)

    for r in range(260, 540, 38):
        pd.arc((760-r,230-r,760+r,230+r), 305, 55, fill=(*THEME["gold"],55), width=2)

    img.alpha_composite(pat)
    return img

def load_content():
    rows = []
    if os.path.exists(CONTENT_FILE):
        with open(CONTENT_FILE, "r", encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))

    if not rows:
        return {
            "category": "INSURANCE",
            "title": "Vehicle Insurance direct company se renew karwayein",
            "subtitle": "Fast support • Transparent service • Agent free",
            "cta": "No Agent • No Commission",
            "point1": "Policy issued by Insurance Company",
            "point2": "No Agent • No Commission",
            "point3": "Policy ownership with Customer",
            "bullet1": "Free document check",
            "bullet2": "Renewal alerts",
            "bullet3": "Claim support guidance"
        }

    # Aaj test ke liye first row insurance, daily GitHub me model/theme still change hota rahega
    return rows[0]

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
    gold = (*THEME["gold"],255)
    gold2 = (*THEME["gold2"],255)

    d.ellipse((cx-72,cy-72,cx+72,cy+72), fill=(3,22,52,255), outline=gold2, width=5)
    d.ellipse((cx-62,cy-62,cx+62,cy+62), outline=gold, width=3)

    for p in logo_paths():
        if os.path.exists(p):
            try:
                lg = Image.open(p).convert("RGBA")
                lg.thumbnail((126,126), RESAMPLE)
                img.alpha_composite(lg, (cx-lg.width//2, cy-lg.height//2))
                return True
            except Exception:
                pass

    f = font(34, True)
    tw, th = size(d, "MS", f)
    d.text((cx-tw//2, cy-th//2), "MS", font=f, fill=gold2)
    return False

def model_files():
    out = []
    for i in range(1, 21):
        for ext in ["jpg", "jpeg", "png", "webp"]:
            p = os.path.join(ASSETS_DIR, f"model_{i}.{ext}")
            if os.path.exists(p):
                out.append(p)
    return out

def paste_model(img):
    models = model_files()
    if not models:
        return False

    p = models[0]

    try:
        raw = Image.open(p).convert("RGB")

        # face + upper body crop, professional right side
        photo = ImageOps.fit(raw, (545, 780), method=RESAMPLE, centering=(0.50, 0.16)).convert("RGBA")

        x, y = 548, 170

        halo = Image.new("RGBA", (W,H), (0,0,0,0))
        hd = ImageDraw.Draw(halo)
        hd.ellipse((610,195,1115,735), outline=(*THEME["gold2"],130), width=4)
        hd.ellipse((690,145,1260,780), fill=(*THEME["gold"],28))
        halo = halo.filter(ImageFilter.GaussianBlur(1))
        img.alpha_composite(halo)

        # Soft fade mask so photo blends, not hard box
        mask = Image.new("L", photo.size, 0)
        md = ImageDraw.Draw(mask)
        md.rounded_rectangle((0,0,photo.width,photo.height), radius=45, fill=255)

        # fade lower edge
        fade_h = 130
        for yy in range(photo.height - fade_h, photo.height):
            alpha = int(255 * (1 - (yy - (photo.height - fade_h)) / fade_h))
            ImageDraw.Draw(mask).line((0, yy, photo.width, yy), fill=max(alpha, 0))

        layer = Image.new("RGBA", (W,H), (0,0,0,0))
        layer.paste(photo, (x,y), mask)
        img.alpha_composite(layer)
        return True

    except Exception:
        return False

def chip(draw, box, text):
    x1,y1,x2,y2 = box
    gold = (*THEME["gold"],255)
    gold2 = (*THEME["gold2"],255)

    draw.rounded_rectangle(box, radius=(y2-y1)//2, fill=gold, outline=(255,255,255,120), width=2)

    sx, sy = x1+55, y1+15
    draw.polygon([(sx,sy),(sx+36,sy+12),(sx+31,sy+53),(sx,sy+66),(sx-31,sy+53),(sx-36,sy+12)], fill=(5,31,73))
    draw.line((sx-17,sy+36,sx-4,sy+49,sx+24,sy+20), fill=gold2, width=6)

    draw_box_text(draw, text, (x1+105,y1+9,x2-24,y2-8), 38, 22, (8,24,48,255), True, "left")

def feature_icon(draw, cx, cy, kind):
    gold2 = (*THEME["gold2"],255)
    draw.ellipse((cx-42,cy-42,cx+42,cy+42), outline=gold2, width=3, fill=(7,36,86,255))

    if kind == "direct":
        draw.polygon([(cx-16,cy-28),(cx+20,cy-15),(cx+17,cy+26),(cx,cy+36),(cx-28,cy+18),(cx-30,cy-15)], outline=gold2)
        draw.line((cx-17,cy+3,cx-4,cy+18,cx+25,cy-16), fill=gold2, width=6)
    elif kind == "zero":
        f = font(38, True)
        tw, th = size(draw, "0%", f)
        draw.text((cx-tw//2, cy-th//2-2), "0%", font=f, fill=gold2)
    else:
        draw.ellipse((cx-15,cy-25,cx+15,cy+5), fill=gold2)
        draw.arc((cx-32,cy-5,cx+32,cy+48), 205, 335, fill=gold2, width=8)

def display_headline(title):
    if "Vehicle Insurance" in title:
        return "Vehicle Insurance\ndirect company se\nrenew karwayein"
    return title

def make_caption(c):
    tags = "#MetaSolw #MetaSolwServices #EverythingSolved #VehicleInsurance #InsuranceRenewal #DirectCompanyPolicy #NoAgent #NoCommission #Kanpur #UttarPradesh #India"
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
    gold = (*THEME["gold"],255)
    gold2 = (*THEME["gold2"],255)
    card_col = (*THEME["card"],242)

    img = background()
    d = ImageDraw.Draw(img)

    d.rounded_rectangle((28,28,W-28,H-28), radius=42, outline=(255,255,255,190), width=3)
    d.rounded_rectangle((46,46,W-46,H-46), radius=34, outline=(*THEME["gold"],135), width=2)

    model_ok = paste_model(img)
    logo_ok = draw_logo(img)
    d = ImageDraw.Draw(img)

    draw_box_text(d, "METASOLW", (230,45,790,112), 68, 42, (255,255,255,255), True, "left")
    draw_box_text(d, "SERVICES", (230,115,790,182), 68, 42, (255,255,255,255), True, "left")

    tf = font(30, True)
    tag = "Everything Solved"
    tw, th = size(d, tag, tf)
    tag_x, tag_y = 325, 198
    d.line((245, tag_y+18, tag_x-25, tag_y+18), fill=gold, width=3)
    d.text((tag_x, tag_y), tag, font=tf, fill=gold2)
    d.line((tag_x+tw+25, tag_y+18, tag_x+tw+130, tag_y+18), fill=gold, width=3)

    chip(d, (42,290,445,380), c["category"].upper())

    d.line((42,462,552,462), fill=(*THEME["gold"],140), width=2)

    draw_box_text(d, display_headline(c["title"]), (42,510,608,760), 60, 40, (255,255,255,255), True, "left")

    cta_box = (42,795,540,865)
    d.rounded_rectangle(cta_box, radius=35, fill=gold, outline=(255,255,255,110), width=2)
    draw_box_text(d, c["cta"], (70,805,512,856), 32, 20, (10,24,45,255), True, "center")
    draw_box_text(d, c["subtitle"], (42,895,625,935), 24, 16, (245,245,245,255), False, "left")

    band_y = 1000
    card(img, (28,band_y,W-28,band_y+92), 18, gold, (255,255,255,110), 2, True)
    d = ImageDraw.Draw(img)
    draw_box_text(d, "PLATFORM BY METASOLW SERVICES", (70,band_y+16,W-70,band_y+76), 38, 24, (8,23,48,255), True, "center")

    fy = 1110
    box_w, box_h, gap = 325, 250, 18

    feature_data = [
        ("DIRECT", c["point1"], "direct"),
        ("ZERO", c["point2"], "zero"),
        ("CONTROL", c["point3"], "control"),
    ]

    for i, (title, body, kind) in enumerate(feature_data):
        x1 = 42 + i * (box_w + gap)
        x2 = x1 + box_w
        card(img, (x1,fy,x2,fy+box_h), 20, card_col, (*THEME["gold"],160), 2, True)
        d = ImageDraw.Draw(img)
        feature_icon(d, x1+box_w//2, fy+60, kind)
        draw_box_text(d, title, (x1+22,fy+112,x2-22,fy+160), 34, 22, gold2, True, "center")
        draw_box_text(d, body, (x1+28,fy+166,x2-28,fy+230), 23, 15, (255,255,255,255), False, "center")

    ty = 1390
    card(img, (28,ty,W-28,ty+320), 24, card_col, (*THEME["gold"],160), 2, True)
    d = ImageDraw.Draw(img)

    sx, sy = 130, ty+70
    shield = [(sx,sy),(sx+72,sy+24),(sx+66,sy+108),(sx,sy+155),(sx-66,sy+108),(sx-72,sy+24)]
    d.polygon(shield, fill=(*THEME["card2"],255), outline=gold2)
    d.line((sx-35,sy+83,sx-10,sy+112,sx+45,sy+47), fill=gold2, width=12)

    draw_box_text(d, "Policy issued directly by Insurance Company", (245,ty+42,W-70,ty+92), 32, 20, (255,255,255,255), True, "left")
    draw_box_text(d, "No Agent • No Commission • Direct Company Policy", (245,ty+100,W-70,ty+146), 30, 18, gold2, True, "left")
    d.line((245,ty+160,W-70,ty+160), fill=(*THEME["gold"],180), width=2)
    draw_box_text(d, "India's Direct Insurance Support Platform", (245,ty+172,W-70,ty+220), 27, 18, (236,236,236,255), False, "left")

    by = ty+230
    card(img, (55,by,W-55,by+72), 20, (8,40,92,150), (255,255,255,55), 1, False)
    d = ImageDraw.Draw(img)

    items = [c["bullet1"], c["bullet2"], c["bullet3"]]
    xs = [95,420,705]

    for idx, text in enumerate(items):
        x = xs[idx]
        d.ellipse((x,by+15,x+46,by+61), outline=gold2, width=3)
        d.ellipse((x+18,by+33,x+28,by+43), fill=gold2)
        draw_box_text(d, text, (x+55,by+12,x+285,by+62), 22, 15, (255,255,255,255), False, "left")
        if idx < 2:
            d.line((x+305,by+14,x+305,by+58), fill=(*THEME["gold"],120), width=2)

    foot_y = 1752
    card(img, (28,foot_y,W-28,H-52), 24, card_col, (*THEME["gold"],170), 2, True)
    d = ImageDraw.Draw(img)

    d.ellipse((90,foot_y+34,170,foot_y+114), outline=gold2, width=4)
    d.arc((112,foot_y+55,148,foot_y+90), 35, 330, fill=gold2, width=5)
    d.line((128,foot_y+88,150,foot_y+106), fill=gold2, width=5)

    draw_box_text(d, f"WhatsApp: {PHONE}", (215,foot_y+25,W-75,foot_y+86), 45, 28, (255,255,255,255), True, "left")
    draw_box_text(d, WEBSITE, (315,foot_y+90,W-110,foot_y+135), 30, 19, (255,255,255,255), False, "left")
    d.ellipse((278,foot_y+102,302,foot_y+126), outline=gold2, width=2)

    img.convert("RGB").save(POSTER_PATH, quality=96)

    with open(CAPTION_PATH, "w", encoding="utf-8") as f:
        f.write(make_caption(c))

    print("Poster created successfully:")
    print(POSTER_PATH)
    print("Caption created successfully:")
    print(CAPTION_PATH)
    print("Logo found:", logo_ok)
    print("Model found:", model_ok)
    print("Category:", c["category"])

if __name__ == "__main__":
    make_poster()