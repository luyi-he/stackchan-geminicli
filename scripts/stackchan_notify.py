import sys
import urllib.request
import json

def notify(preset_name):
    url = "http://127.0.0.1:9999/notify"
    data = json.dumps({"preset": preset_name}).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    
    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                print("Notification sent successfully.")
            else:
                print(f"Failed to send notification: {response.status}")
    except Exception as e:
        print(f"Error: Could not reach the background keep-alive service. Is it running? ({e})")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        notify(sys.argv[1])
    else:
        print("Usage: python stackchan_notify.py <approval|done|error>")

