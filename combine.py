import json

files = [f"{i}.json" for i in range(1, 8)]
all_items = []

# загрузка всех файлов
for file in files:
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)
        all_items.extend(data)

# сортировка по year, затем по title
all_items.sort(key=lambda x: (x["year"], x["title"]))

# сохранение результата
with open("combined_sorted.json", "w", encoding="utf-8") as f:
    json.dump(all_items, f, ensure_ascii=False, indent=2)

print(f"Готово! Объединено {len(all_items)} записей.")