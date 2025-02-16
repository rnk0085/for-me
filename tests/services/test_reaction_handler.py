import pytest
from unittest.mock import AsyncMock, Mock, patch
from src.services.reaction_handler import ReactionHandler

class TestReactionHandler:
    @pytest.fixture
    def reaction_handler(self, mock_config_service):
        with patch('src.services.reaction_handler.get_prompt', return_value="テスト用プロンプト"):
            return ReactionHandler(mock_config_service)

    @pytest.mark.asyncio
    async def test_fetch_reaction(self, reaction_handler):
        """リアクションの取得テスト"""
        ### Given
        message_id = "123456789"
        message_content = "テストメッセージ"
        
        # OpenAIClientのモック
        reaction_handler.openai_client.get_response = AsyncMock(return_value="良い 面白い")

        ### When
        await reaction_handler.fetch_reaction(message_id, message_content)

        ### Then
        assert message_id in reaction_handler.reactions
        assert len(reaction_handler.reactions[message_id]) > 0
        assert "👍" in reaction_handler.reactions[message_id]  # "良い"に対応する絵文字
        assert "😂" in reaction_handler.reactions[message_id]  # "面白い"に対応する絵文字

    @pytest.mark.asyncio
    async def test_fetch_reaction_already_fetching(self, reaction_handler):
        """既に取得中のメッセージIDに対するテスト"""
        ### Given
        message_id = "123456789"
        message_content = "テストメッセージ"
        reaction_handler.fetching_message_ids.append(message_id)

        ### When
        await reaction_handler.fetch_reaction(message_id, message_content)

        ### Then
        assert message_id not in reaction_handler.reactions

    def test_get_reactions(self, reaction_handler):
        """保存されたリアクションの取得テスト"""
        ### Given
        message_id = "123456789"
        test_reactions = ["👍", "❤️"]
        reaction_handler.reactions[message_id] = test_reactions

        ### When
        result = reaction_handler.get_reactions(message_id)

        ### Then
        assert result == test_reactions

    def test_get_reactions_not_found(self, reaction_handler):
        """存在しないメッセージIDのリアクション取得テスト"""
        ### Given
        message_id = "nonexistent"

        ### When
        result = reaction_handler.get_reactions(message_id)

        ### Then
        assert result == []

    def test_generate_reactions(self, reaction_handler):
        """ジャンルレスポンスからのリアクション生成テスト"""
        ### Given
        genre_response = "良い 面白い 悲しい"

        ### When
        reactions = reaction_handler._generate_reactions(genre_response)

        ### Then
        assert "👀" in reactions  # デフォルトリアクション
        assert "👍" in reactions  # "良い"
        assert "😂" in reactions  # "面白い"
        assert "😢" in reactions  # "悲しい"

    def test_generate_reactions_with_error(self, reaction_handler):
        """リアクション生成時のエラー処理テスト"""
        ### Given
        genre_response = None  # エラーを発生させる入力

        ### When
        reactions = reaction_handler._generate_reactions(genre_response)

        ### Then
        assert reactions == ["👀"]  # エラー時はデフォルトリアクションのみ

    @pytest.mark.asyncio
    async def test_remove_old_reactions(self, reaction_handler):
        """古いリアクションの削除テスト"""
        ### Given
        message_id = "123456789"
        reaction_handler.reactions[message_id] = ["👍"]

        ### When
        await reaction_handler._remove_old_reactions(message_id, timeout=0.1)

        ### Then
        assert message_id not in reaction_handler.reactions 