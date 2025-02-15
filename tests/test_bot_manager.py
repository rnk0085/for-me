import pytest
from unittest.mock import Mock, patch
from src.services.bot_manager import DiscordBotManager

class TestBotManager:
    @pytest.fixture
    def bot_manager(self):
        bot = Mock()
        reactions = Mock()
        openai_client = Mock()
        discord_client = Mock()
        config_service = Mock()
        
        return DiscordBotManager(
            bot=bot,
            reactions=reactions,
            openai_client=openai_client,
            discord_client=discord_client,
            config_service=config_service
        )
    
    def test_is_auto_response_channel(self, bot_manager):
        bot_manager.config_service.get_channel_id.side_effect = [
            100,  # FREE_TALK
            200,  # FB
            300   # PRAISE
        ]
        
        assert bot_manager.is_auto_response_channel(100) == True
        assert bot_manager.is_auto_response_channel(999) == False
    
    def test_should_auto_respond(self, bot_manager):
        bot_manager.config_service.get_channel_id.return_value = 100
        
        assert bot_manager.should_auto_respond(100, False) == True
        assert bot_manager.should_auto_respond(100, True) == False 