import sqlite3
from datetime import datetime


class ReminderPackage:
    def __init__(self, title: str, date: datetime, message: str, guildId:int, channelId: int, pingId: int) -> None:
        self.title = title
        self.date = date
        self.message = message
        self.guildId = guildId
        self.channelId = channelId
        self.pingId = pingId


def db_create_tables():
    conn = sqlite3.connect("data.db", detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    c = conn.cursor()
    c.execute(
    """
    CREATE TABLE Reminder (
        Id          INTEGER     PRIMARY KEY,
        Title       TEXT        NOT NULL,
        Date        TIMESTAMP   NOT NULL,
        Message     TEXT        NOT NULL,
        GuildId     INTEGER     NOT NULL,
        ChannelId   INTEGER     NOT NULL,
        PingId      INTEGER     NOT NULL
    )
    """
    )
    conn.commit()
    conn.close()


def db_add_reminder(title: str, date: datetime, message: str, guildId:int, channelId: int, pingId: int):
    conn = sqlite3.connect("data.db", detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    c = conn.cursor()
    c.execute(f'SELECT Title FROM Reminder')
    # Ensuring that title is unique
    reminder_titles = c.fetchall()
    for reminder_title in reminder_titles:
        if reminder_title[0] == title:
            return False
    c.execute("INSERT INTO Reminder VALUES (NULL,?,?,?,?,?,?)", (title, date, message, guildId, channelId, pingId))
    conn.commit()
    conn.close()
    return True


def db_get_reminders() -> list:
    conn = sqlite3.connect("data.db", detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    c = conn.cursor()
    c.execute(f'SELECT Title, Date, Message, GuildId, ChannelId, PingId FROM Reminder')
    reminders = c.fetchall()
    if reminders == []:
        return []
    reminders = list(map(lambda reminder: ReminderPackage(reminder[0], reminder[1], reminder[2], reminder[3], reminder[4], reminder[5]), reminders))
    conn.commit()
    conn.close()
    return reminders


def db_get_valid_closest_reminder() -> ReminderPackage:
    conn = sqlite3.connect("data.db", detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    c = conn.cursor()
    current_date = datetime.now()
    c.execute(f'SELECT Title, Date, Message, GuildId, ChannelId, PingId FROM Reminder')
    reminders = c.fetchall()
    if reminders == []: return None
    # Get all reminders past the current date (valid)
    valid_reminders = list(filter(lambda reminder: reminder[1] > current_date, reminders))
    if valid_reminders == []: return None
    # Get the closest date out of the minimum
    reminder = min(valid_reminders, key=lambda reminder: reminder[1])
    conn.commit()
    conn.close()
    return ReminderPackage(reminder[0], reminder[1], reminder[2], reminder[3], reminder[4], reminder[5])


def db_delete_by_title(title: str):
    conn = sqlite3.connect("data.db", detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    c = conn.cursor()
    c.execute(f'SELECT Title FROM Reminder WHERE Title = "{title}"')
    reminder = c.fetchone()
    if reminder == None:
        return False
    c.execute(f'DELETE FROM Reminder WHERE Title = "{title}"')
    conn.commit()
    conn.close()
    return True

# For test only, will delete
def db_is_table_exist():
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Reminder'")
    tables = c.fetchall()
    if tables == []:
        return False
    return True
    conn.close()


# For test only, will delete
# def db_reset():
#     conn = sqlite3.connect("data.db")
#     c = conn.cursor()
#     c.execute("DROP TABLE Reminder")

