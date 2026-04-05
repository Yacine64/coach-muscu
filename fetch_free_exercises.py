import requests
import json
import os
import time

REPO_RAW = "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main"
EXERCISES_URL = f"{REPO_RAW}/dist/exercises.json"
GIFS_DIR = "gifs"

os.makedirs(GIFS_DIR, exist_ok=True)

print("Fetching exercises list from free-exercise-db...")
resp = requests.get(EXERCISES_URL, timeout=60)
resp.raise_for_status()
raw_exercises = resp.json()
print(f"Total exercises available: {len(raw_exercises)}")

exercices = []
errors = 0

for i, ex in enumerate(raw_exercises):
    ex_id = ex.get("id", "")
    if not ex_id:
        continue

    nom = ex.get("name", "")
    primary_muscles = ex.get("primaryMuscles", [])
    secondary_muscles = ex.get("secondaryMuscles", [])
    muscle = ", ".join(primary_muscles) if primary_muscles else ""
    instructions = ex.get("instructions", [])
    level = ex.get("level", "")
    equipment = ex.get("equipment", "")
    category = ex.get("category", "")
    force = ex.get("force", "")
    mechanic = ex.get("mechanic", "")

    # Build description from available metadata
    parts = []
    if level:
        parts.append(f"Level: {level}")
    if category:
        parts.append(f"Category: {category}")
    if equipment:
        parts.append(f"Equipment: {equipment}")
    if force:
        parts.append(f"Force: {force}")
    if mechanic:
        parts.append(f"Mechanic: {mechanic}")
    if secondary_muscles:
        parts.append(f"Secondary muscles: {', '.join(secondary_muscles)}")
    description = " | ".join(parts)

    # Download first image
    images = ex.get("images", [])
    gif_path = ""
    if images:
        img_relative = images[0]  # e.g. "3_4_Sit-Up/0.jpg"
        img_url = f"{REPO_RAW}/exercises/{img_relative}"

        # Use the exercise id as filename, keep original extension
        ext = img_relative.split(".")[-1] if "." in img_relative else "jpg"
        local_filename = f"{GIFS_DIR}/{ex_id}.{ext}"

        if not os.path.exists(local_filename):
            try:
                img_resp = requests.get(img_url, timeout=30, stream=True)
                if img_resp.status_code == 200:
                    with open(local_filename, "wb") as f:
                        for chunk in img_resp.iter_content(8192):
                            f.write(chunk)
                    gif_path = local_filename
                    print(f"[{i+1}/{len(raw_exercises)}] Downloaded: {local_filename}")
                else:
                    print(f"[{i+1}/{len(raw_exercises)}] HTTP {img_resp.status_code} for {img_url}")
                    errors += 1
            except Exception as e:
                print(f"[{i+1}/{len(raw_exercises)}] Error: {e}")
                errors += 1
            time.sleep(0.1)
        else:
            gif_path = local_filename
            print(f"[{i+1}/{len(raw_exercises)}] Already exists: {local_filename}")

    exercices.append({
        "id": ex_id,
        "nom": nom,
        "muscle": muscle,
        "muscles_secondaires": secondary_muscles,
        "niveau": level,
        "equipement": equipment,
        "categorie": category,
        "description": description,
        "steps": instructions,
        "gif_path": gif_path
    })

print(f"\nDone. {len(exercices)} exercises processed, {errors} image errors.")

with open("exercices.json", "w", encoding="utf-8") as f:
    json.dump(exercices, f, ensure_ascii=False, indent=2)

print("exercices.json written successfully!")
