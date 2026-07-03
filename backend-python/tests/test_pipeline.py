# test_pipeline.py

import os
import pytest
from unittest.mock import patch, MagicMock
from pipeline import Pipeline


class TestPipeline:
    """Тестирование всего пайплайна."""

    def test_simulate_ml_extraction(self):
        """Проверяет, что заглушка ML возвращает валидные списки."""
        pipeline = Pipeline()
        nodes, edges = pipeline.simulate_ml_extraction("Любой текст")

        assert isinstance(nodes, list)
        assert len(nodes) > 0
        assert isinstance(edges, list)

    @patch("pipeline.DocxParser")
    @patch("pipeline.GoBackendClient")
    def test_process_file_success(self, MockClient, MockParser):
        """Проверяет парсинг -> ML -> отправка."""
        pipeline = Pipeline()

        # 1. Настраиваем мок парсера: успешно прочитал файл
        pipeline.docx_parser.parse.return_value = {
            "metadata": {"status": "success", "file_name": "test.docx"},
            "text": "Тестовый извлеченный текст",
        }

        # 2. Настраиваем мок клиента: "как будто" получил 201 от Go
        pipeline.client.send_data.return_value = True

        result = pipeline.process_file("inbound/test.docx", "test.docx")

        assert result is True
        pipeline.docx_parser.parse.assert_called_once_with("inbound/test.docx")
        pipeline.client.send_data.assert_called_once()

    def test_process_file_unsupported_format(self):
        """
        Проверяет, что система не пытается парсить PDF и возвращает False.
        """
        pipeline = Pipeline()
        result = pipeline.process_file("inbound/test.pdf", "test.pdf")
        assert result is False

    # Тест бесконечного цикла
    @patch("pipeline.time.sleep", side_effect=KeyboardInterrupt)
    @patch("pipeline.shutil.move")
    @patch("pipeline.os.listdir")
    @patch("pipeline.os.path.isfile", return_value=True)
    def test_run_moves_file_on_success(
            self, mock_isfile, mock_listdir, mock_move, mock_sleep):
        """
        Проверяет, что если файл успешно обработан,
        он переносится в папку done/ и записывается в реестр.
        """

        mock_listdir.return_value = ["report.docx"]

        with patch.object(
                Pipeline, 'process_file', return_value=True) as mock_process:

            pipeline = Pipeline()
            pipeline.registry = MagicMock()
            pipeline.registry.get_hash.return_value = "dummy_hash"
            pipeline.registry.needs_processing.return_value = True

            try:
                pipeline.run()
            except KeyboardInterrupt:
                pass  # Ловим искусственную остановку цикла

            # 1. Проверяем, что файл был передан в обработку
            mock_process.assert_called_once_with(
                os.path.join("inbound", "report.docx"), "report.docx")

            # 2. Проверяем, что реестр обновился со статусом success
            pipeline.registry.update_record.assert_called_once_with(
                "report.docx",
                os.path.join("inbound", "report.docx"),
                "dummy_hash",
                "success",
            )

            # 3. Проверяем, что файл был физически перенесен в папку done/
            mock_move.assert_called_once_with(
                os.path.join("inbound", "report.docx"),
                os.path.join("done", "report.docx"),
            )
