import zipfile
import re
from typing import Dict, Any
from loguru import logger
from parser.base import BaseParser

class ArchiveXMLParser(BaseParser):
    def parse(self, file_path: str) -> Dict[str, Any]:
        metadata = self.extract_base_metadata(file_path)
        metadata["parser"] = "archive_xml"
        metadata["status"] = "success"
        metadata["error_message"] = ""
        extracted_text = ""
        
        try:
            with zipfile.ZipFile(file_path, "r") as z:
                for filename in z.namelist():
                    if filename.endswith(".xml"):
                        try:
                            content = z.read(filename).decode("utf-8", errors="ignore")
                            # Удаляем XML теги и заменяем их на пробелы
                            clean = re.sub(r'<[^>]+>', ' ', content)
                            # Убираем лишние пробелы
                            clean = re.sub(r'\s+', ' ', clean).strip()
                            # Если строка имеет буквы, сохраняем
                            if clean and re.search(r'[a-zA-Zа-яА-Я]', clean):
                                extracted_text += clean + "\n"
                        except Exception:
                            pass
        except Exception as e:
            logger.error(f"Ошибка парсинга ZIP/XML файла {metadata['file_name']}: {e}")
            metadata["status"] = "error"
            metadata["error_message"] = str(e)
            
        return {"text": extracted_text.strip(), "metadata": metadata}
