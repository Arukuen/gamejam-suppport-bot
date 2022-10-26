from datetime import datetime
from email.mime import image
from discord.ext import tasks
import discord

class Reminder:
    def __init__(self) -> None:
        self.title: str = None
        self.date: datetime = None
        self.message: str = None
        self.channel: discord.TextChannel = None
        self.image: discord.Embed = None
        self.callback = None

        
    def set_and_start(self, title: str, new_date: datetime, message: str, channel: discord.TextChannel, image: discord.Embed, callback):
        # Will delete printing checkpoint (for debug only)
        # If the new date is already done compared to current real time
        if new_date < datetime.now():
            print('cp 1')
            return
        # If there's currently running
        if self.date != None:
            print('cp 2')
            # If new date is farther than currently running’s date
            if new_date > self.date:
                print('cp 3')
                return
        print('cp 4')
        
        # Set
        self.title = title
        self.date = new_date
        self.message = message
        self.channel = channel
        self.image = image
        self.callback = callback
        # Start
        if not self.task.is_running():
            self.task.start()
        else:
            self.task.restart()
        
    def force_reset(self):
        self.task.cancel()
        self.date = None
        self.callback()
    
    @tasks.loop(seconds=5)
    async def task(self):
        # For debugging only
        print(self.date - datetime.now())
        if datetime.now() >= self.date:
            print('Reminder done')
            if self.image == None:
                await self.channel.send(f'{self.message}', allowed_mentions=discord.AllowedMentions(everyone=True))
            else:
                await self.channel.send(f'{self.message}', allowed_mentions=discord.AllowedMentions(everyone=True), embed=self.image)
            self.task.cancel()
            # Resetting
            self.date = None
            self.callback()