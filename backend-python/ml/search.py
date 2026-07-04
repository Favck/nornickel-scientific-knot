
from .utils import create_property
from .embedder import Embedder
from .ner_extractor import NerPipeline



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

        doc = super().ner_for_search(raw_query)
        
        filters = {
            "numeric": [],
            "geo": None
        }
        
        words_to_remove = set()


        query_lower = raw_query.lower()
        if any(loc in query_lower for loc in RUSSIA_LOCATIONS) or "россий" in query_lower:
            filters["geo"] = "Россия"
        elif "зарубеж" in query_lower or "иностран" in query_lower:
            filters["geo"] = "Зарубежье"

<<<<<<< HEAD:ml/search.py

=======
        # Бежим по сущностям и собираем числовые фильтры через готовые лейблы
>>>>>>> develop:backend-python/ml/search.py
        for ent in doc.ents:

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

<<<<<<< HEAD:ml/search.py
=======
        # Очищаем текст от найденных параметров и локаций
>>>>>>> develop:backend-python/ml/search.py
        clean_text = raw_query
        for word in words_to_remove:
            clean_text = clean_text.replace(word, " ")
        

        for op in ["<=", ">=", "<", ">", "=", "–", "-"]:
            clean_text = clean_text.replace(op, " ")
            

        clean_text = " ".join(clean_text.split())

<<<<<<< HEAD:ml/search.py
        
=======

>>>>>>> develop:backend-python/ml/search.py
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