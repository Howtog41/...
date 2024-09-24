import csv

from pyrogram import Client, filters

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import Config  # Import your bot's configuration

from helper.Database import db  # Database for MongoDB operations

from plugins.poll_sender import send_all_polls  # Import the function from poll_sender.py

# Global dictionary to store user data temporarily and to track CSV upload state

user_data = {}

upload_state = {}  # To track if a user has initiated the /uploadcsv command

@Client.on_message(filters.command("uploadcsv"))

async def upload_csv_command(client, message):

    user_id = message.from_user.id

    user_info = await db.get_user(user_id)

    if user_id in Config.ADMIN_ID or user_info:

        await message.reply_text(

            "📂 To upload your CSV file for MCQ conversion, please ensure it meets the following requirements: \n"

            "👉 Format: \"Question\", \"Option A\", \"Option B\", \"Option C\", \"Option D\", \"Answer\", \"Description\". \n"

            "👉 The \"Answer\" should be in A, B, C, D format. \n"

            "👉 The \"Description\" is optional. If not provided, it will be automatically filled.\n"

            "Example CSV format: [Download Example CSV](https://t.me/How_To_Google/10)"

        )

        # Mark that the user has initiated the CSV upload process

        upload_state[user_id] = True

    else:

        await message.reply_text("You are not authorized to use this bot. Please contact the admin.")

@Client.on_message(filters.document)

async def handle_csv_file(client, message):

    user_id = message.from_user.id

    user_info = await db.get_user(user_id)

    # Check if the user initiated the CSV upload process with /uploadcsv

    if upload_state.get(user_id):

        if user_id in Config.ADMIN_ID or user_info:

            if message.document.mime_type == "text/csv":

                file = await message.download()  # Download the CSV file to the server

                with open(file, 'r') as f:

                    reader = csv.DictReader(f)

                    questions = list(reader)

                user_data[user_id] = {'questions': questions}

                keyboard = [

                    [InlineKeyboardButton("Bot", callback_data='bot')],

                    [InlineKeyboardButton("Channel", callback_data='channel')]

                ]

                reply_markup = InlineKeyboardMarkup(keyboard)

                await message.reply_text(

                    "Do you want to upload these quizzes to the bot or forward them to a channel?",

                    reply_markup=reply_markup

                )

                # Clear the upload state after processing

                upload_state.pop(user_id, None)

            else:

                await message.reply_text("Please upload a valid CSV file.")

        else:

            await message.reply_text("You are not authorized to use this bot. Please contact the admin.")

    else:

        await message.reply_text("Please use /uploadcsv command before sending the CSV file.")


@Client.on_callback_query()
async def choose_destination(client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    choice = callback_query.data  # Choice will be either 'bot' or 'channel'

    # Fetch the questions stored in memory for this user
    questions = user_data.get(user_id, {}).get('questions', [])

    if not questions:
        await callback_query.edit_message_text("No quiz data found. Please upload the CSV file again.")
        return

    if choice == 'bot' or choice == 'channel':
        # Ask for a custom description
        await callback_query.message.reply_text("Please provide a custom description to append to the quizzes (or send 'None' for no description):")
        user_data[user_id]['destination'] = choice  # Store destination (bot/channel)
    else:
        await callback_query.edit_message_text("Invalid choice. Please select 'bot' or 'channel'.")


# Handle the description response
@Client.on_message(filters.text)
async def handle_description(client, message):
    user_id = message.from_user.id

    # Check if the user is in the middle of uploading CSV
    if user_id in user_data and 'destination' in user_data[user_id]:
        custom_description = message.text.strip()

        # Check if the user said 'None' (no custom description)
        if custom_description.lower() == 'none':
            custom_description = None

        # Determine destination
        destination = user_data[user_id]['destination']
        questions = user_data[user_id].get('questions', [])

        if destination == 'bot':
            chat_id = message.chat.id
            await send_all_polls(chat_id, client, questions, custom_description)
            await message.reply_text("Quizzes have been sent to the bot.")
        elif destination == 'channel':
            user_info = await db.get_user(user_id)
            if user_info and 'channels' in user_info and user_info['channels']:
                if len(user_info['channels']) == 1:
                    channel_id = user_info['channels'][0]
                    await send_all_polls(channel_id, client, questions, custom_description)
                    await message.reply_text(f"Quizzes have been sent to {channel_id}.")
                else:
                    # Ask user to select a channel if they have multiple channels
                    keyboard = [
                        [InlineKeyboardButton(channel, callback_data=channel) for channel in user_info['channels']]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await message.reply_text("Choose a channel:", reply_markup=reply_markup)

        # Clear user data after sending
        user_data.pop(user_id, None)