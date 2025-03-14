import random
import logging
from deep_translator import GoogleTranslator

# Получаем список доступных языков
languages = list(GoogleTranslator().get_supported_languages())

def wrong_translator(text, iterations):
    """Функция случайных переводов"""
    translated_text = text
    used_languages = []  # Список использованных языков
    logging.info(f"Исходный текст: {text}")

    for i in range(iterations):
        lang = random.choice(languages)
        used_languages.append(lang)
        translated_text = GoogleTranslator(source="auto", target=lang).translate(translated_text)
        logging.info(f"[{i+1}] Переведено на {lang}: {translated_text}")

    final_text = GoogleTranslator(source="auto", target="ru").translate(translated_text)
    logging.info(f"Финальный перевод: {final_text}")

    return final_text, used_languages