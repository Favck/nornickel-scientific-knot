import docx
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import Table
from docx.text.paragraph import Paragraph

from loguru import logger
from typing import Dict, Any
from .base import BaseParser


class DocxParser(BaseParser):
    """
    Парсер для файлов .docx на базе библиотеки python-docx.
    Читает документ последовательно, сохраняя хронологию текста и таблиц.
    """

    def parse(self, file_path: str) -> Dict[str, Any]:
        logger.info(f"Парсим DOCX: {file_path}")
        metadata = self.extract_base_metadata(file_path)
        extracted_text_blocks = []

        try:
            doc = docx.Document(file_path)

            # Итерируемся по внутреннему XML-дереву, чтобы читать параграфы и таблицы в их реальном порядке
            for child in doc.element.body.iterchildren():
                if isinstance(child, CT_P):
                    para = Paragraph(child, doc)
                    text = para.text.strip()
                    if text:
                        # Проверяем, является ли параграф элементом списка
                        is_list = False
                        if para.style and para.style.name and para.style.name.startswith('List'):
                            is_list = True
                        elif child.xpath('./w:pPr/w:numPr'):
                            is_list = True
                            
                        if is_list and not text.startswith("-"):
                            text = f"- {text}"
                            
                        extracted_text_blocks.append(text)
                        
                elif isinstance(child, CT_Tbl):
                    table = Table(child, doc)
                    for row in table.rows:
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
