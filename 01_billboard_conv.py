import json
from collections import defaultdict

input_file = "billboard_all.json"
output_file = "output_top50_by_year.json"

songs_by_year = defaultdict(dict)

with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

for entry in data:
    year = int(entry["date"][:4])

    for item in entry.get("data", []):
        artist = item.get("artist")
        title = item.get("song")

        if not artist or not title:
            continue

        peak_position = item.get("peak_position")
        weeks_on_chart = item.get("weeks_on_chart") or 0

        key = (artist.strip().lower(), title.strip().lower())

        existing = songs_by_year[year].get(key)

        if existing is None:
            songs_by_year[year][key] = {
                "artist": artist.strip(),
                "title": title.strip(),
                "year": year,
                "peak_position": peak_position,
                "weeks_on_chart": weeks_on_chart
            }
        else:
            # берём лучший peak_position и максимальное количество недель
            if peak_position is not None:
                if existing["peak_position"] is None:
                    existing["peak_position"] = peak_position
                else:
                    existing["peak_position"] = min(existing["peak_position"], peak_position)

            existing["weeks_on_chart"] = max(
                existing["weeks_on_chart"],
                weeks_on_chart
            )

result = []

for year, songs_dict in songs_by_year.items():
    songs = list(songs_dict.values())

    top_50 = sorted(
        songs,
        key=lambda x: (
            x["peak_position"] if x["peak_position"] is not None else 999,
            -x["weeks_on_chart"]
        )
    )[:30]

    for song in top_50:
        result.append({
            "artist": song["artist"],
            "title": song["title"],
            "year": song["year"]
        })

result.sort(key=lambda x: (x["year"], x["artist"], x["title"]))

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"Готово! Сохранено {len(result)} песен в {output_file}")