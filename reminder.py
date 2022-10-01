from datetime import datetime
from discord.ext import tasks
import discord

class Reminder:
    def __init__(self) -> None:
        self.title: str = None
        self.date: datetime = None
        self.message: str = None
        self.channel: discord.TextChannel = None
        self.callback = None

    def insert_and_run(self, title: str, new_date: datetime, message: str, channel: discord.TextChannel, callback):
        self.title = title
        self.date = new_date
        self.message = message
        self.channel = channel
        self.callback = callback
        if not self.task.is_running():
            self.task.start()
        else:
            self.task.restart()
        
    def set_and_start(self, title: str, new_date: datetime, message: str, channel: discord.TextChannel, callback):
        # If initially empty or the new date is closer than current, replace the current and rerun the loop
        # If the new date is already done
        # Will remove just for debugging
        if new_date < datetime.now():
            print('cp 1')
            return
        # If no currently running
        if self.date == None:
            self.insert_and_run(title, new_date, message, channel, callback)
            print('cp 2')
            return
        # If new date is closer than currently running’s date
        if new_date > self.date:
            print('cp 3')
            return
        self.insert_and_run(title, new_date, message, channel, callback)
        print('cp 4')
        

    @tasks.loop(seconds=5)
    async def task(self):
        print(self.date - datetime.now())
        if datetime.now() >= self.date:
            print('Reminder done')
            await self.channel.send(f'{self.message}', allowed_mentions=discord.AllowedMentions(everyone=True))
            self.task.stop()
            # Resetting
            self.date = None
            self.callback()