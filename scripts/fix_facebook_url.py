import os
import re
import json
import requests

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
FB_LOG_FILE = os.path.join(BASE_DIR, "logs", "facebook_post_log.txt")
OUTPUT_FILE = os.path.join(BASE_DIR, "output", "facebook_image_url.txt")


def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def get_last_photo_id():
    if not os.path.exists(FB_LOG_FILE):
        raise FileNotFoundError("facebook_post_log.txt nahi mili.")

    with open(FB_LOG_FILE, "r", encoding="utf-8") as f:
        text = f.read()

    ids = re.findall(r"Photo/Post ID:\s*(\d+)", text)

    if not ids:
        raise ValueError("Facebook Photo/Post ID log me nahi mila.")

    return ids[-1]


def save_image_url():
    config = load_config()
    token = config["page_access_token"]
    photo_id = get_last_photo_id()

    url = f"https://graph.facebook.com/v25.0/{photo_id}"
    params = {
        "fields": "images,source",
        "access_token": token
    }

    response = requests.get(url, params=params, timeout=60)
    result = response.json()

    image_url = ""

    if result.get("source"):
        image_url = result["source"]
    elif result.get("images"):
        image_url = result["images"][0].get("source", "")

    if not image_url:
        print(result)
        raise ValueError("Facebook image URL nahi mila.")

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(image_url)

    print("DONE: facebook_image_url.txt ban gayi")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    save_image_url()