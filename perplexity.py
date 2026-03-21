import json
import os
import time
import re
from pathlib import Path

import requests


# ====== НАСТРОЙКИ ======
INPUT_FILE = "songs.json"
OUTPUT_FILE = "songs.with_perplexity.json"
SAVE_EVERY = 5

# Модель можно поменять при необходимости
PERPLEXITY_MODEL = "sonar"

# Небольшая пауза между запросами, чтобы не долбить API слишком резко
SLEEP_BETWEEN_REQUESTS = 1.0

API_URL = "https://api.perplexity.ai/v1/sonar"


def load_json_array(path: str):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("Входной JSON должен быть массивом объектов.")

    return data


def save_json_array(path: str, data):
    tmp_path = f"{path}.tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, path)

def parse_perplexity_json(text: str):
    # ищем JSON внутри ``` ```
    match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    
    if match:
        json_str = match.group(1)
    else:
        # fallback: берем всё как есть
        json_str = text.strip()

    return json.loads(json_str)

def call_perplexity(api_key: str, artist: str, title: str):
    prompt = f"Мне нужно знать дату выхода и официальное название песни '{artist} - {title}'. Под датой выхода я имею в виду дату, когда песня стала доступна для общественности (первый раз прозвучала в фильме, вышла на пластинке, вышла на альбоме и т.д.). Результат выведи в json формате с полями: \n* perplexity_year - год выхода, который ты обнаружил\n* perplexity_artist - официальное название исполнителя\n* perplexity_title - официальное название композиции\n* perplexity_comment - для комментариев (например если не удалось точно понять год выхода, тогда причину этих непоняток нужно указать в этом поле)"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": PERPLEXITY_MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    response = requests.post(API_URL, headers=headers, json=payload, timeout=120)
    response.raise_for_status()
    data = response.json()

    # По документации текст ответа лежит здесь:
    # choices[0].message.content
    content = None
    choices = data.get("choices", [])
    if choices and isinstance(choices, list):
        message = choices[0].get("message", {})
        content = message.get("content")

    citations = data.get("citations", [])



    return {
        "perplexity_content": parse_perplexity_json(content),
        "perplexity_citations": citations
    }


def main():
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "Не найден PERPLEXITY_API_KEY. "
            "Задай его как переменную окружения, например:\n"
            "Windows PowerShell: $env:PERPLEXITY_API_KEY='your_key'\n"
            "Linux/macOS: export PERPLEXITY_API_KEY='your_key'"
        )

    input_path = Path(INPUT_FILE)
    output_path = Path(OUTPUT_FILE)

    items = load_json_array(str(input_path))
    results = []

    # Если файл уже существует, можно продолжить с того места, где остановились
    if output_path.exists():
        try:
            existing = load_json_array(str(output_path))
            if isinstance(existing, list) and len(existing) <= len(items):
                results = existing
                print(f"Найден существующий выходной файл. Уже обработано: {len(results)}")
        except Exception as e:
            print(f"Не удалось прочитать существующий output-файл, начну заново: {e}")

    start_index = len(results)

    for i in range(start_index, len(items)):
        item = items[i]

        artist = item.get("artist", "")
        title = item.get("title", "")

        print(f"[{i + 1}/{len(items)}] Обрабатываю: {artist} — {title}")

        try:
            perplexity_result = call_perplexity(
                api_key=api_key,
                artist=artist,
                title=title,
            )

            merged = {
                **item,
                **perplexity_result,
            }

        except Exception as e:
            merged = {
                **item,
                "perplexity_content": None,
                "perplexity_citations": [],
                "perplexity_raw_response": None,
                "perplexity_error": str(e),
            }
            print(f"  Ошибка: {e}")

        results.append(merged)

        # Сохраняем каждые SAVE_EVERY записей
        if (i + 1) % SAVE_EVERY == 0:
            save_json_array(str(output_path), results)
            print(f"Промежуточное сохранение после {i + 1} записей -> {output_path}")

        time.sleep(SLEEP_BETWEEN_REQUESTS)

    save_json_array(str(output_path), results)
    print(f"Готово. Итоговый файл сохранён: {output_path}")


if __name__ == "__main__":
    main()