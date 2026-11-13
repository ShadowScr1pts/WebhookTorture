import re
from urllib.parse import urlsplit

import requests


def get_discord_webhook_url():
    webhook_url = input("webhook to use: ").strip()
    try:
        parsed = urlsplit(webhook_url)
        port = parsed.port
    except ValueError:
        parsed = None
        port = None

    if (
        parsed is None
        or parsed.scheme != "https"
        or parsed.hostname not in {"discord.com", "discordapp.com"}
        or port not in {None, 443}
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
        or not re.fullmatch(r"/api(?:/v\d+)?/webhooks/\d+/[A-Za-z0-9._-]+", parsed.path)
    ):
        print("Please enter a valid HTTPS Discord webhook URL.")
        return None

    return webhook_url


def main():
    webhook_url = get_discord_webhook_url()
    if webhook_url is None:
        return

    message = input("what to say? ")
    if not message.strip():
        print("Message cannot be empty.")
        return

    session = requests.Session()
    session.trust_env = False

    try:
        response = session.post(
            webhook_url,
            json={"content": message, "allowed_mentions": {"parse": []}},
            timeout=10,
            allow_redirects=False,
        )
    except requests.RequestException as exc:
        print(f"Message send failed: {exc}")
        return

    if not 200 <= response.status_code < 300:
        if response.status_code == 429:
            print("Discord rate limited the request; no retry was attempted.")
        else:
            print(f"Message send failed: HTTP {response.status_code}")
        return

    print("message sent!")

    new_name = input("webhooks new name? ").strip()
    if not new_name or len(new_name) > 80:
        print("Webhook name must be between 1 and 80 characters.")
        return

    try:
        response = session.patch(
            webhook_url,
            json={"name": new_name},
            timeout=10,
            allow_redirects=False,
        )
    except requests.RequestException as exc:
        print(f"Webhook name change failed: {exc}")
        return

    if 200 <= response.status_code < 300:
        print("name changed!")
    else:
        print(f"Webhook name change failed: HTTP {response.status_code}")


if __name__ == "__main__":
    main()
