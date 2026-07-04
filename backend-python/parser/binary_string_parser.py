import re
from typing import Dict, Any
from loguru import logger
from parser.base import BaseParser

class BinaryStringParser(BaseParser):
    def parse(self, file_path: str) -> Dict[str, Any]:
        metadata = self.extract_base_metadata(file_path)
        metadata["parser"] = "binary_string"
        metadata["status"] = "success"
        metadata["error_message"] = ""
        extracted_text = ""
        
        try:
            with open(file_path, "rb") as f:
                data = f.read()
                
            # Извлекаем строки в разных кодировках
            text_utf8 = data.decode("utf-8", errors="ignore")
            text_cp1251 = data.decode("cp1251", errors="ignore")
            
            combined_text = text_utf8 + "\n" + text_cp1251
            
            # Ищем последовательности из минимум 5 читаемых символов
            strings = re.findall(r'[a-zA-Zа-яА-Я0-9\s.,!?:;-]{5,}', combined_text)
            
            # Фильтруем от мусора
            cleaned_strings = []
            for s in strings:
                clean = re.sub(r'\s+', ' ', s).strip()
                # Сохраняем, если есть хотя бы одно слово
                if clean and re.search(r'[a-zA-Zа-яА-Я]{2,}', clean):
                    cleaned_strings.append(clean)
                    
            extracted_text = "\n".join(cleaned_strings)
            
        except Exception as e:
            logger.error(f"Ошибка бинарного парсинга {metadata['file_name']}: {e}")
            metadata["status"] = "error"
            metadata["error_message"] = str(e)
            
        return {"text": extracted_text, "metadata": metadata}
