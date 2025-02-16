import pytest
from unittest.mock import AsyncMock, Mock, patch
from src.services.reaction_handler import ReactionHandler

class TestReactionHandler:
    @pytest.fixture
    def reaction_handler(self, mock_config_service):
        return ReactionHandler(
            mock_config_service,
        )

    @pytest.mark.asyncio
    async def test_fetch_reaction(self, reaction_handler):
        """リアクションの取得テスト"""
        ### Given
        message_id = "123456789"
        message_content = "テストメッセージ"
        
        # OpenAIClientのモック
        reaction_handler.openai_client.get_response = AsyncMock(return_value="良い 面白い")

        ### When
        await reaction_handler.fetchReaction(message_id, message_content)

        ### Then
        assert message_id in reaction_handler.message_reactions
        assert len(reaction_handler.message_reactions[message_id]) > 0
        assert "👍" in reaction_handler.message_reactions[message_id]  # "良い"に対応する絵文字
        assert "😂" in reaction_handler.message_reactions[message_id]  # "面白い"に対応する絵文字

    def test_get_reactions(self, reaction_handler):
        """保存されたリアクションの取得テスト"""
        ### Given
        message_id = "123456789"
        test_reactions = ["👍", "❤️"]
        reaction_handler.message_reactions[message_id] = test_reactions

        ### When
        result = reaction_handler.getReactions(message_id)

        ### Then
        assert result == test_reactions

    def test_get_reactions_not_found(self, reaction_handler):
        """存在しないメッセージIDのリアクション取得テスト"""
        ### Given
        message_id = "nonexistent"

        ### When/Then
        with pytest.raises(KeyError):
            reaction_handler.getReactions(message_id) 