import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, Mock
from discord.ext import commands
from src.cogs.task_commands import TaskCommands

class TestTaskCommands:
    @pytest_asyncio.fixture
    async def cog(self):
        """テスト用のセットアップ"""
        # Botのモックを作成
        self.bot = Mock()
        self.bot.user = Mock()
        self.bot.user.mention = "<@bot>"

        # Contextのモックを作成
        self.ctx = AsyncMock()
        self.ctx.send = AsyncMock()
        self.ctx.author = Mock()
        self.ctx.author.mention = "<@user>"

        # Cogを作成して返す
        cog = TaskCommands(self.bot)
        return cog

    @pytest.mark.asyncio
    async def test_task_command_success(self, cog):
        """タスクコマンドが正常に動作することを確認"""

        # When: taskコマンドを実行
        await cog.task.callback(cog, self.ctx)  # .callbackを使用して直接呼び出し

        # Then: 期待する応答が送信されたことを確認
        self.ctx.send.assert_called_once()
        assert "作業を決定します！" in str(self.ctx.send.call_args[0][0])

    @pytest.mark.asyncio
    async def test_task_command_error(self, cog):
        """エラー時の処理が正しく動作することを確認"""
        # Given: エラーを発生させる状況を設定
        self.ctx.send.side_effect = Exception("テストエラー")

        # When & Then: エラーが発生することを確認
        with pytest.raises(Exception):
            await cog.task.callback(cog, self.ctx)  # .callbackを使用して直接呼び出し
