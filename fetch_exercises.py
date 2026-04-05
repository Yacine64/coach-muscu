import requests
import json
import os
import time
from urllib.parse import urljoin

WGER_BASE = "https://wger.de"
API_URL = "https://wger.de/api/v2/exerciseinfo/?format=json&language=2&limit=100&offset=0"

os.makedirs("gifs", exist_ok=True)

exercises_data = []
url = API_URL

print("Fetching exercises from wger.de...")
page = 0
while url and page < 5:  # Limit to 5 pages (500 exercises max)
    print(f"  Page {page+1}: {url}")
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    results = data.get("results", [])
    for ex in results:
        # Only exercises with images
        if not ex.get("images"):
            continue

        # Get English name
        nom = ""
        for trans in ex.get("translations", []):
            if trans.get("language") == 2:  # English
                nom = trans.get("name", "")
                break
        if not nom:
            continue

        # Get description from translations
        description = ""
        steps = []
        for trans in ex.get("translations", []):
            if trans.get("language") == 2:
                description = trans.get("description", "")
                # Try to split description into steps
                if description:
                    import re
                    parts = re.split(r'\n+|\r\n+', description.strip())
                    steps = [p.strip() for p in parts if p.strip()]
                break

        # Get muscle category
        muscle = ""
        if ex.get("category"):
            muscle = ex["category"].get("name", "")

        # Download image
        img_url = ex["images"][0].get("image", "")
        if img_url:
            if img_url.startswith("/"):
                img_url = WGER_BASE + img_url

            # Determine extension
            ext = img_url.split(".")[-1].split("?")[0] if "." in img_url else "jpg"
            gif_path = f"gifs/{ex['id']}.{ext}"

            if not os.path.exists(gif_path):
                try:
                    img_resp = requests.get(img_url, timeout=30, stream=True)
                    if img_resp.status_code == 200:
                        with open(gif_path, "wb") as f:
                            for chunk in img_resp.iter_content(8192):
                                f.write(chunk)
                        print(f"  Downloaded: {gif_path}")
                    else:
                        gif_path = ""
                except Exception as e:
                    print(f"  Failed to download {img_url}: {e}")
                    gif_path = ""
                time.sleep(0.2)

            exercises_data.append({
                "id": ex["id"],
                "nom": nom,
                "muscle": muscle,
                "description": description,
                "steps": steps,
                "gif_path": gif_path
            })

    url = data.get("next")
    page += 1
    time.sleep(0.5)

print(f"\nTotal exercises with images: {len(exercises_data)}")

with open("exercices.json", "w", encoding="utf-8") as f:
    json.dump(exercises_data, f, ensure_ascii=False, indent=2)

print("exercices.json created!")
