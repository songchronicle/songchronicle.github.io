import json

INPUT_FILE = "songs.json"

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    songs = json.load(f)

# оставляем только записи где есть youtube_url
songs_with_url = [s for s in songs if s.get("youtube_url")]

# сортируем по youtube_url
songs_with_url.sort(key=lambda x: x["youtube_url"])

duplicates_found = 0

for i in range(1, len(songs_with_url)):
    prev = songs_with_url[i - 1]
    curr = songs_with_url[i]

    if prev["youtube_url"] == curr["youtube_url"]:
        print("\nДУБЛИКАТ YOUTUBE URL:")
        print(json.dumps(prev, ensure_ascii=False, indent=2))
        print(json.dumps(curr, ensure_ascii=False, indent=2))
        duplicates_found += 1

print(f"\nВсего найдено дубликатов: {duplicates_found}")