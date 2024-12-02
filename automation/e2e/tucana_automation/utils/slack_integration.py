import json
import sys

import requests


def send_slack_notification(slack_webhook, slack_data):
    byte_length = str(sys.getsizeof(slack_data))
    headers = {"Content-Type": "application/json", "Content-Length": byte_length}
    response = requests.post(
        slack_webhook, data=json.dumps(slack_data), headers=headers
    )
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
