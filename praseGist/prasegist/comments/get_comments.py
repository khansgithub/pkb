import time
import requests
import json
from pathlib import Path

GIST_ID = "c7a6bfca57631a4c45e2c75b7b5f881e"
URL = f"https://api.github.com/gists/{GIST_ID}/comments"
FILENAME = "comments.json"
FILEPATH = Path(__file__).parent / FILENAME
headers = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}

def get_comments():
    all_comments = []
    max_pages = 100  # Failsafe to avoid infinite loop

    for page in range(1, max_pages + 1):
        paged_url = f"{URL}?page={page}"
        try:
            resp = requests.get(paged_url, headers=headers, timeout=10)
            resp.raise_for_status()
            comments = resp.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching page {page}: {e}")
            break

        if not comments:
            break
        all_comments.extend(comments)
        time.sleep(1)  # Add timeout between requests


    try:
        with open(FILEPATH, "w") as f:
            json.dump(all_comments, f, indent=4)
    except (OSError, IOError) as file_err:
        print(f"Error writing to {FILENAME}: {file_err}")
        # You might want to handle or propagate the error depending on your needs

    return all_comments

if __name__ == "__main__":
    comments = get_comments()  
    # print(comments)