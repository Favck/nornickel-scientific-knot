# test_pipeline.py

import os
import pytest
from unittest.mock import patch, MagicMock, mock_open
from pipeline import Pipeline


class TestPipeline:
    """Тестирование всего пайплайна."""

    @patch("pipeline.NerPipeline")
    def test_adapt_ml_to_backend(self, MockNerPipeline):
        """Проверяет корректность работы адаптера форматов."""
        pipeline = Pipeline()

        ml_data = {
            "nodes": {
                "Material": [{"id": "1", "name": "Файнштейн"}],
                "Process": [{"id": "2", "name": "Выщелачивание"}]
            },
            "relationships": [
                {"source": "2", "target": "1", "type": "uses_material"}
            ]
        }

        nodes, edges = pipeline._adapt_ml_to_backend(ml_data)

        # Проверяем узлы
        assert len(nodes) == 2
        assert any(n["id"] == "1" and n["type"] == "Material" for n in nodes)
        assert any(n["id"] == "2" and n["type"] == "Process" for n in nodes)

        # Проверяем связи
        assert len(edges) == 1
        assert edges[0]["source"] == "2"
        assert edges[0]["target"] == "1"
        assert edges[0]["relation_type"] == "uses_material"
        assert edges[0]["is_contradictory"] is False


    @patch("builtins.open", new_callable=mock_open, read_data="{}")
    @patch("pipeline.json.dump")
    @patch("pipeline.NerPipeline")
    @patch("pipeline.DocxParser")
    def test_process_file_success(
            self, MockParser, MockNerPipeline, mock_json_dump, mock_open):
        """Проверяет сценарий: парсинг -> ML -> сохранение в очередь."""
        pipeline = Pipeline()

        # 1. Настраиваем мок парсера
        pipeline.docx_parser.parse.return_value = {
            "metadata": {"status": "success", "file_name": "test.docx"},
            "text": "Тестовый текст",
        }

        # 2. Настраиваем мок ML модели
        pipeline.ner_pipeline.ner_extractor.return_value = {
            "nodes": {"Material": [{"id": "1", "name": "Файнштейн"}]},
            "relationships": []
        }

        result = pipeline.process_file("inbound/test.docx", "test.docx")

        assert result is True
        pipeline.docx_parser.parse.assert_called_once_with("inbound/test.docx")
        pipeline.ner_pipeline.ner_extractor.assert_called_once_with(
            "Тестовый текст")
        
        # Убеждаемся, что JSON был сохранен
        assert mock_json_dump.call_count == 1


    @patch("pipeline.shutil.move")
    @patch("pipeline.os.listdir")
    @patch("pipeline.os.path.exists", return_value=True)
    @patch("builtins.open", new_callable=mock_open, read_data="{}")
    @patch("pipeline.json.load")
    @patch("pipeline.GoBackendClient")
    @patch("pipeline.NerPipeline")
    def test_process_pending_success(
            self, MockNerPipeline, MockClient, mock_json_load, mock_open,
            mock_exists, mock_listdir, mock_move):
        """Проверяет отправку данных из очереди."""
        pipeline = Pipeline()
        
        mock_listdir.return_value = ["test.json"]
        mock_json_load.return_value = {
            "metadata": {"file_name": "test.docx"},
            "nodes": [],
            "edges": []
        }
        pipeline.client.send_data.return_value = True

        pipeline.process_pending()

        pipeline.client.send_data.assert_called_once()
        mock_move.assert_called_once_with(
            os.path.join("pending_send", "test.json"),
            os.path.join("done_json", "test.json")
        )

    @patch("pipeline.NerPipeline")
    def test_process_file_unsupported_format(self, MockNerPipeline):
        """Проверяет, что система не пытается парсить PDF."""
        pipeline = Pipeline()
        result = pipeline.process_file("inbound/test.pdf", "test.pdf")
        assert result is False

    @patch("pipeline.time.sleep", side_effect=KeyboardInterrupt)
    @patch("pipeline.shutil.move")
    @patch("pipeline.os.listdir")
    @patch("pipeline.os.path.isfile", return_value=True)
    @patch("pipeline.NerPipeline")
    def test_run_moves_file_on_success(
            self, MockNerPipeline, mock_isfile,
            mock_listdir, mock_move, mock_sleep):
        """Проверяет главный цикл при успешной обработке файла."""

        mock_listdir.return_value = ["report.docx"]

        with patch.object(Pipeline, 'process_file', return_value=True) as mock_process, \
             patch.object(Pipeline, 'process_pending') as mock_pending:
            
            pipeline = Pipeline()
            pipeline.registry = MagicMock()
            pipeline.registry.get_hash.return_value = "dummy_hash"
            pipeline.registry.needs_processing.return_value = True

            try:
                pipeline.run()
            except KeyboardInterrupt:
                pass

            mock_pending.assert_called_once()
            mock_process.assert_called_once_with(
                os.path.join("inbound", "report.docx"), "report.docx")
            pipeline.registry.update_record.assert_called_once_with(
                "report.docx", os.path.join(
                    "inbound", "report.docx"), "dummy_hash", "success",
            )
            mock_move.assert_called_once_with(
                os.path.join("inbound", "report.docx"),
                os.path.join("done", "report.docx"),
            )
