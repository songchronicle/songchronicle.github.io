import json
import os
from copy import deepcopy

INPUT_FILE = "songs.json"
OUTPUT_FILE = "songs.resolved.json"


def load_json_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json_file(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def ask_choice(field_name, original_value, perplexity_value):
    while True:
        print(f"\nПоле '{field_name}' отличается:")
        print(f"1. Оставить исходное значение: {original_value}")
        print(f"2. Взять значение из Perplexity: {perplexity_value}")
        print("3. Ввести своё значение")

        choice = input("Ваш выбор (1/2/3): ").strip()

        if choice == "1":
            return original_value
        elif choice == "2":
            return perplexity_value
        elif choice == "3":
            custom = input(f"Введите новое значение для '{field_name}': ")
            if field_name == "year":
                custom = custom.strip()
                try:
                    return int(custom)
                except ValueError:
                    print("Год должен быть числом.")
            else:
                return custom
        else:
            print("Некорректный ввод. Введите 1, 2 или 3.")


def normalize_record(record):
    record = deepcopy(record)

    perplexity_content = record.get("perplexity_content") or {}
    perplexity_citations = record.get("perplexity_citations")

    # Переносим citations внутрь perplexity_content
    if perplexity_citations is not None:
        perplexity_content["perplexity_citations"] = perplexity_citations

    # Удаляем служебные поля из perplexity_content
    perplexity_content.pop("perplexity_year", None)
    perplexity_content.pop("perplexity_artist", None)
    perplexity_content.pop("perplexity_title", None)

    record["perplexity_content"] = perplexity_content

    # Удаляем верхнеуровневое поле
    record.pop("perplexity_citations", None)

    return record


def process_record(record):
    artist = record.get("artist")
    title = record.get("title")
    year = record.get("year")

    perplexity_content = record.get("perplexity_content") or {}

    p_artist = perplexity_content.get("perplexity_artist")
    p_title = perplexity_content.get("perplexity_title")
    p_year = perplexity_content.get("perplexity_year")
    p_comment = perplexity_content.get("perplexity_comment")

    print("\n" + "=" * 80)
    print(f"Обрабатывается {artist} - {title}")
    print("-" * 80)
    print("Комментарий Perplexity:")
    print(p_comment if p_comment is not None else "(нет комментария)")
    print("-" * 80)

    if p_artist is not None and artist != p_artist:
        record["artist"] = ask_choice("artist", artist, p_artist)

    if p_title is not None and title != p_title:
        record["title"] = ask_choice("title", title, p_title)

    if p_year is not None and year != p_year:
        record["year"] = ask_choice("year", year, p_year)

    record = normalize_record(record)
    return record


def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Исходный файл не найден: {INPUT_FILE}")
        return

    source_data = load_json_file(INPUT_FILE)

    if not isinstance(source_data, list):
        print("Ошибка: исходный JSON должен содержать массив записей.")
        return

    # Если выходной файл уже есть — продолжаем с места остановки
    if os.path.exists(OUTPUT_FILE):
        output_data = load_json_file(OUTPUT_FILE)
        if not isinstance(output_data, list):
            print("Ошибка: выходной JSON должен содержать массив записей.")
            return
        start_index = len(output_data)
        print(f"Найден существующий файл {OUTPUT_FILE}.")
        print(f"Уже обработано записей: {start_index}")
    else:
        output_data = []
        start_index = 0
        print(f"Выходной файл {OUTPUT_FILE} будет создан заново.")

    if start_index > len(source_data):
        print("Ошибка: в выходном файле записей больше, чем в исходном.")
        return

    for i in range(start_index, len(source_data)):
        record = source_data[i]
        processed = process_record(record)
        output_data.append(processed)

        save_json_file(OUTPUT_FILE, output_data)
        print(f"Сохранено: {i + 1} из {len(source_data)}")

    print("\nГотово.")


if __name__ == "__main__":
    main()