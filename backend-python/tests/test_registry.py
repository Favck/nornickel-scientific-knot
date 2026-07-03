# test_registry.py

import os
import json
import pytest
from pipeline import FileRegistry


@pytest.fixture
def temp_registry_path(tmp_path):
    """Возвращает путь к временному JSON-файлу реестра."""
    return str(tmp_path / "test_registry.json")


@pytest.fixture
def dummy_file(tmp_path):
    """Создает временный текстовый файл для проверки хэширования."""
    file_path = tmp_path / "dummy_doc.txt"
    file_path.write_text("Hello, Nornickel!", encoding="utf-8")
    return str(file_path)


class TestFileRegistry:
    """Тестирование FileRegistry."""

    def test_registry_creates_empty_dict_if_no_file(self, temp_registry_path):
        """Проверяет, что при отсутствии файла реестра создается словарь."""
        registry = FileRegistry(temp_registry_path)
        assert registry.data == {}

    def test_registry_loads_existing_data(self, temp_registry_path):
        """Проверяет, что реестр корректно загружает старые данные из JSON."""
        fake_data = {
            "old_file.docx": {"hash": "abc", "status": "success"},
        }
        with open(temp_registry_path, "w", encoding="utf-8") as f:
            json.dump(fake_data, f)

        registry = FileRegistry(temp_registry_path)

        assert "old_file.docx" in registry.data
        assert registry.data["old_file.docx"]["hash"] == "abc"

    def test_get_hash_success(self, temp_registry_path, dummy_file):
        """Проверяет корректность вычисления MD5 хэша реального файла."""
        registry = FileRegistry(temp_registry_path)

        # MD5 от строки "Hello, Nornickel!":
        expected_hash = "aaeefd3c1bd965152c3c939a23c07d82"
        actual_hash = registry.get_hash(dummy_file)

        assert actual_hash == expected_hash

    def test_get_hash_file_not_found(self, temp_registry_path):
        """
        Проверяет, что при отсутствии файла метод не падает,
        а возвращает пустую строку.
        """
        registry = FileRegistry(temp_registry_path)
        result = registry.get_hash("non_existent_file.pdf")

        assert result == ""

    def test_needs_processing_logic(self, temp_registry_path):
        """Проверяет: нужно обрабатывать файл или нет."""
        registry = FileRegistry(temp_registry_path)
        registry.data = {
            "success_file.pdf": {"hash": "hash_1", "status": "success"},
            "failed_file.pdf": {"hash": "hash_2", "status": "failed"}
        }

        # Сценарий 1: НУЖНО обрабатывать
        assert registry.needs_processing("new_file.pdf", "hash_3") is True

        # Сценарий 2: Файл есть, но статус failed -> НУЖНО обрабатывать
        assert registry.needs_processing("failed_file.pdf", "hash_2") is True

        # Сценарий 3: Файл есть, статус success, но хэш изменился -> НУЖНО
        assert registry.needs_processing(
            "success_file.pdf", "hash_new_version") is True

        # Сценарий 4: Файл есть, статус success, хэш тот же самый -> НЕ нужно
        assert registry.needs_processing("success_file.pdf", "hash_1") is False

    def test_update_record_saves_to_disk(self, temp_registry_path):
        """Проверяет, что при обновлении записи данные сохраняются в JSON."""
        registry = FileRegistry(temp_registry_path)

        registry.update_record(
            filename="report_2024.docx",
            filepath="inbound/report_2024.docx",
            file_hash="xyz789",
            status="success",
        )

        assert "report_2024.docx" in registry.data
        assert registry.data["report_2024.docx"]["status"] == "success"

        with open(temp_registry_path, "r", encoding="utf-8") as f:
            saved_json = json.load(f)

        assert "report_2024.docx" in saved_json
        assert saved_json["report_2024.docx"]["hash"] == "xyz789"
