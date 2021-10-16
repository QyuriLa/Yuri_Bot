import discord
from discord import ButtonStyle


class ConfirmView(discord.ui.View):
    def __init__(self, ctx, timeout=300):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.value = None
        self.user = self.ctx.author

    @discord.ui.button(label='확인', style=ButtonStyle.primary)
    async def okay(self, b, i):
        self.value = True
        self.stop()

    @discord.ui.button(label='취소', style=ButtonStyle.secondary)
    async def cancel(self, b, i):
        self.value = False
        self.stop()

    async def interaction_check(self, interaction):
        if interaction.user != self.user:
            return await interaction.response.send_message(
                '명령어를 입력한 본인만 누를 수 있어!', ephemeral=True
            )
        return True
