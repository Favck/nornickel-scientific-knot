import spacy
import uuid
from spacy.pipeline import EntityRuler
from .constants import  patterns
from .utils import detector, find_equipment, find_experts, find_material, find_facilities, find_process, find_publication, create_property, find_all_experiments





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
                "Property": [],"Experiment":[], "Publication": [], "Expert": [], "Facility": []
            },
            "relationships": []
        }
        language = detector(text)
        pub = find_publication(text)
        if pub: result["nodes"]["Publication"].append(pub)

        doc = self.models[language](text)


        for sentence in doc.sents:
            
            materials = find_material(sentence, language)
            processes = find_process(sentence, language)
            equipments = find_equipment(sentence, language)
            experiments = find_all_experiments(sentence)

            properties = []
            experts = []
            facilities = []
            
           
            for ent in sentence.ents:
                if ent.label_ in ["VALUE_RANGE", "VALUE_LIMIT", "VALUE_EXACT"]:
                    prop = create_property(ent)  
                    if prop: 
                        prop["_token_idx"] = ent.root.i
                        properties.append(prop)
                    
                elif ent.label_ == "PER":
                    expert ={
                        "id": str(uuid.uuid4()),
                        "full_name": ent.text,
                        "organization": ent.root.head.text if ent.root.head.ent_type_ == "ORG" else None,
                        "_token_idx":ent.root.i
                    }
                    experts.append(expert)


                elif ent.label_ == "ORG":
                    text_lower = ent.text.lower()
                    russian_keywords = ["рф", "россия", "нии", "гмк", "оао", "ооо", "завод", "фабрика", "институт"]
                    geography = "Россия" if any(word in text_lower for word in russian_keywords) else "Зарубежье"
                    
                    facility = {
                        "id": str(uuid.uuid4()), 
                        "name_ru": ent.text,
                        "geography": geography,
                        "_token_idx": ent.root.i
                    }
                    facilities.append(facility)    

            if processes and materials:
                for mat in materials:
                    closest_proc = min(processes, key=lambda p: abs(p["_token_idx"] - mat["_token_idx"]))
                    result["relationships"].append({
                        "type":"uses_material",
                        "source": closest_proc["id"],
                        "target": mat["id"]
                    })

            if processes and properties:
                for prop in properties:
                    closest_proc = min(processes, key=lambda p: abs(p["_token_idx"] - prop["_token_idx"]))
                    result["relationships"].append({
                        "type": "operates_at_condition",
                        "source": closest_proc["id"],
                        "target": prop["id"]
                })

            if pub and properties:
                for prop in properties:
                    result["relationships"].append({
                        "type": "described_in",
                        "source": prop["id"], 
                        "target": pub["id"]
                    })
            
            # Связь эксперта и фабрики если они рядом
            if experts and facilities:
                for exp in experts:
                    closest_fac = min(facilities, key=lambda f: abs(f["_token_idx"] - exp["_token_idx"]))
                    # Если они в пределах, например, 5 слов друг от друга
                    if abs(exp["_token_idx"] - closest_fac["_token_idx"]) < 5:
                        result["relationships"].append({
                            "type": "works_at",
                            "source": exp["id"],
                            "target": closest_fac["id"]
                        })

            for nodes_list in [materials, processes, equipments, properties, experts, facilities]:
                for node in nodes_list:
                    node.pop("_token_idx", None)

            result["nodes"]["Material"].extend(materials)
            result["nodes"]["Process"].extend(processes)
            result["nodes"]["Equipment"].extend(equipments)
            result["nodes"]["Property"].extend(properties)
            result["nodes"]["Expert"].extend(experts)
            result["nodes"]["Facility"].extend(facilities)

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

