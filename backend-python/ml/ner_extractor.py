import spacy
import uuid
from spacy.pipeline import EntityRuler
from .constants import  patterns
from .utils import detector, find_equipment, find_experts, find_material, find_facilities, find_process, find_publication, create_property





class NerPipeline():
    
    def __init__(self):
        self.nlp_ru = spacy.load("ru_core_news_md")
        self.nlp_en = spacy.load("en_core_web_md")

        self.ruler_en = self.nlp_en.add_pipe("entity_ruler", before="ner")
        self.ruler_en.add_patterns(patterns["en"])

        self.ruler_ru = self.nlp_ru.add_pipe("entity_ruler", before="ner")
        self.ruler_ru.add_patterns(patterns["ru"])

        self.models = {
            "en": self.nlp_en,
            "ru": self.nlp_ru
        }


    def ner_extractor(self, text: str) -> dict:

        result = {
            "nodes": {
                "Material": [], "Process": [], "Equipment": [], 
                "Property": [], "Publication": [], "Expert": [], "Facility": []
            },
            "relationships": []
        }
        language = detector(text)
        pub = find_publication(text)
        if pub: result["nodes"]["Publication"].append(pub)

        doc = self.models[language](text)


        for sentence in doc.sents:
            
            # Словарные термины
            mat = find_material(sentence, language)
            if mat: result["nodes"]["Material"].append(mat)
                
            proc = find_process(sentence, language)
            if proc: result["nodes"]["Process"].append(proc)
                
            equip = find_equipment(sentence, language)
            if equip: result["nodes"]["Equipment"].append(equip)

            # Числа, люди и заводы из ents
            for ent in sentence.ents:
                prop = None
                if ent.label_ in ["VALUE_RANGE", "VALUE_LIMIT", "VALUE_EXACT"]:
                    prop = create_property(ent) # Твоя функция
                    if prop: result["nodes"]["Property"].append(prop)
                    
                elif ent.label_ == "PER":
                    result["nodes"]["Expert"].append({
                        "id": str(uuid.uuid4()), "full_name": ent.text
                    })
                    
                elif ent.label_ == "ORG":
                    result["nodes"]["Facility"].append({
                        "id": str(uuid.uuid4()), "name_ru": ent.text
                    })

                if proc and prop: 
                    result["relationships"].append({
                        "type": "operates_at_condition",
                        "source": proc["id"],
                        "target": prop["id"]
                    })
                
                if pub and prop:
                    result["relationships"].append({
                        "type": "described_in",
                        "source": prop["id"], 
                        "target": pub["id"]
                    })

            if proc and mat:
                result["relationships"].append({
                    "type": "uses_material",
                    "source": proc["id"],
                    "target": mat["id"]
                })



        return result

    def ner_for_search(self, query):
        language = detector(query)
        return self.models[language](query)




if __name__=="__main__":
    text = """
    Интенсификация процесса хлорного растворения медно-никелевых файнштейнов в современных условиях.
    В 2024 году на базе научно-исследовательского центра ООО Институт Гипроникель (Россия) были проведены полупромышленные испытания новой технологии переработки сырья. Ведущий исследователь Четверкин Николай Васильевич предложил модифицировать классическое хлорное выщелачивание. 
    В качестве исходного сырья использовался высокосортный медно-никелевый файнштейн, поставляемый с площадки Кольская ГМК. Реакция протекала в агрессивной среде, для чего применялся специализированный титановый автоклав. 
    В ходе опытов установлено, что оптимальная температура пульпы составляет 80–85 °C. При этом концентрация активного хлора в маточном растворе строго поддерживалась на уровне 200–300 мг/л. Давление кислорода зафиксировано: ≥2.5 атм. Анализ проб показал, что в очищенном растворе сухой остаток не превышает ≤1000 мг/дм³. Скорость потока реагентов достигла 1.5 м/с.
    В результате процесса формируется обогащенный анодный шлам, а эффективность извлечения цветных металлов равна 98 %.
    """

    pipe = NerPipeline()
    print(pipe.ner_extractor(text))

