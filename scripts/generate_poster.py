from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import csv
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ASSETS_DIR = os.path.join(BASE_DIR, "assets")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
CONTENT_FILE = os.path.join(BASE_DIR, "content.csv")

LOGO_PATH = os.path.join(ASSETS_DIR, "logo.png")
POSTER_PATH = os.path.join(OUTPUT_DIR, "status_today.png")
CAPTION_PATH = os.path.join(OUTPUT_DIR, "caption_today.txt")

W, H = 1080, 1920


def font(size, bold=False):
    possible_fonts = [
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\calibrib.ttf" if bold else r"C:\Windows\Fonts\calibri.ttf",
    ]

    for f in possible_fonts:
        if os.path.exists(f):
            return ImageFont.truetype(f, size)

    return ImageFont.load_default()


def draw_centered(draw, text, y, fnt, fill, max_width=960, line_gap=12):
    lines = []
    words = text.split()
    current = ""

    for word in words:
        test = current + " " + word if current else word
        bbox = draw.textbbox((0, 0), test, font=fnt)
        if bbox[2] - bbox[0] <= max_width:
            current = test
        else:
            lines.append(current)
            current = word

    if current:
        lines.append(current)

    total_height = 0
    line_heights = []

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=fnt)
        h = bbox[3] - bbox[1]
        line_heights.append(h)
        total_height += h + line_gap

    total_height -= line_gap
    start_y = y - total_height // 2

    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=fnt)
        text_w = bbox[2] - bbox[0]
        x = (W - text_w) // 2
        draw.text((x, start_y), line, font=fnt, fill=fill)
        start_y += line_heights[i] + line_gap


def rounded_rectangle(draw, xy, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def load_content():
    if not os.path.exists(CONTENT_FILE):
        return {
            "category": "Insurance",
            "text": "Vehicle Insurance direct company se renew karwayein",
            "cta": "No Agent • No Commission"
        }

    rows = []
    with open(CONTENT_FILE, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("text"):
                rows.append(row)

    if not rows:
        return {
            "category": "Insurance",
            "text": "Vehicle Insurance direct company se renew karwayein",
            "cta": "No Agent • No Commission"
        }

    day_number = datetime.now().timetuple().tm_yday
    return rows[day_number % len(rows)]


def create_gradient_bg():
    img = Image.new("RGB", (W, H), "#061326")
    pixels = img.load()

    top = (5, 20, 44)
    bottom = (13, 42, 82)

    for y in range(H):
        ratio = y / H
        r = int(top[0] * (1 - ratio) + bottom[0] * ratio)
        g = int(top[1] * (1 - ratio) + bottom[1] * ratio)
        b = int(top[2] * (1 - ratio) + bottom[2] * ratio)

        for x in range(W):
            pixels[x, y] = (r, g, b)

    return img


def make_poster():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    data = load_content()
    today = datetime.now().strftime("%d %B %Y")

    img = create_gradient_bg()
    draw = ImageDraw.Draw(img)

    gold = "#D6A84F"
    white = "#FFFFFF"
    light = "#DCE7F7"
    cyan = "#6ED6FF"
    dark_card = "#0B2344"

    draw.rounded_rectangle((45, 45, W - 45, H - 45), radius=45, outline=gold, width=5)

    rounded_rectangle(draw, (80, 90, W - 80, 360), 35, fill="#081A33", outline="#254B7D", width=2)

    if os.path.exists(LOGO_PATH):
        try:
            logo = Image.open(LOGO_PATH).convert("RGBA")
            logo.thumbnail((170, 170))
            lx = (W - logo.width) // 2
            img.paste(logo, (lx, 115), logo)
        except Exception:
            pass

    brand_font = font(52, bold=True)
    tagline_font = font(28, bold=False)

    draw_centered(draw, "METASOLW SERVICES", 295, brand_font, gold)
    draw_centered(draw, "EVERYTHING SOLVED", 340, tagline_font, light)

    rounded_rectangle(draw, (285, 405, 795, 475), 32, fill="#102B52", outline=cyan, width=2)
    draw_centered(draw, today, 438, font(32, bold=True), white)

    rounded_rectangle(draw, (160, 545, W - 160, 625), 36, fill=gold)
    draw_centered(draw, data["category"].upper(), 585, font(38, bold=True), "#071529")

    rounded_rectangle(draw, (90, 700, W - 90, 1160), 45, fill=dark_card, outline="#315F98", width=3)
    draw_centered(draw, data["text"], 930, font(62, bold=True), white, max_width=800, line_gap=20)

    rounded_rectangle(draw, (130, 1235, W - 130, 1345), 45, fill="#0F365F", outline=gold, width=3)
    draw_centered(draw, data["cta"], 1290, font(38, bold=True), gold, max_width=780)

    usp_y = 1445
    usps = [
        "Platform by Metasolw Services",
        "Policy issued directly by Insurance Company",
        "No Agent • No Commission • Direct Company Policy"
    ]

    for line in usps:
        draw_centered(draw, line, usp_y, font(30, bold=False), light, max_width=900)
        usp_y += 50

    rounded_rectangle(draw, (80, 1660, W - 80, 1810), 35, fill="#07182E", outline="#254B7D", width=2)
    draw_centered(draw, "WhatsApp: 6390063999", 1708, font(38, bold=True), white)
    draw_centered(draw, "www.metasolwservices.in", 1760, font(32, bold=False), cyan)

    img.save(POSTER_PATH, quality=95)

    caption = f"""MetaSolw Services

{data["category"]}: {data["text"]}

{data["cta"]}

Contact: 6390063999
Website: www.metasolwservices.in

#MetaSolw #EverythingSolved #{data["category"].replace(" ", "")}"""

    with open(CAPTION_PATH, "w", encoding="utf-8") as f:
        f.write(caption)

    print("Poster created successfully:")
    print(POSTER_PATH)
    print("Caption created successfully:")
    print(CAPTION_PATH)


if __name__ == "__main__":
    make_poster()