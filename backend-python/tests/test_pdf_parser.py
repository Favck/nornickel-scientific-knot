import os
import pytest
from unittest.mock import patch, MagicMock

from parser.pdf_parser import PdfParser


@pytest.fixture
def parser():
    return PdfParser()


def test_pdf_parser_robustness(parser, tmp_path):
    """
    Robustness: Попытка распарсить несуществующий файл не должна ронять систему.
    Должна возвращать status: error и писать в лог.
    """
    fake_path = str(tmp_path / "missing.pdf")
    
    result = parser.parse(fake_path)
    
    assert result["metadata"]["status"] == "error"
    assert "error" in result["metadata"]["status"]
    assert result["text"] == ""
    assert result["metadata"]["file_name"] == "missing.pdf"


@patch('parser.pdf_parser.pdfplumber.open')
def test_pdf_parser_scan_check(mock_open, parser, tmp_path):
    """
    Scan Check: Если документ пустой (скан без OCR), парсер возвращает ошибку.
    """
    fake_path = str(tmp_path / "scan.pdf")
    
    mock_pdf = MagicMock()
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "   \n  "
    mock_pdf.pages = [mock_page]
    
    # Настраиваем контекстный менеджер
    mock_open.return_value.__enter__.return_value = mock_pdf
    
    result = parser.parse(fake_path)
    
    assert result["metadata"]["status"] == "error"
    assert "OCR" in result["metadata"]["error_message"]
    assert result["text"] == ""


@patch('parser.pdf_parser.pdfplumber.open')
def test_pdf_parser_happy_path(mock_open, parser, tmp_path):
    """
    Happy Path: Парсинг таблиц, колонок, спецсимволов и лигатур.
    """
    fake_path = str(tmp_path / "valid.pdf")
    
    mock_pdf = MagicMock()
    mock_page = MagicMock()
    
    # 1. Скан-чек должен пройти
    mock_page.extract_text.return_value = "Some text"
    
    # Геометрия страницы
    mock_page.width = 600
    mock_page.height = 800
    
    # Мокаем cropped_page и within_bbox
    mock_cropped = MagicMock()
    mock_page.within_bbox.return_value = mock_cropped
    mock_cropped.width = 600
    mock_cropped.height = 800
    
    # Таблицы (из mock_cropped)
    mock_table_obj = MagicMock()
    mock_table_obj.bbox = (10, 10, 100, 100)
    mock_table_obj.extract.return_value = [
        ["сульфаты", "<=200 мг/л", " "], # " " will be filtered
        ["ОВП", "150 °C", ""]
    ]
    mock_cropped.find_tables.return_value = [mock_table_obj]
    mock_cropped.filter.return_value = mock_cropped
    
    # Текст из двух колонок (из mock_cropped)
    # mock_page.within_bbox возвращает mock_cropped для полного кропа
    mock_page.within_bbox.return_value = mock_cropped
    
    # mock_cropped.within_bbox возвращает половинки
    def bbox_side_effect(bbox):
        m = MagicMock()
        if bbox[0] == 0 and bbox[2] == 300:  # Левая половинка
            m.extract_text.return_value = "Left1 Left2\nLeft3\ufb01ltration" # \ufb01 = fi
        elif bbox[0] == 300 and bbox[2] == 600:  # Правая половинка
            m.extract_text.return_value = "Right1 Right2"
        else:
            m.extract_text.return_value = ""
        return m
        
    mock_cropped.within_bbox.side_effect = bbox_side_effect
    
    mock_pdf.pages = [mock_page]
    mock_open.return_value.__enter__.return_value = mock_pdf
    
    result = parser.parse(fake_path)
    
    assert result["metadata"]["status"] == "success"
    assert result["metadata"]["error_message"] == ""
    
    text = result["text"]
    
    # Проверка склейки таблиц
    assert "сульфаты | <=200 мг/л" in text
    assert "ОВП | 150 °C" in text
    
    # Проверка порядка колонок
    assert text.find("Left1 Left2") < text.find("Right1 Right2")
    
    # Проверка раскрытия лигатур
    assert "Left3filtration" in text
