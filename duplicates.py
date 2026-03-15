import json

INPUT_FILE = "songs.checked.strict.json"
OUTPUT_FILE = "songs.deduplicated.json"

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    songs = json.load(f)

# группируем по youtube_url
groups = {}
for song in songs:
    url = song.get("youtube_url")
    if not url:
        continue
    groups.setdefault(url, []).append(song)

# список песен, которые останутся
result = []
processed_urls = set()

for song in songs:
    url = song.get("youtube_url")

    if not url:
        result.append(song)
        continue

    if url in processed_urls:
        continue

    duplicates = groups.get(url, [])

    if len(duplicates) == 1:
        result.append(duplicates[0])
    else:
        print("\nНайден дубликат youtube_url:")
        print(url)
        print()

        for i, d in enumerate(duplicates):
            print(f"[{i}] {d.get('artist')} - {d.get('title')} ({d.get('year')}) | genre={d.get('genre')}")

        while True:
            choice = input("Какой вариант оставить? Введите номер: ")
            try:
                choice = int(choice)
                if 0 <= choice < len(duplicates):
                    break
            except:
                pass
            print("Неверный ввод, попробуйте снова.")

        result.append(duplicates[choice])

    processed_urls.add(url)

# сохраняем
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"\nГотово. Сохранено {len(result)} записей в {OUTPUT_FILE}")