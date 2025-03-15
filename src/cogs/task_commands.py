import discord
from discord.ext import commands
from discord.ext.commands import Context

class TaskCommands(commands.Cog):
    """タスク関連のスラッシュコマンドを管理"""

    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="task", description="作業を決定します！")
    async def task(self, context: Context) -> None:
        """作業を決定するコマンド"""
        try:
            # ここではまだスプレッドシートは使わない
            await context.send("作業を決定します！")
        except Exception as e:
            await context.send(f"⚠️ エラーが発生しました: {str(e)}")
    
async def setup(bot):
    """Cog を Bot に追加"""
    await bot.add_cog(TaskCommands(bot))
