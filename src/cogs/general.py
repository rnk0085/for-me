import discord
import platform
from discord.ext import commands
from discord import app_commands
from discord.ext.commands import Context

class General(commands.Cog, name="general"):
    """Taskuma の基本コマンドを定義"""

    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="ping", description="Taskumaが応答するか確認する")
    async def ping(self, context: Context) -> None:
        """Botの応答を確認"""
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"The bot latency is {round(self.bot.latency * 1000)}ms.",
            color=0xBEBEFE,
        )
        await context.send(embed=embed)

    @commands.hybrid_command(name="botinfo", description="Botの情報を取得")
    async def botinfo(self, context: Context) -> None:
        """Bot に関する情報を表示"""
        embed = discord.Embed(
            description="Taskuma - A Task Management Bot",
            color=0xBEBEFE,
        )
        embed.set_author(name="Bot Information")
        embed.add_field(name="Python Version:", value=f"{platform.python_version()}", inline=True)
        embed.add_field(name="Prefix:", value="/ (Slash Commands) or !", inline=False)
        embed.set_footer(text=f"Requested by {context.author}")
        await context.send(embed=embed)

    @commands.hybrid_command(name="list_commands", description="登録済みのコマンドを確認")
    async def list_commands(self, context: Context) -> None:
        """Bot に登録されているコマンドを一覧表示"""
        commands_list = [cmd.name for cmd in self.bot.commands]
        await context.send(f"登録されているコマンド: {commands_list}")

async def setup(bot) -> None:
    """Cog を Bot に追加"""
    await bot.add_cog(General(bot))
