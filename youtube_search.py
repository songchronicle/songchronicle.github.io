import json
import time
from yt_dlp import YoutubeDL

INPUT_FILE = "combined_with_youtube_test.json"
SAVE_EVERY = 10


def find_youtube_url(query):
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
        "default_search": "ytsearch1",
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(f"ytsearch1:{query}", download=False)
            entries = result.get("entries", [])

            if not entries:
                return None

            video_id = entries[0].get("id")
            if video_id:
                return f"https://www.youtube.com/watch?v={video_id}"

    except Exception as e:
        print(f"Ошибка поиска {query}: {e}")

    return None


def save_file(data):
    with open(INPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)


processed = 0
updated = 0

for i, item in enumerate(data):

    if item.get("youtube_url"):
        continue

    artist = item.get("artist", "").strip()
    title = item.get("title", "").strip()
    query = f"{artist} {title}"

    print(f"[{i}] Поиск: {query}")

    url = find_youtube_url(query)

    item["youtube_url"] = url
    print(" ->", url)

    processed += 1
    updated += 1

    if updated % SAVE_EVERY == 0:
        print("Сохраняю файл...")
        save_file(data)

    time.sleep(1)


print("Финальное сохранение...")
save_file(data)

print(f"Готово. Обработано {processed} записей.")