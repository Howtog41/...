from pyrogram import Client, filters

from config import Config
from helper.Database import db
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

admin_ids = Config.ADMIN_ID
USERS_COLLECTION = Config.USERS_COLLECTION
# Command to set the channel (triggers on /setchannel command)

@Client.on_message(filters.command("setchannel"))

async def set_channel(client, message):

    try:

        channel_id = message.command[1]  # Get the channel ID from the command arguments

        channels = await db.add_channel(message.from_user.id, channel_id)

        await message.reply_text(f"Channel ID {channel_id} has been added.")

        # Call the channels function automatically after setting the channel

        await channels(client, message)  # Calling the channels function

    except IndexError:

        await message.reply_text("Usage: /setchannel <channel_id>")

# Function to list and manage channels
@Client.on_message(filters.command("channel"))
async def channels(client, message):
    print("Received /channel command")

    # Fetch the user's channels from the database
    channels = await db.get_channels(message.from_user.id)


    if not channels:

        await message.reply_text("No channels are set. Use /setchannel <channel_id> to add a new channel.")

        return

    # Create inline buttons for channel management

    keyboard = [

        [InlineKeyboardButton(channel, callback_data=f"remove_{channel}") for channel in channels],

        [InlineKeyboardButton("Add new channel", callback_data="add_channel")]

    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await message.reply_text("Manage your channels:", reply_markup=reply_markup)

# Callback handler for managing channel buttons

@Client.on_callback_query(filters.regex(r"^remove_|add_channel$"))

@Client.on_message(filters.command("channelmanagement"))
async def channel_management_callback(client, callback_query):

    data = callback_query.data

    if data == "add_channel":

        await callback_query.edit_message_text(text="Please use /setchannel <channel_id> to add a new channel.")

    elif data.startswith("remove_"):

        channel_id = data.split("_", 1)[1]

        channels = await db.remove_channel(message.from_user.id)

        await callback_query.edit_message_text(text=f"Channel {channel_id} has been removed.")