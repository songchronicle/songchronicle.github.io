import json
import time
from yt_dlp import YoutubeDL

input_file = "output_top50_billboard.json"
output_file = "output_with_youtube.json"

SEARCH_DELAY_SECONDS = 3

ydl_opts = {
    "quiet": False,
    "skip_download": True,
    "extract_flat": "in_playlist",
    "noplaylist": True,
}

def find_youtube_url(artist, title):
    query = f"ytsearch1:{artist} - {title}"

    try:
        with YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(query, download=False)

        entries = result.get("entries") or []

        if not entries:
            return None

        video = entries[0]

        video_id = video.get("id")
        webpage_url = video.get("webpage_url")
        url = video.get("url")

        if webpage_url:
            return webpage_url

        if video_id:
            return f"https://www.youtube.com/watch?v={video_id}"

        if url and url.startswith("http"):
            return url

        return None

    except Exception as e:
        print(f"Ошибка поиска для {artist} - {title}: {e}")
        return None


with open(input_file, "r", encoding="utf-8") as f:
    songs = json.load(f)

for i, song in enumerate(songs, start=1):
    artist = song.get("artist")
    title = song.get("title")

    if not artist or not title:
        song["youtube_url"] = None
        continue

    if song.get("youtube_url"):
        continue

    print(f"[{i}/{len(songs)}] Ищу: {artist} - {title}")

    song["youtube_url"] = find_youtube_url(artist, title)

    print(" ->", song["youtube_url"])

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(songs, f, ensure_ascii=False, indent=2)

    time.sleep(SEARCH_DELAY_SECONDS)

print(f"Готово! Файл сохранён: {output_file}")