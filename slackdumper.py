import argparse
import requests
import json
import os
import re

def get_channel_list(api_key):
    url = "https://slack.com/api/conversations.list"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "types": "public_channel,private_channel"
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    response.raise_for_status()
    return response.json()

def extract_urls_from_text(text):
    url_pattern = r"https?://[^\s]+"
    urls = re.findall(url_pattern, text)
    return urls

def get_channel_history(api_key, channel_id):
    url = "https://slack.com/api/conversations.history"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "channel": channel_id
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    response.raise_for_status()
    return response.json()

def download_attachment(attachment_url, download_path):
    try:
        response = requests.get(attachment_url)
        response.raise_for_status()

        if response.status_code == 200:
            with open(download_path, "wb") as file:
                file.write(response.content)
                print(f"Downloaded attachment: {os.path.basename(download_path)}")
        else:
            print(f"Failed to download attachment: {os.path.basename(download_path)}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading attachment: {e}")

def main():
    parser = argparse.ArgumentParser(description="Dump Slack channel history, extract URLs, and download attachments")
    parser.add_argument("-api", required=True, help="Slack API key (e.g., xoxb-123456)")
    args = parser.parse_args()

    api_key = args.api
    channel_list = get_channel_list(api_key)

    with open("urls.txt", "w") as urls_file:
        for channel in channel_list["channels"]:
            channel_id = channel["id"]
            channel_name = channel["name"]
            channel_history = get_channel_history(api_key, channel_id)

            with open(f"{channel_name}.json", "w") as file:
                json.dump(channel_history, file, indent=4)

            print(f"Dumped history for channel: {channel_name}")

            if "messages" in channel_history:
                for message in channel_history["messages"]:
                    if "files" in message:
                        for attachment in message["files"]:
                            attachment_url = attachment.get("url_private_download")
                            if attachment_url:
                                file_name = attachment.get("name")
                                download_dir = os.path.join("attachments", channel_name)
                                os.makedirs(download_dir, exist_ok=True)
                                download_path = os.path.join(download_dir, file_name)
                                download_attachment(attachment_url, download_path)

                    if "text" in message:
                        message_text = message["text"]
                        message_urls = extract_urls_from_text(message_text)
                        for url in message_urls:
                            urls_file.write(f"{channel_name}: {url}\n")

if __name__ == "__main__":
    main()
