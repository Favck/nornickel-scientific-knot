
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
        # например, "200-300мг/л"
        {
            "label": "VALUE_RANGE",
            # Для слитного токена добавляем хвост прямо в регулярку: (?:\s*/\s*UNITS_REGEX_RU)?
            "pattern": [{"TEXT": {"REGEX": r"^\d+[-–]\d+" + UNITS_REGEX_RU + r"(?:\s*/\s*" + UNITS_REGEX_RU + r")?$"}}]
        },
        # (например, "200–300 мг/л", "200-300 мг")
        {
            "label": "VALUE_RANGE",
            # Добавили два опциональных ("OP": "?") токена для косой черты и правой единицы
            "pattern": [
                {"TEXT": {"REGEX": r"^\d+[-–]\d+$"}}, 
                {"TEXT": {"REGEX": r"^" + UNITS_REGEX_RU + r"$"}},
                {"TEXT": {"REGEX": r"^/$"}, "OP": "?"},
                {"TEXT": {"REGEX": r"^" + UNITS_REGEX_RU + r"$"}, "OP": "?"}
            ]
        },
        # (например, "≤1000мг/дм³")
        {
            "label": "VALUE_LIMIT",
            "pattern": [{"TEXT": {"REGEX": r"^[≤≥<>=]+\d+" + UNITS_REGEX_RU + r"(?:\s*/\s*" + UNITS_REGEX_RU + r")?$"}}]
        },
        # (например, "≤1000 мг/дм³")
        {
            "label": "VALUE_LIMIT",
            "pattern": [
                {"TEXT": {"REGEX": r"^[≤≥<>=]+\d+$"}}, 
                {"TEXT": {"REGEX": r"^" + UNITS_REGEX_RU + r"$"}},
                {"TEXT": {"REGEX": r"^/$"}, "OP": "?"},
                {"TEXT": {"REGEX": r"^" + UNITS_REGEX_RU + r"$"}, "OP": "?"}
            ]
        },
        # (например, "≤ 1000 мг/дм³")
        {
            "label": "VALUE_LIMIT",
            "pattern": [
                {"TEXT": {"REGEX": r"^[≤≥<>=]+$"}}, 
                {"TEXT": {"REGEX": r"^\d+$"}}, 
                {"TEXT": {"REGEX": r"^" + UNITS_REGEX_RU + r"$"}},
                {"TEXT": {"REGEX": r"^/$"}, "OP": "?"},
                {"TEXT": {"REGEX": r"^" + UNITS_REGEX_RU + r"$"}, "OP": "?"}
            ]
        },
        # (Пример: "1500 °C", "20 %", "15 мг/л")
        {
            "label": "VALUE_EXACT",
            "pattern": [
                {"TEXT": {"REGEX": r"^\d+$"}}, 
                {"TEXT": {"REGEX": r"^" + UNITS_REGEX_RU + r"$"}},
                {"TEXT": {"REGEX": r"^/$"}, "OP": "?"},
                {"TEXT": {"REGEX": r"^" + UNITS_REGEX_RU + r"$"}, "OP": "?"}
            ]
        },
        # (например, "1500°C", "20%")
        {
            "label": "VALUE_EXACT",
            "pattern": [{"TEXT": {"REGEX": r"^\d+" + UNITS_REGEX_RU + r"(?:\s*/\s*" + UNITS_REGEX_RU + r")?$"}}]
        }
    ],
    
    "en": [
        {
            "label": "VALUE_RANGE",
            "pattern": [{"TEXT": {"REGEX": r"^\d+[-–]\d+" + UNITS_REGEX_EN + r"(?:\s*/\s*" + UNITS_REGEX_EN + r")?$"}}]
        },
        {
            "label": "VALUE_RANGE",
            "pattern": [
                {"TEXT": {"REGEX": r"^\d+[-–]\d+$"}}, 
                {"TEXT": {"REGEX": r"^" + UNITS_REGEX_EN + r"$"}},
                {"TEXT": {"REGEX": r"^/$"}, "OP": "?"},
                {"TEXT": {"REGEX": r"^" + UNITS_REGEX_EN + r"$"}, "OP": "?"}
            ]
        },
        {
            "label": "VALUE_LIMIT",
            "pattern": [{"TEXT": {"REGEX": r"^[≤≥<>=]+\d+" + UNITS_REGEX_EN + r"(?:\s*/\s*" + UNITS_REGEX_EN + r")?$"}}]
        },
        {
            "label": "VALUE_LIMIT",
            "pattern": [
                {"TEXT": {"REGEX": r"^[≤≥<>=]+\d+$"}}, 
                {"TEXT": {"REGEX": r"^" + UNITS_REGEX_EN + r"$"}},
                {"TEXT": {"REGEX": r"^/$"}, "OP": "?"},
                {"TEXT": {"REGEX": r"^" + UNITS_REGEX_EN + r"$"}, "OP": "?"}
            ]
        },
        {
            "label": "VALUE_LIMIT",
            "pattern": [
                {"TEXT": {"REGEX": r"^[≤≥<>=]+$"}}, 
                {"TEXT": {"REGEX": r"^\d+$"}}, 
                {"TEXT": {"REGEX": r"^" + UNITS_REGEX_EN + r"$"}},
                {"TEXT": {"REGEX": r"^/$"}, "OP": "?"},
                {"TEXT": {"REGEX": r"^" + UNITS_REGEX_EN + r"$"}, "OP": "?"}
            ]
        },
        {
            "label": "VALUE_EXACT",
            "pattern": [
                {"TEXT": {"REGEX": r"^\d+$"}}, 
                {"TEXT": {"REGEX": r"^" + UNITS_REGEX_EN + r"$"}},
                {"TEXT": {"REGEX": r"^/$"}, "OP": "?"},
                {"TEXT": {"REGEX": r"^" + UNITS_REGEX_EN + r"$"}, "OP": "?"}
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