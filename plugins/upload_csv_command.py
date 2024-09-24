from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from helper.Database import db  # Database for MongoDB operations
from config import Config
import csv
import os

# In-memory storage for user data (temporary)
user_data = {}

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
            user_data[user_id] = {'questions': questions}

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
        questions = user_data.get(user_id, {}).get('questions', [])
        await send_all_polls(chat_id, client, questions)
        await callback_query.edit_message_text("Quizzes have been sent to the bot.")

    elif choice == 'channel':
        user_info = await db.get_user(user_id)
        if user_info and 'channels' in user_info and user_info['channels']:
            if len(user_info['channels']) == 1:
                # If the user has only one channel set
                channel_id = user_info['channels'][0]
                questions = user_data.get(user_id, {}).get('questions', [])
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


# Function to send all polls from the CSV file
async def send_all_polls(chat_id, client: Client, questions):
    answer_mapping = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
    max_question_length = 255
    max_option_length = 100
    max_description_length = 200

    for question in questions:
        try:
            text = question.get('Question')
            options = [
                question.get('Option A', ''), 
                question.get('Option B', ''), 
                question.get('Option C', ''), 
                question.get('Option D', '')
            ]
            correct_option = question.get('Answer')
            correct_option_id = answer_mapping.get(correct_option.upper(), None) if correct_option else None
            description = question.get('Description', '')

            # Check for missing data
            missing_data = False
            missing_elements = []

            if not text:
                missing_elements.append("Question")
                missing_data = True

            for index, option in enumerate(options):
                if option == '':
                    missing_elements.append(f"Option {chr(65 + index)}")
                    missing_data = True

            if correct_option is None:
                missing_elements.append("Answer")
                missing_data = True

            if missing_data:
                # Prepare a message showing the MCQ and indicating the missing data
                message_text = f"Question: {text if text else '[Missing]'}\n\n"
                message_text += f"Option A: {options[0] if options[0] else '[Missing]'}\n"
                message_text += f"Option B: {options[1] if options[1] else '[Missing]'}\n"
                message_text += f"Option C: {options[2] if options[2] else '[Missing]'}\n"
                message_text += f"Option D: {options[3] if options[3] else '[Missing]'}\n"
                message_text += f"Answer: {correct_option if correct_option else '[Missing]'}\n"
                message_text += "\nAapne jo MCQ bheja hai usme option ya Answer missing hai. Kripya use sudhar kr punh bheje."
                
                await client.send_message(chat_id=chat_id, text=message_text)
                continue

            # Ensure description contains "@SecondCoaching"
            if '@SecondCoaching' not in description:
                description += ' @SecondCoaching'

            if (len(text) <= max_question_length and 
                all(len(option) <= max_option_length for option in options) and 
                len(description) <= max_description_length):

                # Send the poll
                await client.send_poll(
                    chat_id=chat_id,
                    question=text,
                    options=options,
                    type='quiz',  # Use 'quiz' for quiz-type polls
                    correct_option_id=correct_option_id,
                    explanation=description,
                    is_anonymous=True  # Set to True to make the quiz anonymous
                )
            else:
                # Send the question and options as a text message
                message_text = f"Question: {text}\n\n"
                message_text += f"Option A: {options[0]}\n"
                message_text += f"Option B: {options[1]}\n"
                message_text += f"Option C: {options[2]}\n"
                message_text += f"Option D: {options[3]}\n"
                if description:
                    message_text += f"\nDescription: {description}"

                await client.send_message(chat_id=chat_id, text=message_text)

                # Send a follow-up quiz
                follow_up_question = "Upr diye gye Question ka Answer kya hoga?👆👆👆👆👆👆👆👆👆"
                follow_up_options = ['A', 'B', 'C', 'D']

                await client.send_poll(
                    chat_id=chat_id,
                    question=follow_up_question,
                    options=follow_up_options,
                    type='quiz',
                    correct_option_id=correct_option_id,
                    is_anonymous=True
                )
        except Exception as e:
            error_message = "Aapne jo CSV file upload ki hai usme kuch gadbadi hai. Kripya use shi karke punh upload kre."
            await client.send_message(chat_id=chat_id, text=error_message)
            continue
