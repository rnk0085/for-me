import pytest
from unittest.mock import AsyncMock, Mock, patch
from src.services.discord_message_handler import DiscordMessageHandler

class TestDiscordMessageHandler:
    @pytest.fixture
    def message_handler(self, mock_bot, mock_reaction_manager, mock_openai_client, mock_config_service):
        with patch('src.services.discord_message_handler.get_prompt', return_value="テスト用プロンプト"):
            return DiscordMessageHandler(
                bot=mock_bot,
                reactions=mock_reaction_manager,
                openai_client=mock_openai_client,
                config_service=mock_config_service
            )

    @pytest.fixture
    def mock_message(self):
        message = Mock()
        message.content = "テストメッセージ"
        message.id = "123456789"
        message.channel = Mock()
        message.channel.name = "general"
        message.channel.id = "123456789"
        message.author = Mock()
        message.author.bot = False
        message.add_reaction = AsyncMock()
        message.channel.send = AsyncMock()
        return message

    @pytest.mark.asyncio
    async def test_process_reactions_for_normal_message(self, message_handler, mock_message, mock_reaction_manager):
        """通常のメッセージに対するリアクション処理のテスト"""
        # Given
        message_handler._should_add_reaction = Mock(return_value=True)
        mock_reaction_manager.get_reactions.return_value = ["👍", "❤️"]
        mock_message.author.bot = False
        message_handler._should_react_randomly = Mock(return_value=True)

        ### When
        await message_handler.process_reactions(mock_message)

        ### Then
        mock_reaction_manager.fetch_reaction.assert_called_once_with(
            message_id=mock_message.id,
            message_content=mock_message.content
        )
        assert mock_message.add_reaction.call_count == 2
        mock_message.add_reaction.assert_any_call("👍")
        mock_message.add_reaction.assert_any_call("❤️")

    @pytest.mark.asyncio
    async def test_process_reactions_for_bot_message(self, message_handler, mock_message):
        """Botのメッセージに対するリアクション処理のテスト"""
        ### Given
        mock_message.author.bot = True

        ### When
        await message_handler.process_reactions(mock_message)

        ### Then
        assert not mock_message.add_reaction.called

    @pytest.mark.asyncio
    async def test_process_auto_response_in_free_talk(self, message_handler, mock_message, mock_config_service):
        """フリートークチャンネルでの自動応答のテスト"""
        ### Given
        message_handler._should_auto_respond = Mock(return_value=True)
        expected_response = "AIからの応答"
        message_handler._generate_ai_response = AsyncMock(return_value=expected_response)

        ### When
        await message_handler.process_auto_response(mock_message)

        ### Then
        message_handler._should_auto_respond.assert_called_once_with(mock_message.channel.id, mock_message.author.bot)
        message_handler._generate_ai_response.assert_called_once_with(mock_message, mock_message.content)
        mock_message.channel.send.assert_called_once_with(expected_response)
    
    @pytest.mark.asyncio
    async def test_process_auto_response_in_free_talk_not_auto_respond(self, message_handler, mock_message):
        """フリートークチャンネルでの自動応答がFalseの場合のテスト"""
        ### Given
        message_handler._should_auto_respond = Mock(return_value=False)

        ### When
        await message_handler.process_auto_response(mock_message)

        ### Then
        assert not mock_message.channel.send.called

    @pytest.mark.asyncio
    async def test_process_mentions(self, message_handler, mock_message, mock_discord_client):
        """メンション付きメッセージの処理テスト"""
        ### Given
        mock_message.content = "<@123456789> こんにちは"
        mock_discord_client.user.mentioned_in.return_value = True
        expected_response = "メンションへの応答"
        message_handler.openai_client.get_response = AsyncMock(return_value=expected_response)

        ### When
        await message_handler.process_mentions(mock_message, mock_discord_client)

        ### Then
        mock_message.channel.send.assert_called_once_with(expected_response)

    def test_should_add_reaction_normal_channel(self, message_handler, mock_message, mock_config_service):
        """通常チャンネルでのリアクション追加判定のテスト"""
        ### Given
        mock_message.channel.name = "general"
        mock_message.content = "テストメッセージ"
        mock_message.channel.id = 123456789
        mock_config_service.get_channel_id.return_value = 999

        ### When
        result = message_handler._should_add_reaction(mock_message)

        ### Then
        assert result is True

    def test_should_add_reaction_message_is_empty(self, message_handler, mock_message):
        """メッセージが空の場合のリアクション追加判定のテスト"""
        ### Given
        mock_message.content = ""

        ### When
        result = message_handler._should_add_reaction(mock_message)

        ### Then
        assert result is False

    def test_should_add_reaction_times_channel(self, message_handler, mock_message):
        """timesチャンネルでのリアクション追加判定のテスト"""
        ### Given
        mock_message.channel.name = "times-mbti-name"

        ### When
        result = message_handler._should_add_reaction(mock_message)

        ### Then
        assert result is False
    
    def test_should_add_reaction_dev_channel(self, message_handler, mock_message, mock_config_service):
        """DEVチャンネルでのリアクション追加判定のテスト"""
        ### Given
        mock_message.channel.id = 123456789
        mock_config_service.get_channel_id.return_value = 123456789

        ### When
        result = message_handler._should_add_reaction(mock_message)

        ### Then
        assert result is False

    @pytest.mark.parametrize("channel_type,is_bot,expected", [
        ("FREE_TALK", False, True),   # 一般ユーザー、フリートーク
        ("FB", False, True),          # 一般ユーザー、FB
        ("PRAISE", False, True),      # 一般ユーザー、ほめる
        ("FREE_TALK", True, True),    # Bot、フリートーク
        ("FB", True, False),          # Bot、FB
        ("PRAISE", True, False),      # Bot、ほめる
        ("OTHER", False, False),      # その他チャンネル
    ])
    def test_should_auto_respond(self, message_handler, mock_config_service, channel_type, is_bot, expected):
        """自動応答判定のテスト"""
        ### Given
        free_talk_channel_id = 123
        fb_channel_id = 456
        praise_channel_id = 789

        mock_config_service.get_channel_id.side_effect = [
            free_talk_channel_id,
            fb_channel_id,
            praise_channel_id
        ]

        mock_config_service.get_auto_reply_in_free_talk_rate.return_value = 1.0
        mock_config_service.get_auto_reply_rate.return_value = 1.0
        channel_id = 999
        if channel_type == "FREE_TALK":
            channel_id = free_talk_channel_id
        elif channel_type == "FB":
            channel_id = fb_channel_id
        elif channel_type == "PRAISE":
            channel_id = praise_channel_id
        mock_config_service.get_channel_id.return_value = channel_id

        ### When
        result = message_handler._should_auto_respond(channel_id, is_bot)

        ### Then
        assert mock_config_service.get_channel_id.call_count == 3
        assert result == expected

    def test_remove_mentions(self, message_handler):
        """メンション除去のテスト"""
        ### Given
        test_cases = [
            ("<@123456789> こんにちは", "こんにちは"),
            ("<@&987654321> テスト", "テスト"),
            ("<@!123456789> テスト", "テスト"),
            ("通常のメッセージ", "通常のメッセージ"),
            ("<@123> <@456> 複数メンション", "複数メンション"),
        ]

        for input_text, expected in test_cases:
            ### When
            result = message_handler._remove_mentions(input_text)

            ### Then
            assert result == expected
    
    @pytest.mark.parametrize("channel_id,expected", [
        ("123456789", "あなたが興味関心のある話題をテーマに雑談してください。"),
        ("456789012", "フィードバックをしてください。また、"),
        ("789012345", "全力で褒めてください。また、"),
    ])
    def test_get_prompt(self, message_handler, mock_config_service, channel_id, expected):
        """プロンプト取得のテスト"""
        ### Given
        mock_config_service.get_channel_id.side_effect = lambda x: {
            "FREE_TALK": "123456789",
            "FB": "456789012",
            "PRAISE": "789012345"
        }.get(x, None)  # 引数に対応する値を返し、それ以外は None を返す
        get_prompt_patcher = patch('src.services.discord_message_handler.get_prompt', return_value="テスト用プロンプト")

        ### When
        with get_prompt_patcher:
            result = message_handler._get_prompt(channel_id)

        ### Then
        assert result == expected + "テスト用プロンプト"
