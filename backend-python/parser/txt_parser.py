from typing import Dict, Any
from loguru import logger
from parser.base import BaseParser

class TxtParser(BaseParser):
    def parse(self, file_path: str) -> Dict[str, Any]:
        metadata = self.extract_base_metadata(file_path)
        metadata["parser"] = "txt"
        metadata["status"] = "success"
        metadata["error_message"] = ""
        extracted_text = ""
        
        try:
            # Сначала пробуем utf-8
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    extracted_text = f.read()
            except UnicodeDecodeError:
                # Фоллбэк на windows-1251
                with open(file_path, "r", encoding="cp1251") as f:
                    extracted_text = f.read()
                    
        except Exception as e:
            logger.error(f"Ошибка парсинга TXT файла {metadata['file_name']}: {e}")
            metadata["status"] = "error"
            metadata["error_message"] = str(e)
            
        return {"text": extracted_text.strip(), "metadata": metadata}
