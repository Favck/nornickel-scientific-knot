
MODEL = {
    "en":"en_core_web_md",
    "ru":"ru_core_news_md"
}
#/л|мг/дм³|г/л|г/дм³|мг/куб\.м


# Шаг 1: Оставляем регулярки чистыми базами (добавили "л", "дм³", "м³", "м3" в основной список)
UNITS_REGEX_RU = r"(?:мг|МПа|мВ|В|[°][СС]|мм|мкм|м|м3|м2|%|ч|сут|т/сут|л|дм³|м³|м3)"
UNITS_REGEX_EN = r"(?:mg|g|MPa|mV|V|°C|mm|µm|um|m|%|h|hrs|days|t|L|dm3|m3)"

patterns = {
    "ru": [
        # === VALUE_RANGE ===
        # Слитный (например, "200-300мг/л")
        {
            "label": "VALUE_RANGE",
            "pattern": [{"TEXT": {"REGEX": r"^\d+[-–]\d+" + UNITS_REGEX_RU + r"(?:\s*/\s*" + UNITS_REGEX_RU + r")?$"}}]
        },
        # Раздельный БЕЗ дроби (например, "200–300 мг")
        {
            "label": "VALUE_RANGE",
            "pattern": [
                {"TEXT": {"REGEX": r"^\d+[-–]\d+$"}}, 
                {"TEXT": {"REGEX": r"^" + UNITS_REGEX_RU + r"$"}}
            ]
        },
        # Раздельный С ДРОБЬЮ (например, "200–300 мг/л" — все токены обязательны!)
        {
            "label": "VALUE_RANGE",
            "pattern": [
                {"TEXT": {"REGEX": r"^\d+[-–]\d+$"}}, 
                {"TEXT": {"REGEX": r"^" + UNITS_REGEX_RU + r"$"}},
                {"TEXT": {"REGEX": r"^/$"}},
                {"TEXT": {"REGEX": r"^" + UNITS_REGEX_RU + r"$"}}
            ]
        },

        # === VALUE_LIMIT ===
        # Слитный (например, "≤1000мг/дм³")
        {
            "label": "VALUE_LIMIT",
            "pattern": [{"TEXT": {"REGEX": r"^[≤≥<>=]+\d+" + UNITS_REGEX_RU + r"(?:\s*/\s*" + UNITS_REGEX_RU + r")?$"}}]
        },
        # Раздельный тип 1 БЕЗ дроби (например, "≤1000 мг")
        {
            "label": "VALUE_LIMIT",
            "pattern": [
                {"TEXT": {"REGEX": r"^[≤≥<>=]+\d+$"}}, 
                {"TEXT": {"REGEX": r"^" + UNITS_REGEX_RU + r"$"}}
            ]
        },
        # Раздельный тип 1 С ДРОБЬЮ (например, "≤1000 мг/дм³")
        {
            "label": "VALUE_LIMIT",
            "pattern": [
                {"TEXT": {"REGEX": r"^[≤≥<>=]+\d+$"}}, 
                {"TEXT": {"REGEX": r"^" + UNITS_REGEX_RU + r"$"}},
                {"TEXT": {"REGEX": r"^/$"}},
                {"TEXT": {"REGEX": r"^" + UNITS_REGEX_RU + r"$"}}
            ]
        },
        # Раздельный тип 2 БЕЗ дроби (например, "≤ 1000 мг")
        {
            "label": "VALUE_LIMIT",
            "pattern": [
                {"TEXT": {"REGEX": r"^[≤≥<>=]+$"}}, 
                {"TEXT": {"REGEX": r"^\d+$"}}, 
                {"TEXT": {"REGEX": r"^" + UNITS_REGEX_RU + r"$"}}
            ]
        },
        # Раздельный тип 2 С ДРОБЬЮ (например, "≤ 1000 мг/дм³")
        {
            "label": "VALUE_LIMIT",
            "pattern": [
                {"TEXT": {"REGEX": r"^[≤≥<>=]+$"}}, 
                {"TEXT": {"REGEX": r"^\d+$"}}, 
                {"TEXT": {"REGEX": r"^" + UNITS_REGEX_RU + r"$"}},
                {"TEXT": {"REGEX": r"^/$"}},
                {"TEXT": {"REGEX": r"^" + UNITS_REGEX_RU + r"$"}}
            ]
        },

        # === VALUE_EXACT ===
        # Раздельный БЕЗ дроби (Пример: "1500 °C", "15 мг")
        {
            "label": "VALUE_EXACT",
            "pattern": [
                {"TEXT": {"REGEX": r"^\d+$"}}, 
                {"TEXT": {"REGEX": r"^" + UNITS_REGEX_RU + r"$"}}
            ]
        },
        # Раздельный С ДРОБЬЮ (Пример: "15 мг/л")
        {
            "label": "VALUE_EXACT",
            "pattern": [
                {"TEXT": {"REGEX": r"^\d+$"}}, 
                {"TEXT": {"REGEX": r"^" + UNITS_REGEX_RU + r"$"}},
                {"TEXT": {"REGEX": r"^/$"}},
                {"TEXT": {"REGEX": r"^" + UNITS_REGEX_RU + r"$"}}
            ]
        },
        # Слитный (например, "1500°C", "20%")
        {
            "label": "VALUE_EXACT",
            "pattern": [{"TEXT": {"REGEX": r"^\d+" + UNITS_REGEX_RU + r"(?:\s*/\s*" + UNITS_REGEX_RU + r")?$"}}]
        }
    ],
    
    "en": [
        # === VALUE_RANGE ===
        {
            "label": "VALUE_RANGE",
            "pattern": [{"TEXT": {"REGEX": r"^\d+[-–]\d+" + UNITS_REGEX_EN + r"(?:\s*/\s*" + UNITS_REGEX_EN + r")?$"}}]
        },
        {
            "label": "VALUE_RANGE",
            "pattern": [
                {"TEXT": {"REGEX": r"^\d+[-–]\d+$"}}, 
                {"TEXT": {"REGEX": r"^" + UNITS_REGEX_EN + r"$"}}
            ]
        },
        {
            "label": "VALUE_RANGE",
            "pattern": [
                {"TEXT": {"REGEX": r"^\d+[-–]\d+$"}}, 
                {"TEXT": {"REGEX": r"^" + UNITS_REGEX_EN + r"$"}},
                {"TEXT": {"REGEX": r"^/$"}},
                {"TEXT": {"REGEX": r"^" + UNITS_REGEX_EN + r"$"}}
            ]
        },
        # === VALUE_LIMIT ===
        {
            "label": "VALUE_LIMIT",
            "pattern": [{"TEXT": {"REGEX": r"^[≤≥<>=]+\d+" + UNITS_REGEX_EN + r"(?:\s*/\s*" + UNITS_REGEX_EN + r")?$"}}]
        },
        {
            "label": "VALUE_LIMIT",
            "pattern": [
                {"TEXT": {"REGEX": r"^[≤≥<>=]+\d+$"}}, 
                {"TEXT": {"REGEX": r"^" + UNITS_REGEX_EN + r"$"}}
            ]
        },
        {
            "label": "VALUE_LIMIT",
            "pattern": [
                {"TEXT": {"REGEX": r"^[≤≥<>=]+\d+$"}}, 
                {"TEXT": {"REGEX": r"^" + UNITS_REGEX_EN + r"$"}},
                {"TEXT": {"REGEX": r"^/$"}},
                {"TEXT": {"REGEX": r"^" + UNITS_REGEX_EN + r"$"}}
            ]
        },
        {
            "label": "VALUE_LIMIT",
            "pattern": [
                {"TEXT": {"REGEX": r"^[≤≥<>=]+$"}}, 
                {"TEXT": {"REGEX": r"^\d+$"}}, 
                {"TEXT": {"REGEX": r"^" + UNITS_REGEX_EN + r"$"}}
            ]
        },
        {
            "label": "VALUE_LIMIT",
            "pattern": [
                {"TEXT": {"REGEX": r"^[≤≥<>=]+$"}}, 
                {"TEXT": {"REGEX": r"^\d+$"}}, 
                {"TEXT": {"REGEX": r"^" + UNITS_REGEX_EN + r"$"}},
                {"TEXT": {"REGEX": r"^/$"}},
                {"TEXT": {"REGEX": r"^" + UNITS_REGEX_EN + r"$"}}
            ]
        },
        # === VALUE_EXACT ===
        {
            "label": "VALUE_EXACT",
            "pattern": [
                {"TEXT": {"REGEX": r"^\d+$"}}, 
                {"TEXT": {"REGEX": r"^" + UNITS_REGEX_EN + r"$"}}
            ]
        },
        {
            "label": "VALUE_EXACT",
            "pattern": [
                {"TEXT": {"REGEX": r"^\d+$"}}, 
                {"TEXT": {"REGEX": r"^" + UNITS_REGEX_EN + r"$"}},
                {"TEXT": {"REGEX": r"^/$"}},
                {"TEXT": {"REGEX": r"^" + UNITS_REGEX_EN + r"$"}}
            ]
        },
        {
            "label": "VALUE_EXACT",
            "pattern": [{"TEXT": {"REGEX": r"^\d+" + UNITS_REGEX_EN + r"(?:\s*/\s*" + UNITS_REGEX_EN + r")?$"}}]
        }
    ]
}




dictionary = {
    "ru":{"металл":{
        "synonyms":["металлы"]
    }},
    "en":["Metal"]
}