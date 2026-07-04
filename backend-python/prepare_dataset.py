import os
import argparse
from loguru import logger

from parser.docx_parser import DocxParser
from parser.pymupdf_parser import PyMuPDFParser

def prepare_dataset(source_dir: str, output_file: str):
    """
    Обходит директорию, парсит PDF/DOCX и складывает очищенный текст в один Markdown-файл.
    """
    if not os.path.isdir(source_dir):
        logger.error(f"Директория '{source_dir}' не найдена!")
        return

    logger.info(f"Начинаем сканирование директории: {source_dir}")
    
    docx_parser = DocxParser()
    pdf_parser = PyMuPDFParser()
    
    success_count = 0
    error_count = 0
    
    # Открываем итоговый файл на запись
    with open(output_file, "w", encoding="utf-8") as out_f:
        out_f.write(f"# Датасет для ML\n\nСгенерирован из папки: `{source_dir}`\n\n---\n\n")
        
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                ext = file.lower().split('.')[-1]
                if ext not in ["pdf", "docx"]:
                    continue
                    
                filepath = os.path.join(root, file)
                logger.info(f"Обработка файла: {filepath}")
                
                parsed_data = None
                if ext == "docx":
                    parsed_data = docx_parser.parse(filepath)
                elif ext == "pdf":
                    parsed_data = pdf_parser.parse(filepath)
                    
                if parsed_data and parsed_data.get("metadata", {}).get("status") == "success":
                    text = parsed_data.get("text", "")
                    if text.strip():
                        # Записываем в файл
                        out_f.write(f"## Документ: {file}\n")
                        out_f.write(f"**Путь:** `{filepath}`\n\n")
                        out_f.write(text.strip() + "\n\n---\n\n")
                        success_count += 1
                    else:
                        logger.warning(f"Файл пуст после очистки: {filepath}")
                        error_count += 1
                else:
                    error_msg = parsed_data.get("metadata", {}).get("error_message", "Unknown error") if parsed_data else "Parser returned None"
                    logger.error(f"Ошибка при парсинге {filepath}: {error_msg}")
                    error_count += 1

    logger.success(f"Готово! Успешно обработано: {success_count} файлов. Ошибок/пустых: {error_count}.")
    logger.info(f"Итоговый датасет сохранен в: {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Подготовка чистого текстового датасета для ML.")
    parser.add_argument(
        "--source", 
        type=str, 
        required=True, 
        help="Путь к корневой папке с исходниками (например, ../Information_sources)"
    )
    parser.add_argument(
        "--output", 
        type=str, 
        default="ml_dataset.md", 
        help="Путь к итоговому Markdown файлу (по умолчанию: ml_dataset.md)"
    )
    
    args = parser.parse_args()
    prepare_dataset(args.source, args.output)
