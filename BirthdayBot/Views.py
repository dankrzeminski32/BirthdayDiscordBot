import discord
from BirthdayBot.Models import DiscordUser
from BirthdayBot.Cogs.UserAgeInfo import daysAway

class BaseView(discord.ui.View):
    def __init__(self, *, timeout=180, author: discord.User):
        super().__init__(timeout=timeout)
        self.author = author
        
    async def interaction_check(self, inter: discord.MessageInteraction) -> bool:
        if inter.user != self.author:
            await inter.response.send_message(
                content="You don't have permission to press this button.",
                ephemeral=True,
            )
            return False
        return True



class RegistrationButtons(BaseView):
    def __init__(self):
        super().__init__()
        self.userConfirmation = None

    @discord.ui.button(label="Yes! 👍", style=discord.ButtonStyle.green)  # or .success
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "Confirming..."
        )  # Ephermal = True if we only want user to see, tbd
        self.userConfirmation = True
        self.stop()

    @discord.ui.button(label="No! 👎", style=discord.ButtonStyle.red)  # or .danger
    async def no(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Please try again... (mm/dd/yyyy)")
        self.userConfirmation = False
        self.stop()



class ExistingUserButtons(discord.ui.View):
    def __init__(self, existing_user: DiscordUser):
        super().__init__()
        self.userConfirmation = None
        self.existing_user_bday = existing_user.Birthday

    @discord.ui.button(label="Yes!", style=discord.ButtonStyle.green)  # or .success
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "Please Provide a new Birthday...(mm/dd/yyyy)"
        )  # Ephermal = True if we only want user to see, tbd
        self.userConfirmation = True
        self.stop()

    @discord.ui.button(label="No!", style=discord.ButtonStyle.red)  # or .danger
    async def no(self, interaction: discord.Interaction, button: discord.ui.Button):
        days_away = daysAway(birthdate=self.existing_user_bday)
        await interaction.response.send_message(
            "Sounds good! Only {} Days from your birthday!".format(daysAway)
        )
        self.userConfirmation = False
        self.stop()