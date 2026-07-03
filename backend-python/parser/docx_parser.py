# parser/docx_parser.py

import docx
from loguru import logger
from typing import Dict, Any
from .base import BaseParser


class DocxParser(BaseParser):
    """
    Парсер для файлов .docx на базе библиотеки python-docx.
    """

    def parse(self, file_path: str) -> Dict[str, Any]:
        logger.info(f"Парсим DOCX: {file_path}")
        metadata = self.extract_base_metadata(file_path)
        extracted_text_blocks = []

        try:
            doc = docx.Document(file_path)

            # Извлекаем параграфы
            for para in doc.paragraphs:
                text = para.text.strip()
                if text:
                    extracted_text_blocks.append(text)

            # Извлекаем текст из таблиц
            for table in doc.tables:
                for row in table.rows:
                    # проходимся по ячейкам таблицы
                    row_data = [
                        cell.text.strip() for cell in row.cells
                        if cell.text.strip()
                    ]
                    if row_data:
                        extracted_text_blocks.append(" | ".join(row_data))

            full_text = "\n".join(extracted_text_blocks)
            metadata["status"] = "success"

        except Exception as e:
            logger.error(f"Ошибка при чтении DOCX файла {file_path}: {e}")
            full_text = ""
            metadata["status"] = "error"
            metadata["error"] = str(e)

        return {
            "metadata": metadata,
            "text": full_text,
        }
