#### ISSUES ####
# Event deletion
#   - If done push to done events database
#       - Help also less time finding closest
#   - Might delete the running, need to check
#   
# Max 2000 words for listing
# Delete only deletes from the database, if currently running, then not deleted

#### Changelog ####
# Remove the required ping input since you can ping more conveniently in the message input
# Added list and list_all
# Restricted the User that can use the bot with a hardcoded Role

import discord
from reminder import Reminder
from datetime import MAXYEAR, MINYEAR, datetime, timedelta
import database
import os
from dotenv import load_dotenv

load_dotenv()
# Discord token goes here
TOKEN = os.getenv('DISCORD_TOKEN')
PERMITTED_ROLE_ID = int(os.getenv('PERMITTED_ROLE_ID'))


class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reminder = Reminder()
        self.synced = False

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync()
            self.synced = True
        print(f'Logged in as {self.user}.')
        
        # Creating the database if not yet exist
        if not database.db_is_table_exist():
            database.db_create_tables()

        # Fetch the reminders
        fetch_closest_and_start_reminder()


# The callback
# Do not use callback, instead embed to the reminder
def fetch_closest_and_start_reminder():
    reminder = database.db_get_valid_closest_reminder()
    if reminder is None:
        return
    reminder_guild: discord.Guild = client.get_guild(reminder.guildId)
    reminder_channel = reminder_guild.get_channel(reminder.channelId)
    client.reminder.set_and_start(reminder.title, reminder.date, reminder.message, reminder_channel, fetch_closest_and_start_reminder)



intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)
tree = discord.app_commands.CommandTree(client)



#### Commands ####
@tree.command(name = 'add', description = 'Add a reminder')
@discord.app_commands.describe(
    title = 'Title of the event (should be unique)',
    day = 'What day to remind (1-31)',
    month = 'What month to remind (1-12)',
    year = 'What year to remind',
    hour = 'What hour to remind (0-23)',
    minute = 'What minute to remind (0-59)',
    message = 'Message content',
    channel = 'Channel to send the message',
)
async def add_reminder(
    interaction: discord.Interaction,
    title: str,
    day: int,
    month: int,
    year: int,
    hour: int,
    minute:int,
    message:str,
    channel: discord.TextChannel,
):
    # Role Validation
    valid_role = interaction.guild.get_role(PERMITTED_ROLE_ID)
    if valid_role not in interaction.user.roles:
        await interaction.response.send_message(f'You are not a valid user to use this bot')
        return

    # Input Validation
    if day < 1 or day > 31: 
        await interaction.response.send_message(f'Invalid day {day}')
        return
    if month < 1 or month > 31:
        await interaction.response.send_message(f'Invalid month {month}')
        return
    if year < MINYEAR or year > MAXYEAR:
        await interaction.response.send_message(f'Invalid year {year}')
        return
    if hour < 0 or hour > 23:
        await interaction.response.send_message(f'Invalid hour {hour}')
        return
    if minute < 0 or minute > 59:
        await interaction.response.send_message(f'Invalid minute {minute}')
        return
    
    date = datetime(year, month, day, hour, minute)
    database.db_add_reminder(title, date, message, interaction.guild.id, channel.id)
    client.reminder.set_and_start(title, date, message, channel, fetch_closest_and_start_reminder)
    
    await interaction.response.send_message(f'{title} added')



