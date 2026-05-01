import json

input_file = "output_with_youtube.json"
output_file = "songs_foreign.json"

with open(input_file, "r", encoding="utf-8") as f:
    songs = json.load(f)

result = []

for song in songs:
    youtube_url = song.get("youtube_url")

    # обрабатываем только строки, где youtube_url не пустой
    if not youtube_url:
        continue

    year = song.get("year")

    song["genre"] = ""

    song["perplexity_content"] = {
        "perplexity_comment": f"Песня из топа Billboard {year}[1]",
        "perplexity_citations": [
            f"https://en.wikipedia.org/wiki/Billboard_Year-End_Hot_100_singles_of_{year}"
        ]
    }

    result.append(song)

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"Готово! Сохранено {len(result)} строк в {output_file}")