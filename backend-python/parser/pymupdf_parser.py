import fitz  # PyMuPDF
import re
from loguru import logger
from typing import Dict, Any

from .base import BaseParser

class PyMuPDFParser(BaseParser):
    def parse(self, file_path: str, **kwargs) -> Dict[str, Any]:
        """
        Парсит PDF-файл с использованием библиотеки PyMuPDF (fitz).
        Извлекает таблицы и текст (с учетом 2-колоночной верстки).
        Обрезает верхние и нижние 5% (колонтитулы).
        """
        metadata = self.extract_base_metadata(file_path)
        metadata["parser"] = "pymupdf"
        metadata["status"] = "success"
        metadata["error_message"] = ""
        extracted_text = ""

        try:
            doc = fitz.open(file_path)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_rect = page.rect
                
                # Обрезка колонтитулов (5% сверху и снизу)
                margin = page_rect.height * 0.05
                clip_rect = fitz.Rect(0, margin, page_rect.width, page_rect.height - margin)
                
                # 1. Извлечение таблиц
                # Ищем таблицы в пределах обрезки
                tables = page.find_tables(clip=clip_rect)
                table_bboxes = []
                
                if tables and tables.tables:
                    for table in tables.tables:
                        table_bboxes.append(table.bbox)
                        table_data = table.extract()
                        
                        total_cells = 0
                        empty_cells = 0
                        table_text = ""
                        
                        for row in table_data:
                            # Очищаем ячейки
                            clean_row = [str(cell).replace('\n', ' ').strip() for cell in row if cell is not None and str(cell).strip()]
                            total_cells += len(row)
                            empty_cells += (len(row) - len(clean_row))
                            if clean_row:
                                table_text += " | ".join(clean_row) + "\n"
                                
                        # Фильтруем "мусорные" рамки (слайды и декорации)
                        if total_cells > 0 and (empty_cells / total_cells) < 0.7 and table_text.strip():
                            extracted_text += table_text + "\n"

                blocks = page.get_text("blocks", clip=clip_rect, sort=True)
                
                for block in blocks:
                    if len(block) >= 7 and block[6] == 0:
                        b_rect = fitz.Rect(block[:4])
                        # Проверяем, не пересекается ли блок с одной из таблиц
                        in_table = False
                        for t_bbox in table_bboxes:
                            t_rect = fitz.Rect(t_bbox)
                            # Если пересечение значительное
                            if b_rect.intersects(t_rect):
                                in_table = True
                                break
                                
                        if not in_table:
                            text_chunk = block[4]
                            if text_chunk.strip():
                                extracted_text += text_chunk + "\n"
                                
            doc.close()
            
            # 3. Финальная очистка
            extracted_text = self._normalize_text(extracted_text)
            
            return {
                "text": extracted_text,
                "metadata": metadata
            }

        except Exception as e:
            logger.error(f"Ошибка парсинга PDF-файла (PyMuPDF) {metadata['file_name']}: {e}")
            metadata["status"] = "error"
            metadata["error_message"] = str(e)
            return {"text": "", "metadata": metadata}

    def _normalize_text(self, text: str) -> str:
        """
        Заменяет лигатуры, маркеры списков, вырезает FFFD и склеивает переносы строк.
        """
        # Таблица лигатур и маркеров
        ligatures = {
            '\ufb00': 'ff', '\ufb01': 'fi', '\ufb02': 'fl',
            '\ufb03': 'ffi', '\ufb04': 'ffl', '\ufb05': 'st', '\ufb06': 'st',
            '': '- ', '➢': '- ', '•': '- ', '·': '- '
        }
        for lig, rep in ligatures.items():
            text = text.replace(lig, rep)
            
        # Умная склейка предложений
        text = re.sub(r'([^\.\:;?!\n])\n([a-zа-яA-ZА-Я])', r'\1 \2', text)

        # Убираем множественные пробелы
        text = re.sub(r' {2,}', ' ', text)
        
        # Убираем множественные пустые строки
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Фильтрация строк с нечитаемым мусором (\ufffd) и изолированной пунктуацией
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            if len(line) > 3 and line.count('\ufffd') > len(line) * 0.1:
                continue
                
            line = line.replace('\ufffd', '')
            line = line.replace('\x00', '')
            
            if line.strip() and not re.search(r'[a-zA-Zа-яА-Я0-9]', line):
                continue
                
            cleaned_lines.append(line)
            
        text = '\n'.join(cleaned_lines)
        
        return text.strip()
