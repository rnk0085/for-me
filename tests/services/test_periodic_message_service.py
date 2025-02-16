import pytest
from unittest.mock import AsyncMock, Mock, patch
from src.services.periodic_message_service import PeriodicMessageService

class TestPeriodicMessageService:
    five_percent_rate = 9.498307102162595e-05
    ten_percent_rate = 0.00019509303291176394
    fifteen_percent_rate = 0.0003009156963386106
    twenty_percent_rate = 0.0004131434314691429

    @pytest.fixture
    def periodic_service(self, mock_bot, mock_openai_client, mock_config_service):
        return PeriodicMessageService(
            bot=mock_bot,
            openai_client=mock_openai_client,
            config_service=mock_config_service
        )

    @pytest.fixture
    def mock_channel(self):
        channel = Mock()
        channel.send = AsyncMock()
        return channel

    @pytest.mark.asyncio
    async def test_send_random_message_not_sent_when_should_send_message_false(self, periodic_service):
        """_should_send_message() が False の場合、メッセージを送信しない"""
        periodic_service._should_send_message = Mock(return_value=False)
        mock_client = Mock()
        await periodic_service.send_random_message(mock_client)

        mock_client.get_channel.assert_not_called()

    @pytest.mark.asyncio
    async def test_send_random_message_sent_to_correct_channel(self, periodic_service):
        """_should_send_message() が True の場合、適切なチャンネルにメッセージを送信する"""
        periodic_service._should_send_message = Mock(return_value=True)

        # チャンネルのモック
        mock_channel = AsyncMock()
        mock_client = Mock()
        mock_client.get_channel = Mock(return_value=mock_channel)

        # `_get_target_channel()` をモック化して、期待するチャンネルを返す
        periodic_service._get_target_channel = Mock(return_value=mock_channel)

        # `_generate_random_message()` をモック化して、固定メッセージを返す
        periodic_service._generate_random_message = AsyncMock(return_value="Test Message")

        await periodic_service.send_random_message(mock_client)

        # 適切なチャンネルで send() が呼ばれたことを確認
        mock_channel.send.assert_called_once_with("Test Message")
    
    def test_get_target_channel(self, periodic_service, mock_config_service):
        """_get_target_channel() が正しくチャンネルを取得するか"""
        mock_client = Mock()
        mock_client.get_channel = Mock(return_value="MockChannel")
        
        # `config_service.get_channel_id()` が `TIMES_ENTP` を返すようにする
        mock_config_service.get_channel_id = Mock(return_value="123456789")

        print(periodic_service)
        channel = periodic_service._get_target_channel(mock_client)
        
        # `get_channel` が適切な ID で呼ばれたか
        mock_client.get_channel.assert_called_once_with("123456789")
        assert channel == "MockChannel"

    @pytest.mark.asyncio
    async def test_generate_random_message(self, periodic_service, mock_openai_client):
        """_generate_random_message() が OpenAI から正しいレスポンスを受け取るか"""
        periodic_service.openai_client.get_response = Mock(return_value="AI Generated Message")

        result = await periodic_service._generate_random_message("Test Topic")

        # OpenAI API に正しいプロンプトでリクエストされているか
        periodic_service.openai_client.get_response.assert_called_once_with(
            prompt="",
            user_message="「Test Topic」をテーマに自由に雑談して"
        )

        assert result == "AI Generated Message"

    @patch("src.services.periodic_message_service.datetime.datetime")
    def test_should_send_message(self, mock_datetime, periodic_service):
        """_should_send_message() が時間帯に応じて正しく判定するか"""
        mock_datetime.now.return_value.hour = 10  # 10時のシミュレーション
        periodic_service._get_hourly_post_rate = Mock(return_value=0.2)  # 20% の確率で投稿

        with patch("src.services.periodic_message_service.random_true_with_probability") as mock_random:
            mock_random.return_value = True  # 確実に投稿するようにする
            assert periodic_service._should_send_message() is True

            mock_random.return_value = False  # 確実に投稿しないようにする
            assert periodic_service._should_send_message() is False
    
    @pytest.mark.parametrize("hour, expected_rate", [
        (0, 0.0), 
        (1, 0.0),
        (2, 0.0),
        (3, 0.0),
        (4, 0.0),
        (5, 0.0),
        (6, 0.0),
        (7, five_percent_rate),
        (8, five_percent_rate),
        (9, twenty_percent_rate),
        (10, twenty_percent_rate),
        (11, twenty_percent_rate),  
        (12, fifteen_percent_rate),
        (13, fifteen_percent_rate),
        (14, fifteen_percent_rate),
        (15, fifteen_percent_rate),
        (16, fifteen_percent_rate),
        (17, ten_percent_rate),
        (18, ten_percent_rate),
        (19, ten_percent_rate),
        (20, five_percent_rate),
        (21, five_percent_rate),
        (22, five_percent_rate),
        (23, five_percent_rate),
    ])
    def test_get_hourly_post_rate(self, periodic_service, hour, expected_rate):
        """_get_hourly_post_rate() の時間帯ごとの確率が正しいか"""
        assert periodic_service._get_hourly_post_rate(hour) == expected_rate
    
    @pytest.mark.parametrize("percent, expected_value", [
        (5, five_percent_rate),
        (10, ten_percent_rate),
        (15, fifteen_percent_rate),
        (20, twenty_percent_rate),
    ])
    def test_get_rate_for_all_characters(self, periodic_service, percent, expected_value):
        """_get_rate_for_all_characters() の計算が正しいか"""
        assert periodic_service._get_rate_for_all_characters(percent) == expected_value

    @pytest.mark.asyncio
    async def test_send_random_message(self, periodic_service, mock_discord_client, mock_channel):
        """send_random_message() メソッドが正しく呼び出されるか"""
        periodic_service._should_send_message = Mock(return_value=True)
        mock_discord_client.get_channel.return_value = mock_channel
        await periodic_service.send_random_message(mock_discord_client)
        assert mock_channel.send.called
        assert periodic_service.openai_client.get_response.called
