from pyrogram import Client, filters

from datetime import datetime, timedelta

from config import Config  # Import your bot's configuration

from helper.Database import db  # Database for MongoDB operations

@Client.on_message(filters.command("authorize"))

async def authorize(client, message):

    user_id = message.from_user.id  # Get the admin's user ID

    if user_id in Config.ADMIN_ID:  # Check if the user is an admin

        try:

            # Extract the new user_id and optionally the number of days

            args = message.command

            new_user_id = int(args[1])  # e.g., /authorize <new_user_id> <days>

            days = int(args[2]) if len(args) > 2 else 30  # Default to 30 days if not specified

            # Set the expiration date by adding the number of days to the current date

            expiration_date = datetime.utcnow() + timedelta(days=days)

            # Authorize the user by updating the database with the expiration date

            await db.authorize_user(new_user_id, expiration_date)

            # Confirm the authorization

            await message.reply_text(f"User {new_user_id} has been authorized for {days} days.")

        except (IndexError, ValueError):

            # Handle missing or invalid arguments

            await message.reply_text("Usage: /authorize <user_id> <days> (e.g., /authorize 123456789 30)")

    else:

        await message.reply_text("You are not authorized to use this command.")
        
@Client.on_message(filters.command("unauthorize"))

async def unauthorize(client, message):

    user_id = message.from_user.id

    if user_id in Config.ADMIN_ID:  # Ensure only admins can unauthorize users

        try:

            # Extract the user_id to unauthorize

            new_user_id = int(message.command[1])  # e.g., /unauthorize <new_user_id>

            # Unauthorize the user by updating the database

            await db.unauthorize_user(new_user_id)

            # Confirm the unauthorization

            await message.reply_text(f"User {new_user_id} has been unauthorized and cannot use the bot.")

        except (IndexError, ValueError):

            # Handle missing or invalid arguments

            await message.reply_text("Usage: /unauthorize <user_id> (e.g., /unauthorize 123456789)")

    else:

        await message.reply_text("You are not authorized to use this command.")        