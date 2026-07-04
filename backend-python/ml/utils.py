import re
import uuid
from spacy.pipeline import EntityRuler
from .constants import MODEL, patterns, dictionary



def detector(text: str, subsample: int = 10000) -> str:
    """
    Функция для определения языка текста
    """
    text = text.lower()[:subsample]

    ru_latters = 0
    en_latters = 0
    for char in text:
        if "\u0400" <= char <= "\u04ff" or char == "ё":
            ru_latters += 1
        elif "a"<= char <= "z":
            en_latters += 1
    
    total = ru_latters + en_latters

    if ru_latters/total*100 > 0.2:
        return "ru"
    elif en_latters/total > 0.2:
        return "en"
    return "ru"








def separation(pattern, text) -> dict:
        match = re.match(pattern, text.strip())
        if match:
            data = match.groupdict()
            return data
        return dict()


# .ents - позволяет достать сущности
# .sents - достаёт по предложениям

# ДОПИЛИТЬ нормальное забирание главных слов и проблемы с единицами измерения
def create_property(ent) -> dict:
    """
    Функция для заполнения сущности Property
    """
    limit_pattern = r'(?P<sign>["<>=≤≥]*)\s*(?P<value>\d+(?:[.,]\d+)?)\s*(?P<unit>.+)'
    range_pattern = r"(?P<from_val>\d+)\s*[-–—]\s*(?P<to_val>\d+)\s*(?P<unit>.+)"
    exact_pattern = r"(?P<value>\d+(?:[.,]\d+)?)\s*(?P<unit>%)"

    label = ent.label_
    text = ent.text
    prop_fields = {
        "id":str(uuid.uuid4()),
        "value_raw": text,
        "operator": None,
        "value_numeric": None,
        "value_min": None,
        "value_max": None,
        "unit": None
    }



   
    if label == "VALUE_LIMIT":
        data = separation(limit_pattern, text)
        if data:
            sign = data["sign"]
           
            val = float(data["value"].replace(',', '.'))
            prop_fields["operator"] = sign
            prop_fields["unit"] = data["unit"].strip()
            
            if sign in {"<", "≤"}:
                prop_fields["value_max"] = val
            elif sign in {">", "≥"}:
                prop_fields["value_min"] = val
            elif sign == "=":
                prop_fields["value_numeric"] = val

    elif label == "VALUE_RANGE":
        data = separation(range_pattern, text)
        if data:
            prop_fields["operator"] = "range"
            prop_fields["value_min"] = float(data["from_val"].replace(',', '.'))
            prop_fields["value_max"] = float(data["to_val"].replace(',', '.'))
            prop_fields["unit"] = data["unit"].strip()
            
    elif label == "VALUE_EXACT":
        data = separation(exact_pattern, text)
        if data:
            prop_fields["operator"] = "="
            prop_fields["value_numeric"] = float(data["value"].replace(',', '.'))
            prop_fields["unit"] = data["unit"].strip() # Здесь запишется "%"


    parent_token = ent.root.head

    if parent_token.pos_ == "VERB":
        for child in parent_token.children:
            if child.dep_ == "nsubj":  # Ищем главное подлежащее предложения
                parent_token = child
                break

    parent_name = parent_token.text

    for child in parent_token.children:
        if child.dep_ == "nmod" and child.pos_ == "NOUN":
            parent_name += f" {child.text}"
        
    prop_fields["parameter_name"] = parent_name

    

    return prop_fields



def find_material(sentence,language: str = "ru") -> dict:
    """
    Функция для поиска сущности Material
    """
    
    for token in sentence:
        lemma = token.lemma_.lower()
        if lemma in dictionary[language]:
            new_material = {
                "id": str(uuid.uuid4()),
            "name_ru" : lemma if language == "ru" else None,
            "name_en": lemma if language == "en" else None,
            "synonyms": []
            }

            if dictionary[language][lemma]["synonyms"]:
                new_material["synonyms"] = dictionary[language][lemma]["synonyms"]
            else:
                new_material["synonyms"] = None
            return new_material
    return None


def find_process(sentence, language: str = "ru") -> dict:

    for token in sentence:
        lemma = token.lemma_.lower()
        if lemma in dictionary[language]:
            new_process = {
                "id": str(uuid.uuid4()),
                "name_ru": lemma if language == "ru" else None,
                "name_en": lemma if language == "en" else None,
                "synonyms": []
            }

            if dictionary[language][lemma]["synonyms"]:
                new_process["synonyms"] = dictionary[language][lemma]["synonyms"]
            else:
                new_process["synonyms"] = None
                
            return new_process
            
    return None


def find_equipment(sentence, language: str = "ru") -> dict:
    for token in sentence:
        lemma = token.lemma_.lower()
        if lemma in dictionary[language]:
            new_equipment = {
                "id": str(uuid.uuid4()),
                "name_ru": lemma if language == "ru" else None,
                "name_en": lemma if language == "en" else None
            }
            return new_equipment
            
    return None

def find_publication(text: str) -> dict:
    year_match = re.search(r"\b(19\d{2}|20[0-2]\d)\b", text)
    year = int(year_match.group(0)) if year_match else None
    

    russian_keywords = ["рф", "россия", "патент", "гипроникель", "норникель", "вестник", "университет"]
    text_lower = text.lower()
    
    if any(word in text_lower for word in russian_keywords):
        geography = "Россия"
    else:
        geography = "Зарубежье"
        
    # 3. Достаем заголовок (берём самую первую непустую строку текста)
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    title = lines[0] if lines else "Неизвестная публикация"
    

    if len(title) > 150:
        title = title[:147] + "..."

    return {
        "id": str(uuid.uuid4()),
        "title": title,
        "year": year,
        "geography": geography
    }



def find_experts(sentence) -> list:
    experts = []
    for ent in sentence.ents:
        if ent.label_ == "PER":
            new_expert = {
                "id": str(uuid.uuid4()),
                "full_name": ent.text,
                "organization": None
            }
            if ent.root.head.label_ == "ORG":
                new_expert["organization"] = ent.root.head.text
            experts.append(new_expert)
    return experts


def find_facilities(sentence) -> list:
    facilities = []
    russian_keywords = ["рф", "россия", "нии", "гмк", "оао", "ооо", "завод", "фабрика", "институт"]
    
    for ent in sentence.ents:
        if ent.label_ == "ORG":
            text_lower = ent.text.lower()
            geography = "Россия" if any(word in text_lower for word in russian_keywords) else "Зарубежье"
            
            new_facility = {
                "id": str(uuid.uuid4()),
                "name_ru": ent.text,
                "name_en": None,
                "geography": geography
            }
            facilities.append(new_facility)
    return facilities