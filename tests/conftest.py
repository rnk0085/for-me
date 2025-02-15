import pytest
from unittest.mock import Mock, AsyncMock
from src.models.bot import Bot
from src.services.config_service import ConfigService
from src.services.openai_client import OpenAIClient
from src.services.reaction_handler import ReactionHandler

@pytest.fixture
def mock_bot():
    return Bot(
        mbti_type="ENTP",
        mbti_file_name="entp.txt",
        interests=["programming", "AI", "music"]
    )

@pytest.fixture
def mock_discord_client():
    client = Mock()
    client.user = Mock()
    client.user.mentioned_in = AsyncMock(return_value=False)
    client.start = AsyncMock()
    return client

@pytest.fixture
def mock_config_service():
    service = Mock(spec=ConfigService)
    service.get_discord_token.return_value = "mock-token"
    service.get_channel_id.return_value = "123456789"
    service.get_reaction_rate.return_value = 0.5
    return service

@pytest.fixture
def mock_openai_client():
    client = Mock(spec=OpenAIClient)
    client.get_response = AsyncMock(return_value="Mock response")
    return client

@pytest.fixture
def mock_reaction_manager():
    manager = Mock(spec=ReactionHandler)
    manager.fetch_reactions = AsyncMock()
    manager.get_available_reactions = Mock(return_value=["👍", "❤️"])
    return manager 