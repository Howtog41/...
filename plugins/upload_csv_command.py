from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from helper.Database import db  # Database for MongoDB operations
import csv
import os

@Client.on_message(filters.command("uploadcsv") & filters.user(Config.ADMIN_ID))
async def upload_csv_command(client, message):
    user_id = message.from_user.id

    # Fetch user information from the database
    user_info = await db.get_user(user_id)

    if user_info or user_id in Config.ADMIN_ID:
        # Prompt for CSV upload
        await message.reply_text(
            "📂 To upload your CSV file for MCQ conversion, please ensure it meets the following requirements: \n"
            "👉 Format: \"Question\", \"Option A\", \"Option B\", \"Option C\", \"Option D\", \"Answer\", \"Description\". \n"
            "👉 The \"Answer\" should be in A, B, C, D format. \n"
            "👉 The \"Description\" is optional. If not provided, it will be automatically filled.\n"
            "Example CSV format: [Download Example CSV](https://t.me/How_To_Google/10)"
        )
    else:
        # User is not authorized
        await message.reply_text("You are not authorized to use this bot. Please contact the admin.")


@Client.on_message(filters.document & filters.user(Config.ADMIN_ID))
async def handle_csv_file(client, message):
    user_id = message.from_user.id
    user_info = await db.get_user(user_id)

    if user_info or user_id in Config.ADMIN_ID:
        # Check if the uploaded file is a CSV
        if message.document.mime_type == "text/csv":
            file = await message.download()  # Download the CSV file to the server

            # Open the file and read the CSV content
            with open(file, 'r') as f:
                reader = csv.DictReader(f)
                questions = list(reader)

            # Store the questions in user data
            message.chat.user_data['questions'] = questions

            # Prompt user for destination (Bot or Channel)
            keyboard = [
                [InlineKeyboardButton("Bot", callback_data='bot')],
                [InlineKeyboardButton("Channel", callback_data='channel')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await message.reply_text(
                "Do you want to upload these quizzes to the bot or forward them to a channel?",
                reply_markup=reply_markup
            )

        else:
            await message.reply_text("Please upload a valid CSV file.")

    else:
        await message.reply_text("You are not authorized to use this bot. Please contact the admin.")

@Client.on_callback_query(filters.user(Config.ADMIN_ID))
async def choose_destination(client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    choice = callback_query.data

    if choice == 'bot':
        chat_id = callback_query.message.chat.id
        questions = callback_query.message.chat.user_data.get('questions', [])
        await send_all_polls(chat_id, client, questions)
        await callback_query.edit_message_text("Quizzes have been sent to the bot.")
        
    elif choice == 'channel':
        user_info = await db.get_user(user_id)
        if user_info and 'channels' in user_info and user_info['channels']:
            if len(user_info['channels']) == 1:
                # If the user has only one channel set
                channel_id = user_info['channels'][0]
                questions = callback_query.message.chat.user_data.get('questions', [])
                await send_all_polls(channel_id, client, questions)
                await callback_query.edit_message_text(f"Quizzes have been sent to {channel_id}.")
            else:
                # If the user has multiple channels set, ask them to choose one
                keyboard = [
                    [InlineKeyboardButton(channel, callback_data=channel) for channel in user_info['channels']]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await callback_query.edit_message_text("Choose a channel:", reply_markup=reply_markup)
        else:
            await callback_query.edit_message_text("No channels are set. Please set a channel using /setchannel <channel_id>.")
    else:
        await callback_query.edit_message_text("Invalid choice. Please select 'bot' or 'channel'.")
