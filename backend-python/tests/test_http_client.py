import pytest
import requests
from unittest.mock import patch, Mock
from pipeline import GoBackendClient


@pytest.fixture
def client():
    """Создает экземпляр клиента с фейковым URL для тестов."""
    return GoBackendClient("http://fake-backend.com/api/v1/entities")


@pytest.fixture
def sample_payload_data():
    """Возвращает валидные тестовые данные."""
    metadata = {
        "file_name": "test_report.pdf",
        "year": 2025,
        "geography": "Monchegorsk",
    }
    nodes = [{"id": "node_1", "type": "Process", "name": "Очистка"}]
    edges = [
        {"source": "node_1", "target": "node_2", "relation_type": "limits"},
    ]
    return metadata, nodes, edges


class TestGoBackendClient:
    """Тестирование отправки данных на Go backend."""

    @patch("pipeline.requests.post")
    def test_send_data_success_201(
            self, mock_post, client, sample_payload_data):
        """Проверяет: сервер вернул 201 Created."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_post.return_value = mock_response

        metadata, nodes, edges = sample_payload_data

        result = client.send_data(metadata, nodes, edges)

        assert result is True, "Метод должен вернуть True при статусе 201"

        # Проверяем, что requests.post был вызван ровно 1 раз
        mock_post.assert_called_once()

        # Извлекаем данные, которые наш код попытался отправить в requests.post
        called_args, called_kwargs = mock_post.call_args
        sent_json = called_kwargs["json"]

        assert sent_json["source_metadata"]["file_name"] == "test_report.pdf"
        assert sent_json["extracted_data"]["nodes"] == nodes

    @patch("pipeline.requests.post")
    def test_send_data_server_error_500(
            self, mock_post, client, sample_payload_data):
        """Проверяет обработку серверной ошибки."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response

        metadata, nodes, edges = sample_payload_data
        result = client.send_data(metadata, nodes, edges)

        assert (
            result is False
        ), "Метод должен вернуть False, если статус не 201"

    @patch("pipeline.requests.post")
    def test_send_data_network_timeout(
            self, mock_post, client, sample_payload_data):
        """Проверяет отказоустойчивость: что будет, если отвалится интернет."""
        mock_post.side_effect = requests.exceptions.Timeout(
            "Сервер не отвечает",
        )

        metadata, nodes, edges = sample_payload_data
        result = client.send_data(metadata, nodes, edges)

        assert (
            result is False
        ), "При сетевой ошибке скрипт должен вернуть False"

    @patch("pipeline.requests.post")
    def test_send_data_missing_metadata_uses_defaults(self, mock_post, client):
        """Проверяет использование значений по умолчанию."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_post.return_value = mock_response

        result = client.send_data(metadata={}, nodes=[], edges=[])

        assert result is True

        sent_json = mock_post.call_args.kwargs["json"]

        assert sent_json["source_metadata"]["file_name"] == "unknown"
        assert sent_json["source_metadata"]["year"] == 2024
        assert sent_json["source_metadata"]["geography"] == "Norilsk"
