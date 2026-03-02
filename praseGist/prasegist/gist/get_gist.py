import requests
from pathlib import Path

GIST_ID = "c7a6bfca57631a4c45e2c75b7b5f881e"
URL = f"https://gist.githubusercontent.com/khansgithub/{GIST_ID}/raw"
FILENAME = "gist.md"
FILEPATH = Path(__file__).parent / FILENAME
headers = {}

def get_gist():
    gist_text = ""
    
    try:
        resp = requests.get(URL, headers=headers, timeout=10)
        resp.raise_for_status()
        gist_text = resp.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching gist: {e}")
        return ""


    try:
        with open(FILEPATH, "w", encoding="utf-8") as f:
            f.write(gist_text)
    except (OSError, IOError) as file_err:
        print(f"Error writing to {FILENAME}: {file_err}")
        return ""

    return gist_text

if __name__ == "__main__":
    gist_text = get_gist()  
    # print(comments)