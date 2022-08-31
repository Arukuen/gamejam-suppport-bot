from datetime import datetime
from discord.ext import tasks
import discord

class Reminder:
    def __init__(self) -> None:
        self.title: str = None
        self.date: datetime = None
        self.message: str = None
        self.channel: discord.TextChannel = None
        self.ping: discord.Role = None
        self.callback = None

    def set_and_start(self, title: str, date: datetime, message: str, channel: discord.TextChannel, ping: discord.Role, callback):
        # If initially empty or the new date is closer than current, replace the current and rerun the loop
        self.title = title
        self.date = date
        self.message = message
        self.channel = channel
        self.ping = ping
        self.callback = callback
        if not self.task.is_running():
            self.task.start()
        else:
            self.task.restart()


    @tasks.loop(seconds=2)
    async def task(self):
        if datetime.now() >= self.date:
            print('Reminder done')
            await self.channel.send(f'{self.ping.mention}\n{self.message}')
            self.task.stop()
            self.callback()