import os
import json
import requests
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

POSTER_PATH = os.path.join(OUTPUT_DIR, "status_today.png")
CAPTION_PATH = os.path.join(OUTPUT_DIR, "caption_today.txt")
LOG_FILE = os.path.join(LOGS_DIR, "facebook_post_log.txt")


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

    page_id = config.get("page_id", "").strip()
    token = config.get("page_access_token", "").strip()

    if not page_id:
        raise ValueError("config.json me page_id blank hai.")

    if not token:
        raise ValueError("config.json me page_access_token blank hai.")

    return page_id, token


def load_caption():
    if os.path.exists(CAPTION_PATH):
        with open(CAPTION_PATH, "r", encoding="utf-8") as f:
            return f.read().strip()

    return "MetaSolw Services\nEverything Solved\nContact: 6390063999"


def post_photo_to_facebook():
    page_id, page_token = load_config()

    if not os.path.exists(POSTER_PATH):
        raise FileNotFoundError("output/status_today.png file nahi mili. Pehle poster generate karo.")

    caption = load_caption()

    url = f"https://graph.facebook.com/v25.0/{page_id}/photos"

    data = {
        "access_token": page_token,
        "message": caption,
        "published": "true"
    }

    log("Facebook photo posting started.")

    with open(POSTER_PATH, "rb") as image_file:
        files = {
            "source": image_file
        }

        response = requests.post(url, data=data, files=files, timeout=60)

    try:
        result = response.json()
    except Exception:
        result = {"raw_response": response.text}

    if response.status_code == 200 and "id" in result:
        log(f"Facebook post successful. Photo/Post ID: {result.get('id')}")
        return True

    log("Facebook post failed.")
    log(str(result))

    if "error" in result:
        error = result["error"]
        log(f"Error Message: {error.get('message')}")
        log(f"Error Code: {error.get('code')}")

    return False


if __name__ == "__main__":
    try:
        success = post_photo_to_facebook()
        if success:
            print("\nDONE: Facebook Page par post ho gaya.")
        else:
            print("\nFAILED: Facebook post nahi hua. Log check karo.")
    except Exception as e:
        log(f"Exception: {e}")
        print("\nERROR:", e)