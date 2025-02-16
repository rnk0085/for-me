import pytest
from unittest.mock import AsyncMock, Mock, patch
from src.services.discord_bot_manager import DiscordBotManager
from src.services.discord_message_handler import DiscordMessageHandler
from src.services.periodic_message_service import PeriodicMessageService

@pytest.mark.asyncio
class TestDiscordBotManager:
    @pytest.fixture
    def message_handler(self):
        handler = Mock(spec=DiscordMessageHandler)
        handler.process_reactions = AsyncMock()
        handler.process_auto_response = AsyncMock()
        handler.process_mentions = AsyncMock()
        return handler

    @pytest.fixture
    def periodic_service(self):
        service = Mock(spec=PeriodicMessageService)
        service.send_random_message = AsyncMock()
        return service

    @pytest.fixture
    def bot_manager(self, mock_bot, mock_discord_client, message_handler, periodic_service):
        return DiscordBotManager(
            bot=mock_bot,
            discord_client=mock_discord_client,
            message_handler=message_handler,
            periodic_message_service=periodic_service,
        )
    
    async def test_on_ready_event(self, bot_manager):
        """on_ready イベントが発生したときに、正しく `schedule_periodic_messages.start()` が呼ばれるか"""
        with patch.object(bot_manager.schedule_periodic_messages, 'start') as mock_start:
            bot_manager.initialize_event_handlers()

            # `on_ready` を実行
            on_ready = bot_manager.client.event.call_args_list[0][0][0]
            await on_ready()

            #  `schedule_periodic_messages.start()` が実行されたかチェック
            mock_start.assert_called_once()

    async def test_on_message_event(self, bot_manager):
        """on_message イベントが発生したときに、すべてのメッセージ処理が実行されるか"""
        bot_manager.initialize_event_handlers()

        # `on_message` の取得
        on_message = bot_manager.client.event.call_args_list[1][0][0]
        
        # モックのメッセージを作成
        mock_message = Mock()
        mock_message.author = Mock()
        mock_message.author.bot = False  # Botのメッセージではない
        
        await on_message(mock_message)

        # すべてのメッセージ処理が呼ばれたかチェック
        bot_manager.message_handler.process_reactions.assert_called_once_with(mock_message)
        bot_manager.message_handler.process_auto_response.assert_called_once_with(mock_message)
        bot_manager.message_handler.process_mentions.assert_called_once_with(mock_message, bot_manager.client)

    async def test_on_message_ignores_own_bot(self, bot_manager):
        """on_message イベントが発生したときに、Bot 自身のメッセージは無視されるか"""
        bot_manager.initialize_event_handlers()

        on_message = bot_manager.client.event.call_args_list[1][0][0]

        # モックのメッセージ（Bot自身）
        mock_message = Mock()
        mock_message.author = bot_manager.client.user  # Bot自身が送信

        await on_message(mock_message)

        # Bot自身のメッセージなので、メッセージ処理が一切呼ばれないか確認
        bot_manager.message_handler.process_reactions.assert_not_called()
        bot_manager.message_handler.process_auto_response.assert_not_called()
        bot_manager.message_handler.process_mentions.assert_not_called()

    async def test_schedule_periodic_messages(self, bot_manager):
        """schedule_periodic_messages() メソッドが正しく呼び出されるか"""
        await bot_manager.schedule_periodic_messages()
        assert bot_manager.periodic_message_service.send_random_message.called

    async def test_start_bot(self, bot_manager):
        """start() メソッドが正しく呼び出されるか"""
        with patch.object(bot_manager, "initialize_event_handlers") as mock_initialize:
            await bot_manager.start()

            # `initialize_event_handlers()` が1回呼ばれたことを確認
            mock_initialize.assert_called_once()
        bot_manager.client.start.assert_called_once_with(bot_manager.token) 
    
    async def test_schedule_periodic_messages_handles_errors(self, bot_manager):
        """schedule_periodic_messages() でエラーが発生してもクラッシュしないか"""
        # `send_random_message()` をエラーを出すようにする
        bot_manager.periodic_message_service.send_random_message = AsyncMock(side_effect=Exception("Test error"))

        with patch("builtins.print") as mock_print:
            await bot_manager.schedule_periodic_messages()

            # エラーメッセージが出力されているか確認
            mock_print.assert_called_with("定期メッセージ送信中にエラーが発生しました: Test error")
