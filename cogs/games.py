import discord
from discord import Interaction, SelectOption
from discord import ui
from discord.ext import commands


class GameSelect(ui.Select):
    def __init__(self, disabled=False, selected=None):
        self.game_dict = {
            'slide': ("슬라이딩 퍼즐", "(준비중)"),
            'ttt': ("틱택토", "(준비중)"),
            'sans': ("샌즈전", None),
        }
        options = [SelectOption(value=k, label=v[0], description=v[1])
                   for k, v in self.game_dict.items()]
        placeholder = selected or "플레이할 게임 선택하기"
        super().__init__(placeholder=placeholder,
                         options=options, disabled=disabled)

    async def callback(self, interaction: Interaction):
        selected = self.values[0]
        selected_label = self.game_dict[selected][0]
        await interaction.response.edit_message(
            content=f"그럼, 선택한 게임 __**{selected_label}**__을 시작할게!",
            view=GameSelectView(disabled=True, selected=selected_label)
        )

        match selected:
            case 'slide': link = 'https://www.artbylogic.com/puzzles/numSlider/numberShuffle.htm'
            case 'ttt': link = 'https://playtictactoe.org/'
            case 'sans': link = 'https://jcw87.github.io/c2-sans-fight/'
            case _: link = None
        await interaction.followup.send(
            "안만들었어 걍 여기서 하셈\n" + link)


class GameSelectView(ui.View):
    def __init__(self, disabled=False, selected=None):
        super().__init__()
        self.add_item(GameSelect(disabled, selected))


class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command("게임", aliases=["게임목록"])
    async def game_select(self, ctx: commands.Context):
        """게임 선택 메뉴를 출력해 줄게!"""
        view = GameSelectView()
        await ctx.send("목록에서 플레이하고 싶은 게임을 골라줘!", view=view)


def setup(bot):
    bot.add_cog(Games(bot))
