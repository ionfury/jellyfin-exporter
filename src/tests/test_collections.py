import pytest
import json
import logging
from unittest.mock import patch, Mock
from prometheus_client import CollectorRegistry, generate_latest
from collectors import JellyfinSessions, JellyfinItems, JellyfinUsers

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.mark.parametrize(
    "mocked_response_file, expected_metrics_file",
    [("src/tests/sessions/api_1.json", "src/tests/sessions/metrics_1.txt")],
)
@patch("requests.get")
def test_sessions_collector(mock_get, mocked_response_file, expected_metrics_file):
    with open(mocked_response_file, "r") as file:
        mocked_data = json.load(file)

    with open(expected_metrics_file, "r") as file:
        expected_metrics = file.read().strip()

    mock_request_api = Mock()
    mock_request_api.return_value = mocked_data

    registry = CollectorRegistry()
    collector = JellyfinSessions(mock_request_api, logger.critical)
    registry.register(collector)

    generated_metrics = generate_latest(registry).decode("utf-8").strip()

    assert generated_metrics == expected_metrics


@pytest.mark.parametrize(
    "mocked_response_file, expected_metrics_file",
    [("src/tests/items/api_1.json", "src/tests/items/metrics_1.txt")],
)
@patch("requests.get")
def test_items_collector(mock_get, mocked_response_file, expected_metrics_file):
    with open(mocked_response_file, "r") as file:
        mocked_data = json.load(file)

    with open(expected_metrics_file, "r") as file:
        expected_metrics = file.read().strip()

    mock_request_api = Mock()
    mock_request_api.return_value = mocked_data

    registry = CollectorRegistry()
    collector = JellyfinItems(mock_request_api, logger.critical)
    registry.register(collector)

    generated_metrics = generate_latest(registry).decode("utf-8").strip()

    assert generated_metrics == expected_metrics


@pytest.mark.parametrize(
    "mocked_response_file, expected_metrics_file",
    [("src/tests/users/api_1.json", "src/tests/users/metrics_1.txt")],
)
@patch("requests.get")
def test_users_collector(mock_get, mocked_response_file, expected_metrics_file):
    with open(mocked_response_file, "r") as file:
        mocked_data = json.load(file)

    with open(expected_metrics_file, "r") as file:
        expected_metrics = file.read().strip()

    mock_request_api = Mock()
    mock_request_api.return_value = mocked_data

    registry = CollectorRegistry()
    collector = JellyfinUsers(mock_request_api, logger.critical)
    registry.register(collector)

    generated_metrics = generate_latest(registry).decode("utf-8").strip()

    assert generated_metrics == expected_metrics
