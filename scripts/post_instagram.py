import os
import json
import time
import requests
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

CAPTION_PATH = os.path.join(OUTPUT_DIR, "caption_today.txt")
FB_IMAGE_URL_FILE = os.path.join(OUTPUT_DIR, "facebook_image_url.txt")
LOG_FILE = os.path.join(LOGS_DIR, "instagram_post_log.txt")


def log(message):
    os.makedirs(LOGS_DIR, exist_ok=True)
    line = f"[{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}] {message}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def load_config():
    if not os.path.exists(CONFIG_FILE):
        raise FileNotFoundError("config.json file nahi mili.")

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = json.load(f)

    ig_user_id = config.get("ig_user_id", "").strip()
    token = config.get("page_access_token", "").strip()

    if not ig_user_id:
        raise ValueError("config.json me ig_user_id blank hai.")

    if not token:
        raise ValueError("config.json me page_access_token blank hai.")

    return ig_user_id, token


def load_caption():
    if os.path.exists(CAPTION_PATH):
        with open(CAPTION_PATH, "r", encoding="utf-8") as f:
            return f.read().strip()

    return "MetaSolw Services\nEverything Solved\nContact: 6390063999"


def load_image_url():
    if not os.path.exists(FB_IMAGE_URL_FILE):
        raise FileNotFoundError("facebook_image_url.txt nahi mili. Pehle Facebook script chalao.")

    with open(FB_IMAGE_URL_FILE, "r", encoding="utf-8") as f:
        image_url = f.read().strip()

    if not image_url:
        raise ValueError("facebook_image_url.txt blank hai.")

    return image_url


def create_media_container(ig_user_id, token, image_url, caption):
    url = f"https://graph.facebook.com/v25.0/{ig_user_id}/media"

    data = {
        "image_url": image_url,
        "caption": caption,
        "access_token": token
    }

    response = requests.post(url, data=data, timeout=60)

    try:
        result = response.json()
    except Exception:
        result = {"raw_response": response.text}

    if response.status_code == 200 and "id" in result:
        creation_id = result["id"]
        log(f"Instagram media container created. Creation ID: {creation_id}")
        return creation_id

    log("Instagram media container create failed.")
    log(str(result))
    raise Exception(str(result))


def publish_media(ig_user_id, token, creation_id):
    url = f"https://graph.facebook.com/v25.0/{ig_user_id}/media_publish"

    data = {
        "creation_id": creation_id,
        "access_token": token
    }

    response = requests.post(url, data=data, timeout=60)

    try:
        result = response.json()
    except Exception:
        result = {"raw_response": response.text}

    if response.status_code == 200 and "id" in result:
        log(f"Instagram post successful. Post ID: {result['id']}")
        return True

    log("Instagram publish failed.")
    log(str(result))
    raise Exception(str(result))


def post_to_instagram():
    ig_user_id, token = load_config()
    caption = load_caption()
    image_url = load_image_url()

    log("Instagram posting started.")

    creation_id = create_media_container(
        ig_user_id=ig_user_id,
        token=token,
        image_url=image_url,
        caption=caption
    )

    time.sleep(10)

    publish_media(
        ig_user_id=ig_user_id,
        token=token,
        creation_id=creation_id
    )

    return True


if __name__ == "__main__":
    try:
        success = post_to_instagram()
        if success:
            print("\nDONE: Instagram par post ho gaya.")
        else:
            print("\nFAILED: Instagram post nahi hua.")
    except Exception as e:
        log(f"Exception: {e}")
        print("\nERROR:", e)