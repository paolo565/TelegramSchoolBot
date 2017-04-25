import subprocess
import sys
import os
import json

here = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(here, "./vendored"))


def handler(event, context):
    subprocess.call(["telegramschoolbot", "process", json.dumps(event['body'])])

    return {
        "statusCode": 200,
        "body": "{}",
    }
