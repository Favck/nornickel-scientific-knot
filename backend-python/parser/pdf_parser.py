import os
import re
from typing import Dict, Any

from loguru import logger
import pdfplumber

from .base import BaseParser

logger.add("pipeline_errors.log", rotation="10 MB", level="ERROR")


class PdfParser(BaseParser):
    """
    Парсер для научно-технических PDF-документов.
    Обрабатывает таблицы, двуязычные тексты, двухколоночную верстку, спецсимволы.
    """

    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        Основной метод извлечения структурированного текста.
        """
        metadata = self.extract_base_metadata(file_path)
        metadata["status"] = "success"
        metadata["error_message"] = ""
        extracted_text = ""

        try:
            with pdfplumber.open(file_path) as pdf:
                # Проверка на сканированные документы
                raw_text = "".join(
                    page.extract_text() or "" for page in pdf.pages
                )
                if len(raw_text.replace(" ", "").strip()) == 0:
                    logger.warning(
                        f"Файл {metadata['file_name']} является сканированным "
                        f"документом и требует OCR. Пропуск файла."
                    )
                    metadata["status"] = "error"
                    metadata["error_message"] = "Document requires OCR"
                    return {"text": "", "metadata": metadata}

                # Полный разбор страниц
                for page in pdf.pages:
                    # Отрезаем колонтитулы (5% сверху и снизу)
                    margin = page.height * 0.05
                    try:
                        cropped_page = page.within_bbox((0, margin, page.width, page.height - margin))
                    except ValueError:
                        cropped_page = page

                    # 1. Извлечение таблиц
                    found_tables = cropped_page.find_tables()
                    valid_table_bboxes = []
                    
                    for table_obj in found_tables:
                        table = table_obj.extract()
                        total_cells = 0
                        empty_cells = 0
                        table_text = ""
                        for row in table:
                            # Очищаем ячейки от переносов строк \n
                            clean_row = [str(cell).replace('\n', ' ').strip() for cell in row if cell is not None and str(cell).strip()]
                            total_cells += len(row)
                            empty_cells += (len(row) - len(clean_row))
                            if clean_row:
                                table_text += " | ".join(clean_row) + "\n"
                                
                        # Если больше 70% ячеек пустые — это мусор оформления, игнорируем
                        if total_cells > 0 and (empty_cells / total_cells) < 0.7 and table_text.strip():
                            extracted_text += table_text + "\n"
                            valid_table_bboxes.append(table_obj.bbox)

                    # Маскируем текст таблиц, чтобы он не дублировался в extract_text
                    def not_in_table(obj):
                        if obj.get("object_type") == "char":
                            return not any(
                                bbox[0] - 2 <= obj["x0"] <= bbox[2] + 2 and bbox[1] - 2 <= obj["top"] <= bbox[3] + 2
                                for bbox in valid_table_bboxes
                            )
                        return True
                        
                    masked_page = cropped_page.filter(not_in_table)

                    # 2. Извлечение текста с учетом колоночности
                    if page.width > page.height:
                        # Презентация. Читаем целиком.
                        text = masked_page.extract_text(layout=False)
                        if text:
                            extracted_text += text + "\n"
                    else:
                        # A4 Статья. Разрезаем аппаратно на 2 колонки.
                        center = page.width / 2
                        
                        try:
                            left_part = masked_page.within_bbox((0, margin, center, page.height - margin)).extract_text(layout=False)
                            if left_part: extracted_text += left_part + "\n"
                        except ValueError:
                            pass
                            
                        try:
                            right_part = masked_page.within_bbox((center, margin, page.width, page.height - margin)).extract_text(layout=False)
                            if right_part: extracted_text += right_part + "\n"
                        except ValueError:
                            pass

            # 3. Финальная очистка текста (Юникод, лигатуры)
            extracted_text = self._normalize_text(extracted_text)
            
            return {
                "text": extracted_text,
                "metadata": metadata
            }

        except Exception as e:
            logger.error(f"Ошибка парсинга PDF-файла {metadata['file_name']}: {e}")
            metadata["status"] = "error"
            metadata["error_message"] = str(e)
            return {"text": "", "metadata": metadata}


    def _normalize_text(self, text: str) -> str:
        """
        Заменяет лигатуры, маркеры списков и убирает множественные пробелы.
        """
        # Удаляем нечитаемые битые шрифты (cid:xxx)
        text = re.sub(r'\(cid:\d+\)', '', text)

        # Таблица лигатур и маркеров
        ligatures = {
            '\ufb00': 'ff', '\ufb01': 'fi', '\ufb02': 'fl',
            '\ufb03': 'ffi', '\ufb04': 'ffl', '\ufb05': 'st', '\ufb06': 'st',
            '': '- ', '➢': '- ', '•': '- ', '·': '- '
        }
        for lig, rep in ligatures.items():
            text = text.replace(lig, rep)
            
        text = re.sub(r'([^\.\:;?!\n])\n([a-zа-яA-ZА-Я])', r'\1 \2', text)

        # Убираем множественные пробелы
        text = re.sub(r' {2,}', ' ', text)
        
        # Убираем множественные пустые строки
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Фильтрация строк с нечитаемым мусором (\ufffd) и изолированной пунктуацией
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            # Если в строке больше 10% нечитаемых символов () — это мусор
            if len(line) > 3 and line.count('\ufffd') > len(line) * 0.1:
                continue
                
            line = line.replace('\ufffd', '')
            
            # Пропускаем строки, в которых нет ни букв, ни цифр
            if line.strip() and not re.search(r'[a-zA-Zа-яА-Я0-9]', line):
                continue
                
            cleaned_lines.append(line)
            
        text = '\n'.join(cleaned_lines)
        
        return text.strip()
