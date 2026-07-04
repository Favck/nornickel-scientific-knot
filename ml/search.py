
from utils import create_property
from embedder import Embedder
from ner_extractor import NerPipeline



class Search(NerPipeline):

    def __init__(self):
        super().__init__()
        self.embedder = Embedder(model_type="medium")



    def process_query(self, raw_query: str):
        """
        Обрабатывает живой запрос с помощью вашей NER модели, 
        извлекает фильтры (гео и числа) и делает эмбеддинг очищенного текста.
        """
        RUSSIA_LOCATIONS = {"россия", "рф", "сибирь", "кузбасс", "урал", "якутия", "москва", "спб", "норильск", "кольский"}

        # Прогоняем текст через НАШУ кастомную NER-модель (с EntityRuler)
        doc = super().ner_for_search(raw_query)
        
        filters = {
            "numeric": [],
            "geo": None
        }
        
        words_to_remove = set()

        # 1. География: простая проверка по ключевым словам прямо в строке
        query_lower = raw_query.lower()
        if any(loc in query_lower for loc in RUSSIA_LOCATIONS) or "россий" in query_lower:
            filters["geo"] = "Россия"
        elif "зарубеж" in query_lower or "иностран" in query_lower:
            filters["geo"] = "Зарубежье"

        # 2. Бежим по сущностям и собираем числовые фильтры через готовые лейблы
        for ent in doc.ents:
            # Вырезаем гео-сущности из базовой модели, чтобы они не шумели в эмбеддинге
            if ent.label_ in ["GPE", "LOC"]:
                words_to_remove.add(ent.text)
                

            elif ent.label_ in ["VALUE_RANGE", "VALUE_LIMIT", "VALUE_EXACT"]:
                words_to_remove.add(ent.text)
                
    
                prop = create_property(ent) 
                
                if prop:
                    filters["numeric"].append({
                        "raw_entity": ent.text,
                        "operator": prop.get("operator", "="),
                        "value_min": prop.get("value_min"),
                        "value_max": prop.get("value_max"),
                        "value_numeric": prop.get("value_numeric"),
                        "unit": prop.get("unit")
                    })

        # 3. Очищаем текст от найденных параметров и локаций
        clean_text = raw_query
        for word in words_to_remove:
            clean_text = clean_text.replace(word, " ")
        
        # Вычищаем мусорные знаки, которые могли остаться висеть в воздухе
        for op in ["<=", ">=", "<", ">", "=", "–", "-"]:
            clean_text = clean_text.replace(op, " ")
            
        # Убираем двойные пробелы
        clean_text = " ".join(clean_text.split())

        # 4. Генерируем вектор только из смысловой части (например, "хлорное выщелачивание файнштейн")
        query_vector = self.embedder.text_to_vector(clean_text).tolist()

        return {
            "clean_query_text": clean_text,
            "query_vector": query_vector,
            "filters": filters
        }


if __name__=="__main__":
    search = Search()
    test_query = "какие есть современные технологии очистки шахтных вод от сульфатов в Кузбассе если показатели < 250 мг/л"
    print(search.process_query(test_query))