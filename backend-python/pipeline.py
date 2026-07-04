import os
import time
import json
import shutil
import hashlib
import requests
from ml.ner_extractor import NerPipeline
from loguru import logger
from parser.docx_parser import DocxParser



GO_BACKEND_URL = "http://localhost:8080/api/v1/entities"
INBOUND_DIR = "inbound"
DONE_DIR = "done"
PENDING_DIR = "pending_send"
DONE_JSON_DIR = "done_json"
REGISTRY_FILE = "processed_files.json"
SCAN_INTERVAL_SEC = 10

logger.add("pipeline_errors.log", rotation="1 MB", level="ERROR")


class FileRegistry:
    """Управляет и логирует состоянием обработанных файлов."""

    def __init__(self, registry_path: str):
        """Инициализация FileRegistry."""
        self.registry_path = registry_path
        self.data = self._load()

    def _load(self) -> dict:
        if not os.path.exists(self.registry_path):
            return {}
        with open(self.registry_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self):
        with open(self.registry_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    def get_hash(self, filepath: str) -> str:
        """Вычисляет MD5 хэш содержимого файла."""
        hash_md5 = hashlib.md5()
        try:
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.error(f"Ошибка вычисления хэша для {filepath}: {e}")
            return ""

    def needs_processing(self, filename: str, current_hash: str) -> bool:
        """Проверяет, является ли файл новым или измененным."""
        record = self.data.get(filename)
        if not record:
            return True
        if (record.get("hash") != current_hash
                or record.get("status") != "success"):
            return True
        return False

    def update_record(
            self, filename: str, filepath: str, file_hash: str, status: str):
        """Обновляет запись о файле в реестре."""
        self.data[filename] = {
            "path": filepath,
            "hash": file_hash,
            "modified_at": time.time(),
            "status": status,
        }
        self._save()


class GoBackendClient:
    """Отвечает за упаковку и отправку данных на Go-сервер."""

    def __init__(self, endpoint_url: str):
        """Инициализация GoBackendClient."""
        self.endpoint_url = endpoint_url

    def send_data(self, metadata: dict, nodes: list, edges: list) -> bool:
        """
        Формирует JSON-пакет и отправляет POST-запрос.

        Возвращает True, если сервер ответил 201 Created.
        """
        payload = {
            "source_metadata": {
                "file_name": metadata.get("file_name", "unknown"),
                "year": metadata.get("year", 2024),
                "geography": metadata.get("geography", "Norilsk"),
            },
            "extracted_data": {
                "nodes": nodes,
                "edges": edges,
            },
        }

        try:
            response = requests.post(
                self.endpoint_url, json=payload, timeout=10)
            if response.status_code == 201:
                logger.success(
                    f"Успешная отправка: {metadata.get('file_name')}")
                return True
            else:
                logger.error(
                    f"Go-сервер вернул ошибку {response.status_code}: "
                    f"{response.text}",
                )
                return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Сетевая ошибка при отправке на Go-бэкенд: {e}")
            return False


class Pipeline:
    """Главный класс оркестрации пайплайна данных."""

    def __init__(self):
        """Инит пайплайна."""
        os.makedirs(INBOUND_DIR, exist_ok=True)
        os.makedirs(DONE_DIR, exist_ok=True)
        os.makedirs(PENDING_DIR, exist_ok=True)
        os.makedirs(DONE_JSON_DIR, exist_ok=True)

        self.registry = FileRegistry(REGISTRY_FILE)
        self.client = GoBackendClient(GO_BACKEND_URL)

        # Инициализируем парсеры
        self.docx_parser = DocxParser()

        # Инициализируем ML модель
        logger.info("Загрузка ML-моделей...")
        self.ner_pipeline = NerPipeline()
        logger.success("ML-модели успешно загружены!")

    def process_file(self, filepath: str, filename: str) -> bool:
        """Обрабатывает один файл от парсинга до отправки."""
        logger.info(f"Запуск обработки файла: {filename}")

        # 1. Парсинг
        if filename.endswith(".docx"):
            parsed_data = self.docx_parser.parse(filepath)
        else:
            logger.warning(f"Парсер для файла {filename} еще не реализован.")
            return False

        if parsed_data.get("metadata", {}).get("status") != "success":
            logger.error(f"Парсинг файла {filename} завершился с ошибкой.")
            return False

        # 2. ML-извлечение
        logger.info("Запуск ML-экстракции...")
        try:
            raw_ml_data = self.ner_pipeline.ner_extractor(parsed_data["text"])
            
            # Отправляем данные от ML
            nodes = raw_ml_data.get("nodes", {})
            edges = raw_ml_data.get("relationships", [])
            
            logger.info(f"ML извлек данные")
            
            # 3. Сохранение в очередь на отправку
            pending_filename = os.path.splitext(filename)[0] + ".json"
            pending_filepath = os.path.join(PENDING_DIR, pending_filename)
            
            payload = {
                "metadata": parsed_data.get("metadata", {}),
                "nodes": nodes,
                "edges": edges
            }
            with open(pending_filepath, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=4, ensure_ascii=False)
            logger.info(f"Результат сохранен в очередь: {pending_filename}")
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка в ML-модуле при обработке {filename}: {e}")
            return False

    def process_pending(self):
        """Пытается отправить сохраненные результаты из очереди на Go бэкенд."""
        if not os.path.exists(PENDING_DIR):
            return
            
        for filename in os.listdir(PENDING_DIR):
            if not filename.endswith(".json"):
                continue
            filepath = os.path.join(PENDING_DIR, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                logger.info(
                    f"Попытка отправки данных из {filename} на бэкенд...")
                is_success = self.client.send_data(
                    data.get("metadata", {}), 
                    data.get("nodes", []), 
                    data.get("edges", [])
                )
                
                if is_success:
                    shutil.move(filepath, os.path.join(DONE_JSON_DIR, filename))
                    logger.info(
                        f"Файл {filename} успешно отправлен и "
                        f"перемещен в '{DONE_JSON_DIR}/'"
                    )
            except Exception as e:
                logger.error(
                    f"Ошибка при обработке {filename} из очереди отправки: {e}")

    def run(self):
        """Бесконечный цикл сканирования."""
        logger.info(
            f"Пайплайн запущен. Отслеживаем папку '{INBOUND_DIR}/' "
            f"каждые {SCAN_INTERVAL_SEC} сек.",
        )

        while True:
            try:
                # Сначала пробуем отправить то, что в очереди
                self.process_pending()
                
                for filename in os.listdir(INBOUND_DIR):
                    filepath = os.path.join(INBOUND_DIR, filename)

                    if not os.path.isfile(filepath):
                        continue

                    file_hash = self.registry.get_hash(filepath)
                    if not file_hash or not self.registry.needs_processing(
                        filename, file_hash,
                    ):
                        continue

                    # Запускаем обработку файла
                    is_success = self.process_file(filepath, filename)

                    # Обновляем статус
                    status_str = "success" if is_success else "failed"
                    self.registry.update_record(
                        filename, filepath, file_hash, status_str)

                    if is_success:
                        shutil.move(filepath, os.path.join(DONE_DIR, filename))
                        logger.info(
                            f"Файл {filename} перемещен в папку '{DONE_DIR}/'")

            except Exception as e:
                logger.critical(
                    f"Критическая ошибка в главном цикле пайплайна: {e}")

            time.sleep(SCAN_INTERVAL_SEC)


if __name__ == "__main__":
    orchestrator = Pipeline()
    orchestrator.run()
