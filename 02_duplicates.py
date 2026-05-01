import json

input_file = "output_top50_by_year.json"
output_file = "output_top50_billboard.json"

with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

unique = {}

for item in data:
    artist = item["artist"].strip()
    title = item["title"].strip()
    year = item["year"]

    key = (artist.lower(), title.lower())

    if key not in unique:
        unique[key] = {
            "artist": artist,
            "title": title,
            "year": year
        }
    else:
        # оставляем более ранний год
        if year < unique[key]["year"]:
            unique[key]["year"] = year

# преобразуем обратно в список
result = list(unique.values())

# (опционально) сортируем для читаемости
result.sort(key=lambda x: (x["year"], x["artist"], x["title"]))

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"Готово! Осталось {len(result)} уникальных песен")