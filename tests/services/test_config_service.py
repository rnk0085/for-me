import pytest
from unittest.mock import Mock, patch
from src.services.config_service import ConfigService
import os

class TestConfigService:
    @pytest.fixture
    def config_service(self):
        # 既存の環境変数をバックアップ
        original_env = dict(os.environ)
        
        # テスト用の環境変数を設定
        test_env = {
            'DISCORD_TEST_TOKEN': 'test-token',
            'FREE_TALK_CHANNEL_ID': '123456789',
            'FB_CHANNEL_ID': '987654321',
            'PRAISE_CHANNEL_ID': '456789123',
            'DEV_CHANNEL_ID': '321654987',
            'REACTION_RATE': '0.5',
            'AUTO_REPLY_RATE': '0.2',
            'AUTO_REPLY_IN_FREE_TALK_RATE': '0.1',
            'OPENAI_API_KEY': 'test-api-key',
            'GUILD_ID': '1472583690',
        }
        os.environ.clear()
        os.environ.update(test_env)

        # ConfigServiceのインスタンスを作成
        service = ConfigService()

        yield service

        # テスト後に環境変数を元に戻す
        os.environ.clear()
        os.environ.update(original_env)

    def test_get_discord_token(self, config_service):
        """Discordトークンの取得テスト"""
        assert config_service.get_discord_token('TEST') == 'test-token'

    def test_get_channel_id(self, config_service):
        """チャンネルIDの取得テスト"""
        assert config_service.get_channel_id('FREE_TALK') == 123456789
        assert config_service.get_channel_id('FB') == 987654321
        assert config_service.get_channel_id('PRAISE') == 456789123
        assert config_service.get_channel_id('DEV') == 321654987

    def test_get_reaction_rate(self, config_service):
        """リアクション確率の取得テスト"""
        assert config_service.get_reaction_rate() == 0.5

    def test_get_auto_reply_rate(self, config_service):
        """自動応答確率の取得テスト"""
        assert config_service.get_auto_reply_rate() == 0.2

    def test_get_auto_reply_in_free_talk_rate(self, config_service):
        """フリートークでの自動応答確率の取得テスト"""
        assert config_service.get_auto_reply_in_free_talk_rate() == 0.1

    def test_get_openai_api_key(self, config_service):
        """OpenAI APIキーの取得テスト"""
        assert config_service.get_openai_api_key() == 'test-api-key'

    def test_get_nonexistent_channel(self, config_service):
        """存在しないチャンネルIDの取得テスト"""
        assert config_service.get_channel_id('NONEXISTENT') == 0

    def test_get_guild_id(self, config_service):
        """サーバーIDの取得テスト"""
        assert config_service.get_guild_id() == 1472583690
