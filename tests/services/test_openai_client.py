import pytest
from unittest.mock import AsyncMock, Mock, patch
from src.services.openai_client import OpenAIClient

class TestOpenAIClient:
    @pytest.fixture
    def openai_client(self, mock_config_service):
        with patch('src.services.openai_client.OpenAI') as mock_openai:
            client = OpenAIClient(mock_config_service)
            return client

    @pytest.mark.asyncio
    async def test_get_response(self, openai_client):
        """OpenAIからの応答取得テスト"""
        ### Given
        test_prompt = "テストプロンプト"
        test_message = "こんにちは"
        expected_response = "AIからの応答"
        
        # openAiClientプロパティを使用
        openai_client.openAiClient.chat.completions.create = AsyncMock(return_value=Mock(
            choices=[Mock(message=Mock(content=expected_response))]
        ))

        ### When
        response = await openai_client.get_response(test_prompt, test_message)

        ### Then
        assert response == expected_response
        openai_client.openAiClient.chat.completions.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_response_with_error(self, openai_client):
        """エラー発生時のテスト"""
        ### Given
        openai_client.openAiClient.chat.completions.create = AsyncMock(
            side_effect=Exception("API Error")
        )

        ### When
        response = await openai_client.get_response("プロンプト", "メッセージ")

        ### Then
        assert response == "OpenAIでエラーが起きました"