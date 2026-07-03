# parser/base.py

import os
from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseParser(ABC):
    """
    Абстрактный базовый класс для всех парсеров.
    Задает единый интерфейс для извлечения текста.
    """

    @abstractmethod
    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        Основной метод, который обязаны реализовать все наследники.

        :param file_path: Путь к файлу
        :return: Словарь с ключами 'metadata' и 'text'
        """
        pass

    def extract_base_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Общий вспомогательный метод для извлечения базовых метаданных.
        Чтобы не дублировать этот код в каждом парсере.
        """
        return {
            "file_name": os.path.basename(file_path),
        }