@tree.command(name = 'add_from_today', description = 'Add a reminder specifying how many days from today.')
@discord.app_commands.describe(
    title = 'Title of the event (should be unique)',
    days_from_today = 'Days from today to execute the reminder',
    hour = 'What hour to remind (0-23)',
    minute = 'What minute to remind (0-59)',
    message = 'Message content',
    channel = 'Channel to send the message',
)
async def add_reminder_from_today(
    interaction: discord.Interaction,
    title: str,
    days_from_today: int,
    hour: int,
    minute:int,
    message:str,
    channel: discord.TextChannel,
):
    # Role Validation
    valid_role = interaction.guild.get_role(PERMITTED_ROLE_ID)
    if valid_role not in interaction.user.roles:
        await interaction.response.send_message(f'You are not a valid user to use this bot')
        return

    # Input Validation
    if days_from_today < 0: 
        await interaction.response.send_message(f'Invalid day {days_from_today}')
        return
    if hour < 0 or hour > 23:
        await interaction.response.send_message(f'Invalid hour {hour}')
        return
    if minute < 0 or minute > 59:
        await interaction.response.send_message(f'Invalid minute {minute}')
        return
    
    date = datetime.now() + timedelta(days=days_from_today)
    date = date.replace(hour=hour, minute=minute)

    db_resp = database.db_add_reminder(title, date, message, interaction.guild.id, channel.id)
    if db_resp:
        client.reminder.set_and_start(title, date, message, channel, fetch_closest_and_start_reminder)
        await interaction.response.send_message(f'{title} added')
    else:
        await interaction.response.send_message(f'Title "{title}" is duplicated. Choose a unique title.')



@tree.command(name = 'delete', description = 'Delete a reminder.')
@discord.app_commands.describe(
    title = 'Title of the event to delete',
)
async def delete_reminder(
    interaction: discord.Interaction,
    title: str,
):
    # Role Validation
    valid_role = interaction.guild.get_role(PERMITTED_ROLE_ID)
    if valid_role not in interaction.user.roles:
        await interaction.response.send_message(f'You are not a valid user to use this bot')
        return

    db_resp = database.db_delete_by_title(title)
    if db_resp:
        await interaction.response.send_message(f'{title} deleted')
    else:
        await interaction.response.send_message(f'No title "{title}" exist')

    # If the reminder being deleted is not the currently running
    if title != client.reminder.title:
        return
    fetch_closest_and_start_reminder()

    

@tree.command(name = 'list', description = 'List the valid reminders',)
async def list_reminders(interaction: discord.Interaction):
    # Role Validation
    valid_role = interaction.guild.get_role(PERMITTED_ROLE_ID)
    if valid_role not in interaction.user.roles:
        await interaction.response.send_message(f'You are not a valid user to use this bot')
        return

    reminders = database.db_get_reminders(is_valid=True)
    if reminders == []:
        await interaction.response.send_message('No reminders exist')
        return
    reminders = list(map(lambda reminder: 
        f'Event "{reminder.title}" at {reminder.date.strftime("%d %b %Y %H:%M")} with message "{reminder.message}"',
        reminders
    ))
    reminders_str = '\n'.join(reminders)
    # 2000 Length Character
    await interaction.response.send_message(reminders_str)
    


@tree.command(name = 'list_all', description = 'List all the reminders',)
async def list_all_reminders(interaction: discord.Interaction):
    # Role Validation
    valid_role = interaction.guild.get_role(PERMITTED_ROLE_ID)
    if valid_role not in interaction.user.roles:
        await interaction.response.send_message(f'You are not a valid user to use this bot')
        return

    reminders = database.db_get_reminders()
    if reminders == []:
        await interaction.response.send_message('No reminders exist')
        return
    reminders = list(map(lambda reminder: 
        f'Event "{reminder.title}" at {reminder.date.strftime("%d %b %Y %H:%M")} with message "{reminder.message}"',
        reminders
    ))
    reminders_str = '\n'.join(reminders)
    # 2000 Length Character
    await interaction.response.send_message(reminders_str, allowed_mentions=discord.AllowedMentions.none())



@tree.command(name = 'help', description = 'List all the commands',)
async def help(interaction: discord.Interaction):
    await interaction.response.send_message(
        '''
Greetings milord! I am James the Jame Gammer, your humble servant. Your wish is my command.

Commands :
1. /add - adds a new reminder with the given date and message
2. /add_from_today - adds a new reminder with a date set x days from today. x = 0 means today.
3. /list_all - display all reminders
4. /list - display only valid reminders, that is, reminders that are not yet done (> current date)
5. /delete - delete a reminder with given name
6. /help - show all the commands.
        '''
    )

client.run(TOKEN)
