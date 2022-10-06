from asyncio.windows_events import NULL
import csv
from email import message
from types import NoneType
import discord
import random
from discord.ext import commands
from datetime import datetime, timedelta
from datetime import date
from BirthdayBot.Cogs.UserAgeInfo import UserAgeInfo
from BirthdayBot.Utils import session_scope, logger
from sqlalchemy import extract
from BirthdayBot.Models import CelebrityBirthdays, DiscordUser
from BirthdayBot.Models import BirthdayImages
from BirthdayBot.Models import BirthdayMessages
from BirthdayBot.Birthday import Birthday


class BirthdayChecker(object):
    """Handles the checking of birthdays for the day"""

    def __init__(self, bot):
        self.bot = bot

    @classmethod
    def getAllBirthdays(cls, guild) -> list:
        with session_scope() as session:
            all_birthdays = (
                session.query(DiscordUser)
                .filter(
                    extract("month", DiscordUser.Birthday) == datetime.today().month,
                    extract("day", DiscordUser.Birthday) == datetime.today().day,
                    DiscordUser.guild == guild.id,
                )
                .all()
            )
            session.expunge_all()

        return all_birthdays

    @classmethod
    def getAllFutureBirthdays(cls, guild) -> list:
        tomorrowDate = datetime.now() + timedelta(days=1)
        with session_scope() as session:
            all_birthdays = (
                session.query(DiscordUser)
                .filter(
                    extract("month", DiscordUser.Birthday) == tomorrowDate.month,
                    extract("day", DiscordUser.Birthday) == tomorrowDate.day,
                    DiscordUser.guild == guild.id,
                )
                .all()
            )
            session.expunge_all()

        return all_birthdays

    @classmethod
    def getAllMonthBirthdays(cls, guild) -> list:
        with session_scope() as session:
            all_birthdays = (
                session.query(DiscordUser)
                .filter(
                    extract("month", DiscordUser.Birthday) == datetime.today().month,
                    DiscordUser.guild == guild.id,
                )
                .all()
            )
            session.expunge_all()

        return all_birthdays

    @classmethod
    def getAllCelebBirthdays(cls) -> list:
        with session_scope() as session:
            all_birthdays = (
                session.query(CelebrityBirthdays)
                .filter(
                    extract("month", CelebrityBirthdays.celebBirthdate)
                    == datetime.today().month,
                    extract("day", CelebrityBirthdays.celebBirthdate)
                    == datetime.today().day,
                )
                .all()
            )
            session.expunge_all()

        return all_birthdays

    @classmethod
    def getFutureCelebBirthdays(cls) -> list:
        tomorrowDate = datetime.now() + timedelta(days=1)
        with session_scope() as session:
            all_birthdays = (
                session.query(CelebrityBirthdays)
                .filter(
                    extract("month", CelebrityBirthdays.celebBirthdate)
                    == tomorrowDate.month,
                    extract("day", CelebrityBirthdays.celebBirthdate)
                    == tomorrowDate.day,
                )
                .all()
            )
            session.expunge_all()

        return all_birthdays

    @classmethod
    def getCelebMonthBirthdays(cls) -> list:
        with session_scope() as session:
            all_birthdays = (
                session.query(CelebrityBirthdays)
                .filter(
                    extract("month", CelebrityBirthdays.celebBirthdate)
                    == datetime.today().month,
                )
                .all()
            )
            session.expunge_all()

        return all_birthdays

    async def sendBirthdayMessages(self, todays_birthdays: list, channel) -> None:
        todays_birthdays = DiscordUser.getAll(_birthday=Birthday(datetime.today()))
        for birthday in todays_birthdays:
            random_msg_details = self.generateRandomMessage()
            embed = discord.Embed(
                title="Happy Birthday!",
                description=f"<@{birthday.discord_id}>",
                color=discord.Color.red(),
            )
            embed.add_field(
                name="Quote:",
                value=random_msg_details["message"]
                + "\n ~ 🤵"
                + random_msg_details["author"],
                inline=False,
            )
            embed.set_image(url=random_msg_details["birthdayImage"])
            await channel.send(embed=embed)
            logger.info(
                "Sending Birthday Announcement: Username: {} -  Quote ID: {} - Author: {} - Image ID: {}".format(
                    birthday.username,
                    random_msg_details["message_id"],
                    random_msg_details["author"],
                    random_msg_details["birthdayImage_id"],
                )
            )

    def generateRandomMessage(self) -> dict:
        with session_scope() as session:
            birthdayMessage = random.choice(session.query(BirthdayMessages).all())
            birthdayImage = random.choice(session.query(BirthdayImages).all())

            bdayMessage = {
                "message": birthdayMessage.bdayMessage,
                "author": birthdayMessage.author,
                "birthdayImage": birthdayImage.bdayImage,
                "message_id": birthdayMessage.id,
                "birthdayImage_id": birthdayImage.id,
            }

            return bdayMessage


class BirthdayCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="today",
        description="Displays everyone with birthdays for the day.",
    )
    async def today(self, ctx):
        guildId = ctx.message.guild
        todayBdays = DiscordUser.getAll(guild=guildId)
        month = datetime.today().month
        day = datetime.today().day
        numBdays = 1
        embed = discord.Embed(
            title=f"Todays Birthday's - {month}/{day}",
            description="List of people with birthdays today:",
            color=discord.Color.red(),
        )
        await ctx.send(embed=embed)
        for birthdays in todayBdays:
            userAge = UserAgeInfo.getUserAge(birthdays.Birthday)
            user = await ctx.guild.query_members(user_ids=[int(birthdays.discord_ID)])
            user = user[0]
            embed2 = discord.Embed(
                title=f"{birthdays.username}",
                description=f"is {userAge} today!",
                color=discord.Color.red(),
            )
            embed2.set_image(url=user.avatar.url)
            embed2.set_footer(text=f"{numBdays}/{len(todayBdays)}")
            numBdays += 1
            await ctx.send(embed=embed2)

    @commands.hybrid_command(
        name="todayceleb",
        description="Displays a random celebrity with a birthday today.",
    )
    async def todayceleb(self, ctx):
        todayBdays = BirthdayChecker.getAllCelebBirthdays()
        randomBday = random.choice(todayBdays)
        month = datetime.today().month
        day = datetime.today().day
        embed = discord.Embed(
            title=f"Celebrity Birthday - {month}/{day}",
            description="A random Celebrity with a birthday today: ",
            color=discord.Color.red(),
        )
        celebAge = randomBday.celebAge
        celebName = randomBday.celebName
        embed.add_field(name=f"{celebName}", value=f"Age: {celebAge}", inline=True)
        await ctx.send(embed=embed)

    @commands.hybrid_command(
        name="tomorrow",
        description="Displays users birthdays for tomorrow.",
    )
    async def tomorrow(self, ctx):
        guildId = ctx.message.guild
        tomorrowBdays = BirthdayChecker.getAllFutureBirthdays(guildId)
        month = datetime.today().month
        day = datetime.today().day
        numBdays = 1
        embed = discord.Embed(
            title=f"Tomorrows Birthday's - {month}/{day+1}",
            description="List of people with birthdays tomorrow:",
            color=discord.Color.red(),
        )
        await ctx.send(embed=embed)
        for birthdays in tomorrowBdays:
            userAge = UserAgeInfo.getUserAge(birthdays.Birthday)
            user = await ctx.guild.query_members(user_ids=[int(birthdays.discord_ID)])
            user = user[0]
            embed2 = discord.Embed(
                title=f"{birthdays.username}",
                description=f"is {userAge} today!",
                color=discord.Color.red(),
            )
            embed2.set_image(url=user.avatar.url)
            embed2.set_footer(text=f"{numBdays}/{len(tomorrowBdays)}")
            numBdays += 1
            await ctx.send(embed=embed2)

    @commands.hybrid_command(
        name="tomorrowceleb",
        description="Displays a random celebrity with a birthday tomorrow.",
    )
    async def tomorrowceleb(self, ctx):
        tomorrowBdays = BirthdayChecker.getFutureCelebBirthdays()
        randomBday = random.choice(tomorrowBdays)
        month = datetime.today().month
        day = datetime.today().day
        embed = discord.Embed(
            title=f"Celebrity Birthday That's Tomorrow - {month}/{day+1}",
            description="A random Celebrity with a birthday tomorrow: ",
            color=discord.Color.red(),
        )
        celebAge = randomBday.celebAge
        celebName = randomBday.celebName
        embed.add_field(name=f"{celebName}", value=f"Age: {celebAge}", inline=True)
        await ctx.send(embed=embed)

    @commands.hybrid_command(
        name="month",
        description="Displays users birthdays for the month.",
    )
    async def month(self, ctx):
        guildId = ctx.message.guild
        monthBdays = BirthdayChecker.getAllMonthBirthdays(guildId)
        month = datetime.today().month
        month = datetime.strptime(str(month), "%m")
        month = month.strftime("%B")
        embed = discord.Embed(
            title=f"{month} Birthday's",
            description="List of people with birthdays this month:",
            color=discord.Color.red(),
        )
        for birthdays in monthBdays:
            embed.add_field(
                name=f"{birthdays.username}",
                value=f"Birthday: {birthdays.Birthday.month}/{birthdays.Birthday.day}",
                inline=False,
            )
        embed.set_footer(text=f"Total amount of birthdays: {len(monthBdays)}")
        await ctx.send(embed=embed)

    @commands.hybrid_command(
        name="monthceleb",
        description="Displays celebrity birthdays for the month.",
    )
    async def monthceleb(self, ctx):
        monthBdays = BirthdayChecker.getCelebMonthBirthdays()
        month = datetime.today().month
        month = datetime.strptime(str(month), "%m")
        month = month.strftime("%B")
        embed = discord.Embed(
            title=f"{month} Celebrity Birthday's",
            description="List of 5 random Celebrity's with birthdays this month:",
            color=discord.Color.red(),
        )
        for randomBday in range(1, 6):
            randomBday = random.choice(monthBdays)
            embed.add_field(
                name=f"{randomBday.celebName}",
                value=f"Birthday: {randomBday.celebBirthdate.month}/{randomBday.celebBirthdate.day}",
                inline=False,
            )
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(BirthdayCommands(bot))