import os
import json
import requests

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TOKEN_INPUT_FILE = os.path.join(BASE_DIR, "token_input.json")
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def get_long_lived_user_token(app_id, app_secret, short_lived_user_token):
    url = "https://graph.facebook.com/v25.0/oauth/access_token"

    params = {
        "grant_type": "fb_exchange_token",
        "client_id": app_id,
        "client_secret": app_secret,
        "fb_exchange_token": short_lived_user_token
    }

    response = requests.get(url, params=params, timeout=60)
    result = response.json()

    if "access_token" not in result:
        raise Exception(f"Long-lived user token failed: {result}")

    return result["access_token"]


def get_page_data(long_lived_user_token):
    url = "https://graph.facebook.com/v25.0/me/accounts"

    params = {
        "fields": "id,name,access_token,instagram_business_account{id,username,name}",
        "access_token": long_lived_user_token
    }

    response = requests.get(url, params=params, timeout=60)
    result = response.json()

    if "data" not in result or not result["data"]:
        raise Exception(f"Page data not found: {result}")

    return result["data"][0]


def main():
    token_input = load_json(TOKEN_INPUT_FILE)
    config = load_json(CONFIG_FILE)

    app_id = token_input["app_id"].strip()
    app_secret = token_input["app_secret"].strip()
    short_token = token_input["short_lived_user_token"].strip()

    print("Creating long-lived user token...")
    long_user_token = get_long_lived_user_token(app_id, app_secret, short_token)

    print("Getting Page access token...")
    page_data = get_page_data(long_user_token)

    page_id = page_data.get("id", "")
    page_token = page_data.get("access_token", "")

    ig_id = ""
    if page_data.get("instagram_business_account"):
        ig_id = page_data["instagram_business_account"].get("id", "")

    if not page_id or not page_token:
        raise Exception(f"Page ID or Page Token missing: {page_data}")

    config["page_id"] = page_id
    config["page_access_token"] = page_token

    if ig_id:
        config["ig_user_id"] = ig_id

    save_json(CONFIG_FILE, config)

    print("DONE: config.json updated with long-lived Page token.")
    print("Page Name:", page_data.get("name"))
    print("Page ID:", page_id)
    print("IG ID:", ig_id if ig_id else "Not found")


if __name__ == "__main__":
    main()