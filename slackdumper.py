import argparse
import requests
import json

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

def get_channel_history(api_key, channel_id, channel_name):
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
    with open(f"{channel_name}.json", "w") as file:
        file.write(response.text)

def main():
    parser = argparse.ArgumentParser(description="Dump Slack channel history")
    parser.add_argument("-api", required=True, help="Slack API key (e.g., xoxb-123456)")
    args = parser.parse_args()

    api_key = args.api
    channel_list = get_channel_list(api_key)

    for channel in channel_list["channels"]:
        channel_id = channel["id"]
        channel_name = channel["name"]
        get_channel_history(api_key, channel_id, channel_name)
        print(f"Dumped history for channel: {channel_name}")

if __name__ == "__main__":
    main()
